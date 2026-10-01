# aws-coffee-shop-backend

# ☕ Coffee Shop API

A Django REST API for a coffee shop. Browse drinks, food and sides, manage a
per-user cart, and manage the menu through the Django admin.

Built as a group project for AWS deployment.

---

## Features

- Products (drinks, food, sides, merch) with optional sizes
- Categories for grouping products
- Dietary flags (vegetarian, vegan, gluten-free, contains nuts)
- Per-user cart (add / update / remove / clear)
- JWT authentication
- Django admin for managing the menu
- Image uploads for products

---

## Setup

git clone <repo-url>
cd coffee
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

API:   http://localhost:8000/api/
Admin: http://localhost:8000/admin/

admin login: username=admin & password=12345

---

## Endpoints

POST            /api/auth/registration/           Register a new user                -
POST            /api/auth/login/                  Get access + refresh tokens        -
POST            /api/auth/token/refresh/          Refresh access token               -
GET             /api/products/                    List / filter products             -
GET             /api/products/<id>/               Product detail                     -
POST/PUT/DELETE /api/products/...                 Manage products                    Admin
GET             /api/categories/                  List categories                    -
GET             /api/choices/                     Dropdown values for the frontend   -
GET             /api/cart/                        View your cart                     Yes
POST            /api/cart/add-item/               {"product_id": 1, "quantity": 2}   Yes
POST            /api/cart/update-item/<id>/       {"quantity": 5}                    Yes
DELETE          /api/cart/remove-item/<id>/       Remove one item                    Yes
DELETE          /api/cart/clear/                  Empty the cart                     Yes

Authenticated requests need:

    Authorization: Bearer <access_token>

Product filters (query params): search, ordering, product_type, size, category,
is_vegetarian, is_vegan, is_gluten_free, contains_nuts, price_min, price_max.

Example:

    GET /api/products/?product_type=SIDE&is_vegan=true&ordering=price

---

## Example flow

# 1. Log in
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"adminpass"}'

# 2. Add a muffin to the cart
curl -X POST http://localhost:8000/api/cart/add-item/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id": 17, "quantity": 1}'

# 3. View the cart
curl http://localhost:8000/api/cart/ -H "Authorization: Bearer $TOKEN"

---

## Notes

- Menu is managed through /admin/ — add categories and products there.
- Choices live in products/choices.py — the admin dropdowns and /api/choices/
  read from the same place.
- One cart per user — created automatically on first use.
- Uses SQLite for development. Swap to Postgres for AWS.

---

## Roadmap

- Order model (snapshot cart at checkout)
- Payments
- Frontend
- AWS deployment (RDS + S3 + EC2 / Elastic Beanstalk)

---

For educational use.
