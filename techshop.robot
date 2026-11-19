*** Settings ***
Library           RequestsLibrary
Library           Collections
Library           OperatingSystem
Suite Setup       Create TechShop Session
Suite Teardown    Delete All Sessions

*** Variables ***
${BASE_URL}       %{BASE_URL}
${EMAIL}          %{TEST_EMAIL}
${PASSWORD}       %{TEST_PASSWORD}

*** Keywords ***
Create TechShop Session
    Create Session    techshop    ${BASE_URL}    disable_warnings=True

Get Auth Token
    ${body}=    Create Dictionary    email=${EMAIL}    password=${PASSWORD}
    ${response}=    POST On Session    techshop    /auth/login    json=${body}    expected_status=200
    ${json}=    Set Variable    ${response.json()}
    ${token}=    Get From Dictionary    ${json}    token
    RETURN    ${token}

Auth Headers
    [Arguments]    ${token}
    ${headers}=    Create Dictionary    Authorization=Bearer ${token}
    RETURN    ${headers}

Valid Order Payload
    ${item}=    Create Dictionary    productId=${1}    quantity=${1}
    ${items}=    Create List    ${item}
    ${shipping}=    Create Dictionary
    ...    firstName=Jane
    ...    lastName=Doe
    ...    email=jane@example.com
    ...    phone=0412345678
    ${payment}=    Create Dictionary
    ...    cardNumber=4111111111111111
    ...    expiryDate=12/28
    ...    cvv=123
    ${payload}=    Create Dictionary    items=${items}    shipping=${shipping}    payment=${payment}
    RETURN    ${payload}

*** Test Cases ***
Login With Valid Credentials Returns Token
    ${body}=    Create Dictionary    email=${EMAIL}    password=${PASSWORD}
    ${response}=    POST On Session    techshop    /auth/login    json=${body}    expected_status=200
    ${json}=    Set Variable    ${response.json()}
    Dictionary Should Contain Key    ${json}    token
    Dictionary Should Contain Key    ${json}    user

Login With Wrong Password Returns 401
    ${body}=    Create Dictionary    email=${EMAIL}    password=wrongpassword
    ${response}=    POST On Session    techshop    /auth/login    json=${body}    expected_status=any
    Status Should Be    401    ${response}

Login With Missing Email Returns 400
    ${body}=    Create Dictionary    password=${PASSWORD}
    ${response}=    POST On Session    techshop    /auth/login    json=${body}    expected_status=any
    Status Should Be    400    ${response}

Login With Missing Password Returns 400
    ${body}=    Create Dictionary    email=${EMAIL}
    ${response}=    POST On Session    techshop    /auth/login    json=${body}    expected_status=any
    Status Should Be    400    ${response}

Get All Products Returns 200
    ${response}=    GET On Session    techshop    /products    expected_status=200
    ${products}=    Set Variable    ${response.json()}
    ${is_list}=    Evaluate    isinstance($products, list)
    Should Be True    ${is_list}

Get Products With Invalid Category Returns Empty Array
    ${params}=    Create Dictionary    category=invalid-category
    ${response}=    GET On Session    techshop    /products    params=${params}    expected_status=200
    ${products}=    Set Variable    ${response.json()}
    Should Be Empty    ${products}

Get Product By Id Returns 200
    ${response}=    GET On Session    techshop    /products/1    expected_status=200
    ${product}=    Set Variable    ${response.json()}
    Dictionary Should Contain Key    ${product}    id

Get Product With Unknown ID Returns 404
    ${response}=    GET On Session    techshop    /products/999    expected_status=any
    Status Should Be    404    ${response}

Get Cart Returns 200
    ${token}=    Get Auth Token
    ${headers}=    Auth Headers    ${token}
    ${response}=    GET On Session    techshop    /cart    headers=${headers}    expected_status=200
    ${cart}=    Set Variable    ${response.json()}
    Dictionary Should Contain Key    ${cart}    items
    Dictionary Should Contain Key    ${cart}    total

Get Cart Without Token Returns 401
    ${response}=    GET On Session    techshop    /cart    expected_status=any
    Status Should Be    401    ${response}

