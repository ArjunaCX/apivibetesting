"""TechShop API tests — derived from swagger.json + test-ideas.md."""

import os

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")


@pytest.fixture
def auth_token():
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")
    if not email or not password:
        raise ValueError(
            "TEST_EMAIL and TEST_PASSWORD must be set as environment variables"
        )
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password},
        timeout=10,
    )
    assert response.status_code == 200, (
        f"Login failed with {response.status_code}: {response.text}"
    )
    token = response.json().get("token")
    assert token, "Login response did not include a token"
    return token


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


# ── Auth ─────────────────────────────────────────────────────────────────────


def test_login_valid_credentials():
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")
    if not email or not password:
        raise ValueError(
            "TEST_EMAIL and TEST_PASSWORD must be set as environment variables"
        )
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password},
        timeout=10,
    )
    assert response.status_code == 200
    body = response.json()
    assert "token" in body
    assert "user" in body


def test_login_wrong_password_returns_401():
    email = os.getenv("TEST_EMAIL")
    if not email:
        raise ValueError("TEST_EMAIL must be set as an environment variable")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": "wrongpassword"},
        timeout=10,
    )
    assert response.status_code == 401


def test_login_missing_email_returns_400():
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"password": "password123"},
        timeout=10,
    )
    assert response.status_code == 400


def test_login_missing_password_returns_400():
    email = os.getenv("TEST_EMAIL")
    if not email:
        raise ValueError("TEST_EMAIL must be set as an environment variable")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email},
        timeout=10,
    )
    assert response.status_code == 400


# ── Products ─────────────────────────────────────────────────────────────────


def test_get_products_returns_200():
    response = requests.get(f"{BASE_URL}/products", timeout=10)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_products_invalid_category_returns_empty_array():
    response = requests.get(
        f"{BASE_URL}/products",
        params={"category": "invalid-category"},
        timeout=10,
    )
    assert response.status_code == 200
    assert response.json() == []


def test_get_product_by_id_returns_200():
    response = requests.get(f"{BASE_URL}/products/1", timeout=10)
    assert response.status_code == 200
    assert "id" in response.json()


def test_get_product_not_found_returns_404():
    response = requests.get(f"{BASE_URL}/products/999", timeout=10)
    assert response.status_code == 404


# ── Cart ─────────────────────────────────────────────────────────────────────


def test_get_cart_returns_200(auth_headers):
    response = requests.get(f"{BASE_URL}/cart", headers=auth_headers, timeout=10)
    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert "total" in body


def test_get_cart_no_token_returns_401():
    response = requests.get(f"{BASE_URL}/cart", timeout=10)
    assert response.status_code == 401


def test_add_to_cart_returns_201(auth_headers):
    response = requests.post(
        f"{BASE_URL}/cart",
        headers=auth_headers,
        json={"productId": 1, "quantity": 2},
        timeout=10,
    )
    assert response.status_code == 201


@pytest.mark.parametrize("quantity", [0, -1, -100])
def test_add_to_cart_invalid_quantity_returns_400(auth_headers, quantity):
    """swagger: POST /cart quantity minimum: 1"""
    response = requests.post(
        f"{BASE_URL}/cart",
        headers=auth_headers,
        json={"productId": 1, "quantity": quantity},
        timeout=10,
    )
    assert response.status_code == 400


def test_add_to_cart_missing_required_fields_returns_400(auth_headers):
    response = requests.post(
        f"{BASE_URL}/cart",
        headers=auth_headers,
        json={},
        timeout=10,
    )
    assert response.status_code == 400


def test_add_to_cart_no_token_returns_401():
    response = requests.post(
        f"{BASE_URL}/cart",
        json={"productId": 1, "quantity": 1},
        timeout=10,
    )
    assert response.status_code == 401


def test_add_to_cart_product_not_found_returns_404(auth_headers):
    response = requests.post(
        f"{BASE_URL}/cart",
        headers=auth_headers,
        json={"productId": 99999, "quantity": 1},
        timeout=10,
    )
    assert response.status_code == 404


def test_update_cart_item_returns_200(auth_headers):
    add = requests.post(
        f"{BASE_URL}/cart",
        headers=auth_headers,
        json={"productId": 1, "quantity": 1},
        timeout=10,
    )
    assert add.status_code == 201
    body = add.json()
    item_id = body["items"][-1]["id"] if body.get("items") else body.get("id")
    response = requests.put(
        f"{BASE_URL}/cart/{item_id}",
        headers=auth_headers,
        json={"quantity": 3},
        timeout=10,
    )
    assert response.status_code == 200


@pytest.mark.parametrize("quantity", [0, -1, -100])
def test_update_cart_item_invalid_quantity_returns_400(auth_headers, quantity):
    """swagger: PUT /cart/{itemId} quantity minimum: 1"""
    add = requests.post(
        f"{BASE_URL}/cart",
        headers=auth_headers,
        json={"productId": 1, "quantity": 1},
        timeout=10,
    )
    assert add.status_code == 201
    body = add.json()
    item_id = body["items"][-1]["id"] if body.get("items") else body.get("id")
    response = requests.put(
        f"{BASE_URL}/cart/{item_id}",
        headers=auth_headers,
        json={"quantity": quantity},
        timeout=10,
    )
    assert response.status_code == 400


def test_update_cart_item_not_found_returns_404(auth_headers):
    response = requests.put(
        f"{BASE_URL}/cart/99999",
        headers=auth_headers,
        json={"quantity": 2},
        timeout=10,
    )
    assert response.status_code == 404


def test_update_cart_item_no_token_returns_401():
    response = requests.put(
        f"{BASE_URL}/cart/1",
        json={"quantity": 2},
        timeout=10,
    )
    assert response.status_code == 401


