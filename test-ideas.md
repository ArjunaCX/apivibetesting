# TechShop API — Test Ideas

Derived from swagger.json (OpenAPI 3.0.0).

## POST /auth/login
- Happy path: valid email and password (demo@techshop.com / password123) → 200 with token and user
- Negative: wrong password → 401
- Negative: missing email field → 400
- Auth: none required

## GET /products
- Happy path: returns 200 with array of products
- Negative: invalid category filter → 200 with empty array
- Auth: none required

## GET /products/{id}
- Happy path: valid ID → 200 with product object
- Negative: non-existent ID (e.g. 999) → 404
- Auth: none required

## GET /cart
- Happy path: valid token → 200 with cart object (items + total)
- Negative: no token → 401
- Auth: Bearer token required

## POST /cart
- Happy path: valid token + productId + quantity → 201
- Negative: quantity less than 1 → 400
- Negative: no token → 401
- Negative: non-existent productId → 404
- Auth: Bearer token required

## PUT /cart/{itemId}
- Happy path: valid token + valid itemId + quantity → 200
- Negative: quantity less than 1 → 400
- Negative: non-existent itemId → 404
- Negative: no token → 401
- Auth: Bearer token required

## DELETE /cart/{itemId}
- Happy path: valid token + valid itemId → 200
- Negative: no token → 401
- Negative: non-existent itemId → 404
- Auth: Bearer token required

## GET /orders
- Happy path: valid token → 200 with array of orders
- Negative: no token → 401
- Auth: Bearer token required

## POST /orders
- Happy path: valid token + items + shipping + payment → 201
- Negative: expired card expiry date → 400
- Negative: invalid card number (not 16 digits) → 400
- Negative: missing shipping fields → 400
- Negative: no token → 401
- Auth: Bearer token required