Add Item To Cart Returns 201
    ${token}=    Get Auth Token
    ${headers}=    Auth Headers    ${token}
    ${body}=    Create Dictionary    productId=${1}    quantity=${2}
    ${response}=    POST On Session    techshop    /cart    json=${body}    headers=${headers}    expected_status=201

Add To Cart With Invalid Quantity Returns 400
    ${token}=    Get Auth Token
    ${headers}=    Auth Headers    ${token}
    ${body}=    Create Dictionary    productId=${1}    quantity=${0}
    ${response}=    POST On Session    techshop    /cart    json=${body}    headers=${headers}    expected_status=any
    Status Should Be    400    ${response}

Add To Cart With Missing Required Fields Returns 400
    ${token}=    Get Auth Token
    ${headers}=    Auth Headers    ${token}
    ${body}=    Create Dictionary
    ${response}=    POST On Session    techshop    /cart    json=${body}    headers=${headers}    expected_status=any
    Status Should Be    400    ${response}

Add To Cart Without Token Returns 401
    ${body}=    Create Dictionary    productId=${1}    quantity=${1}
    ${response}=    POST On Session    techshop    /cart    json=${body}    expected_status=any
    Status Should Be    401    ${response}

Add Unknown Product To Cart Returns 404
    ${token}=    Get Auth Token
    ${headers}=    Auth Headers    ${token}
    ${body}=    Create Dictionary    productId=${99999}    quantity=${1}
    ${response}=    POST On Session    techshop    /cart    json=${body}    headers=${headers}    expected_status=any
    Status Should Be    404    ${response}

Update Cart Item Returns 200
    ${token}=    Get Auth Token
    ${headers}=    Auth Headers    ${token}
    ${add_body}=    Create Dictionary    productId=${1}    quantity=${1}
    ${add}=    POST On Session    techshop    /cart    json=${add_body}    headers=${headers}    expected_status=201
    ${cart}=    Set Variable    ${add.json()}
    ${items}=    Get From Dictionary    ${cart}    items
    ${item}=    Get From List    ${items}    -1
    ${item_id}=    Get From Dictionary    ${item}    id
    ${update_body}=    Create Dictionary    quantity=${3}
    ${response}=    PUT On Session    techshop    /cart/${item_id}    json=${update_body}    headers=${headers}    expected_status=200

Update Cart Item With Invalid Quantity Returns 400
    ${token}=    Get Auth Token
    ${headers}=    Auth Headers    ${token}
    ${add_body}=    Create Dictionary    productId=${1}    quantity=${1}
    ${add}=    POST On Session    techshop    /cart    json=${add_body}    headers=${headers}    expected_status=201
    ${cart}=    Set Variable    ${add.json()}
    ${items}=    Get From Dictionary    ${cart}    items
    ${item}=    Get From List    ${items}    -1
    ${item_id}=    Get From Dictionary    ${item}    id
    ${update_body}=    Create Dictionary    quantity=${0}
    ${response}=    PUT On Session    techshop    /cart/${item_id}    json=${update_body}    headers=${headers}    expected_status=any
    Status Should Be    400    ${response}

Update Unknown Cart Item Returns 404
    ${token}=    Get Auth Token
    ${headers}=    Auth Headers    ${token}
    ${body}=    Create Dictionary    quantity=${2}
    ${response}=    PUT On Session    techshop    /cart/99999    json=${body}    headers=${headers}    expected_status=any
    Status Should Be    404    ${response}

Update Cart Item Without Token Returns 401
    ${body}=    Create Dictionary    quantity=${2}
    ${response}=    PUT On Session    techshop    /cart/1    json=${body}    expected_status=any
    Status Should Be    401    ${response}

Delete Cart Item Returns 200
    ${token}=    Get Auth Token
    ${headers}=    Auth Headers    ${token}
    ${add_body}=    Create Dictionary    productId=${1}    quantity=${1}
    ${add}=    POST On Session    techshop    /cart    json=${add_body}    headers=${headers}    expected_status=201
    ${cart}=    Set Variable    ${add.json()}
    ${items}=    Get From Dictionary    ${cart}    items
    ${item}=    Get From List    ${items}    -1
    ${item_id}=    Get From Dictionary    ${item}    id
    ${response}=    DELETE On Session    techshop    /cart/${item_id}    headers=${headers}    expected_status=any
    Status Should Be    200    ${response}