def test_delete_cart_item_returns_200(auth_headers):
    add = requests.post(
        f"{BASE_URL}/cart",
        headers=auth_headers,
        json={"productId": 1, "quantity": 1},
        timeout=10,
    )
    assert add.status_code == 201
    body = add.json()
    item_id = body["items"][-1]["id"] if body.get("items") else body.get("id")
    response = requests.delete(
        f"{BASE_URL}/cart/{item_id}",
        headers=auth_headers,
        timeout=10,
    )
    assert response.status_code == 200


def test_delete_cart_item_no_token_returns_401():
    response = requests.delete(f"{BASE_URL}/cart/1", timeout=10)
    assert response.status_code == 401


def test_delete_cart_item_not_found_returns_404(auth_headers):
    response = requests.delete(
        f"{BASE_URL}/cart/99999",
        headers=auth_headers,
        timeout=10,
    )
    assert response.status_code == 404


# ── Orders ───────────────────────────────────────────────────────────────────


def test_get_orders_returns_200(auth_headers):
    response = requests.get(f"{BASE_URL}/orders", headers=auth_headers, timeout=10)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_orders_no_token_returns_401():
    response = requests.get(f"{BASE_URL}/orders", timeout=10)
    assert response.status_code == 401


def test_create_order_returns_201(auth_headers):
    response = requests.post(
        f"{BASE_URL}/orders",
        headers=auth_headers,
        json={
            "items": [{"productId": 1, "quantity": 1}],
            "shipping": {
                "firstName": "Jane",
                "lastName": "Doe",
                "email": "jane@example.com",
                "phone": "0412345678",
            },
            "payment": {
                "cardNumber": "4111111111111111",
                "expiryDate": "12/28",
                "cvv": "123",
            },
        },
        timeout=10,
    )
    assert response.status_code == 201


@pytest.mark.parametrize("quantity", [0, -1, -100])
def test_create_order_invalid_item_quantity_returns_400(auth_headers, quantity):
    """swagger: POST /orders items[].quantity minimum: 1"""
    response = requests.post(
        f"{BASE_URL}/orders",
        headers=auth_headers,
        json={
            "items": [{"productId": 1, "quantity": quantity}],
            "shipping": {
                "firstName": "Jane",
                "lastName": "Doe",
                "email": "jane@example.com",
                "phone": "0412345678",
            },
            "payment": {
                "cardNumber": "4111111111111111",
                "expiryDate": "12/28",
                "cvv": "123",
            },
        },
        timeout=10,
    )
    assert response.status_code == 400


def test_create_order_expired_card_returns_400(auth_headers):
    response = requests.post(
        f"{BASE_URL}/orders",
        headers=auth_headers,
        json={
            "items": [{"productId": 1, "quantity": 1}],
            "shipping": {
                "firstName": "Jane",
                "lastName": "Doe",
                "email": "jane@example.com",
                "phone": "0412345678",
            },
            "payment": {
                "cardNumber": "4111111111111111",
                "expiryDate": "01/20",
                "cvv": "123",
            },
        },
        timeout=10,
    )
    assert response.status_code == 400


def test_create_order_invalid_card_returns_400(auth_headers):
    response = requests.post(
        f"{BASE_URL}/orders",
        headers=auth_headers,
        json={
            "items": [{"productId": 1, "quantity": 1}],
            "shipping": {
                "firstName": "Jane",
                "lastName": "Doe",
                "email": "jane@example.com",
                "phone": "0412345678",
            },
            "payment": {
                "cardNumber": "4111",
                "expiryDate": "12/28",
                "cvv": "123",
            },
        },
        timeout=10,
    )
    assert response.status_code == 400


def test_create_order_missing_shipping_returns_400(auth_headers):
    response = requests.post(
        f"{BASE_URL}/orders",
        headers=auth_headers,
        json={
            "items": [{"productId": 1, "quantity": 1}],
            "shipping": {"firstName": "Jane"},
            "payment": {
                "cardNumber": "4111111111111111",
                "expiryDate": "12/28",
                "cvv": "123",
            },
        },
        timeout=10,
    )
    assert response.status_code == 400


def test_create_order_empty_items_returns_400(auth_headers):
    response = requests.post(
        f"{BASE_URL}/orders",
        headers=auth_headers,
        json={
            "items": [],
            "shipping": {
                "firstName": "Jane",
                "lastName": "Doe",
                "email": "jane@example.com",
                "phone": "0412345678",
            },
            "payment": {
                "cardNumber": "4111111111111111",
                "expiryDate": "12/28",
                "cvv": "123",
            },
        },
        timeout=10,
    )
    assert response.status_code == 400


def test_create_order_missing_payment_returns_400(auth_headers):
    response = requests.post(
        f"{BASE_URL}/orders",
        headers=auth_headers,
        json={
            "items": [{"productId": 1, "quantity": 1}],
            "shipping": {
                "firstName": "Jane",
                "lastName": "Doe",
                "email": "jane@example.com",
                "phone": "0412345678",
            },
            "payment": {},
        },
        timeout=10,
    )
    assert response.status_code == 400


def test_create_order_no_token_returns_401():
    response = requests.post(
        f"{BASE_URL}/orders",
        json={
            "items": [{"productId": 1, "quantity": 1}],
            "shipping": {
                "firstName": "Jane",
                "lastName": "Doe",
                "email": "jane@example.com",
                "phone": "0412345678",
            },
            "payment": {
                "cardNumber": "4111111111111111",
                "expiryDate": "12/28",
                "cvv": "123",
            },
        },
        timeout=10,
    )
    assert response.status_code == 401