Delete Cart Item Without Token Returns 401
    ${response}=    DELETE On Session    techshop    /cart/1    expected_status=any
    Status Should Be    401    ${response}

Delete Unknown Cart Item Returns 404
    ${token}=    Get Auth Token
    ${headers}=    Auth Headers    ${token}
    ${response}=    DELETE On Session    techshop    /cart/99999    headers=${headers}    expected_status=any
    Status Should Be    404    ${response}

Get Orders Returns 200
    ${token}=    Get Auth Token
    ${headers}=    Auth Headers    ${token}
    ${response}=    GET On Session    techshop    /orders    headers=${headers}    expected_status=200
    ${orders}=    Set Variable    ${response.json()}
    ${is_list}=    Evaluate    isinstance($orders, list)
    Should Be True    ${is_list}

Get Orders Without Token Returns 401
    ${response}=    GET On Session    techshop    /orders    expected_status=any
    Status Should Be    401    ${response}

Place Order Returns 201
    ${token}=    Get Auth Token
    ${headers}=    Auth Headers    ${token}
    ${payload}=    Valid Order Payload
    ${response}=    POST On Session    techshop    /orders    json=${payload}    headers=${headers}    expected_status=201

Place Order With Expired Card Returns 400
    ${token}=    Get Auth Token
    ${headers}=    Auth Headers    ${token}
    ${payload}=    Valid Order Payload
    ${payment}=    Create Dictionary    cardNumber=4111111111111111    expiryDate=01/20    cvv=123
    Set To Dictionary    ${payload}    payment=${payment}
    ${response}=    POST On Session    techshop    /orders    json=${payload}    headers=${headers}    expected_status=any
    Status Should Be    400    ${response}

Place Order With Invalid Card Number Returns 400
    ${token}=    Get Auth Token
    ${headers}=    Auth Headers    ${token}
    ${payload}=    Valid Order Payload
    ${payment}=    Create Dictionary    cardNumber=4111    expiryDate=12/28    cvv=123
    Set To Dictionary    ${payload}    payment=${payment}
    ${response}=    POST On Session    techshop    /orders    json=${payload}    headers=${headers}    expected_status=any
    Status Should Be    400    ${response}

Place Order With Missing Shipping Fields Returns 400
    ${token}=    Get Auth Token
    ${headers}=    Auth Headers    ${token}
    ${item}=    Create Dictionary    productId=${1}    quantity=${1}
    ${items}=    Create List    ${item}
    ${shipping}=    Create Dictionary    firstName=Jane
    ${payment}=    Create Dictionary    cardNumber=4111111111111111    expiryDate=12/28    cvv=123
    ${payload}=    Create Dictionary    items=${items}    shipping=${shipping}    payment=${payment}
    ${response}=    POST On Session    techshop    /orders    json=${payload}    headers=${headers}    expected_status=any
    Status Should Be    400    ${response}

Place Order With Empty Items Returns 400
    ${token}=    Get Auth Token
    ${headers}=    Auth Headers    ${token}
    ${payload}=    Valid Order Payload
    ${empty}=    Create List
    Set To Dictionary    ${payload}    items=${empty}
    ${response}=    POST On Session    techshop    /orders    json=${payload}    headers=${headers}    expected_status=any
    Status Should Be    400    ${response}

Place Order With Missing Payment Returns 400
    ${token}=    Get Auth Token
    ${headers}=    Auth Headers    ${token}
    ${payload}=    Valid Order Payload
    ${empty_payment}=    Create Dictionary
    Set To Dictionary    ${payload}    payment=${empty_payment}
    ${response}=    POST On Session    techshop    /orders    json=${payload}    headers=${headers}    expected_status=any
    Status Should Be    400    ${response}

Place Order Without Token Returns 401
    ${payload}=    Valid Order Payload
    ${response}=    POST On Session    techshop    /orders    json=${payload}    expected_status=any
    Status Should Be    401    ${response}
