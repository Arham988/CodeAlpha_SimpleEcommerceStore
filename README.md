# ShopAlpha — Simple E-Commerce Store

**CodeAlpha Full Stack Web Development Internship &bull; Task 1**

A full-featured, responsive, and secure e-commerce web application built from scratch using **Python**, **Django**, and **SQLite**, with a clean frontend crafted strictly in **Pure HTML5, CSS3, and Vanilla JavaScript** (no Bootstrap, Tailwind CSS, or frontend JavaScript frameworks).

---

## 🌟 Key Features

1. **Dynamic Product Catalog (Homepage):**
   * Products fetched dynamically from SQLite database with images, pricing, and live inventory badges.
   * Empty catalog fallback handling.
   * Responsive product card grid with hover elevations and clean typography.

2. **Product Details Page:**
   * Dynamic routing (`/product/<int:pk>/`).
   * High-resolution product images with fallback SVG placeholders.
   * Real-time stock status display (*"Available — X in stock"* or *"Out of stock"*).
   * Interactive quantity selector with bounds enforcement (capped at available inventory).
   * Safe 404 handling (`get_object_or_404`) for non-existent items.

3. **Session-Based Shopping Cart:**
   * Built entirely using Django sessions (`request.session['cart']`).
   * Add to cart from both the homepage grid and the product detail view.
   * Quantity increment, decrement, and item removal directly inside the cart.
   * Live stock limit validation.
   * Global navbar badge (`Cart (X)`) dynamically rendered across all pages via a custom Django Context Processor.
   * Server-side price calculation to prevent client-side price tampering.

4. **User Registration, Login & Logout:**
   * Built on Django's native authentication framework (`django.contrib.auth`).
   * Secure password hashing using PBKDF2 with SHA-256.
   * CSRF protection on all forms.
   * Persistent shopping cart retained across login and logout events.
   * Dynamic navbar reflecting authentication status (*"Welcome, <username>"* & *Logout*).

5. **Checkout & Order Processing:**
   * Protected checkout flow (`@login_required`) with empty cart guards.
   * Customer shipping and contact details form validation.
   * Atomic database transactions (`transaction.atomic`) with row-level locks (`select_for_update`) to prevent race conditions.
   * Historic price snapshots stored in `OrderItem` models.
   * Automatic product stock deduction upon order placement.
   * Cart automatically cleared upon successful transaction.

6. **Order Confirmation & Security:**
   * Detailed receipt page (`/order-success/<int:order_id>/`) with status pills and delivery address.
   * Strict user isolation: users can only view their own orders (tampering returns HTTP 404).

7. **Administrative Dashboard (Django Admin):**
   * Accessible at `/admin/`.
   * Management of products, categories, stock, orders, and inline order items.
   * Search bars, date filters, and custom tabular inlines.

---

## 🛠️ Tech Stack

* **Backend Framework:** Django 6.1.1 (Python 3.14)
* **Database:** SQLite3 (`db.sqlite3`)
* **Frontend:** Pure Semantic HTML5, Custom Responsive CSS3 (CSS Variables, Flexbox, Grid), and Vanilla JavaScript
* **Image Processing:** Pillow 12.3.0
* **Architecture:** Model-View-Template (MVT)

*(Strict compliance: No React, Node.js, Express, Bootstrap, or Tailwind CSS).*

---

## 📁 Project Directory Structure

```text
CodeAlpha_SimpleEcommerceStore/
│
├── .gitignore                    # Prevents git from tracking .venv, db.sqlite3, media/, caches
├── manage.py                     # Django project management utility
├── requirements.txt              # Pinned Python package dependencies
├── db.sqlite3                    # Local SQLite database (git-ignored)
├── README.md                     # Project documentation
│
├── ecommerce_project/            # Project configuration package
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py               # Core project settings (Apps, DB, Media, Static, Context Processors)
│   ├── urls.py                   # Master URL routing
│   └── wsgi.py
│
├── store/                        # Main store application
│   ├── migrations/               # Database schema migration files
│   │   ├── 0001_initial.py       # Product model table migration
│   │   └── 0002_order_orderitem.py # Order & OrderItem tables migration
│   ├── admin.py                  # Django Admin configuration for Product, Order, OrderItem
│   ├── apps.py                   # Store app configuration
│   ├── context_processors.py     # Global cart item counter for the navbar
│   ├── forms.py                  # UserRegistrationForm, UserLoginForm, CheckoutForm
│   ├── models.py                 # Product, Order, OrderItem models
│   ├── tests.py                  # Automated test suite (29 tests)
│   ├── urls.py                   # Storefront, cart, auth, and checkout URL patterns
│   └── views.py                  # Business logic (home, detail, cart, auth, checkout)
│
├── templates/                    # HTML Templates (Django Template Language)
│   └── store/
│       ├── base.html             # Master layout with responsive navbar, alerts, footer
│       ├── home.html             # Product catalog homepage & hero section
│       ├── product_detail.html   # Two-column product detail page with quantity picker
│       ├── cart.html             # Shopping cart table & order summary
│       ├── checkout.html         # Shipping address form & order review
│       ├── order_success.html    # Order confirmation receipt
│       ├── login.html            # User login screen
│       └── register.html         # User registration screen
│
├── static/                       # Static Assets
│   └── store/
│       ├── css/
│       │   └── style.css         # 100% custom, responsive stylesheet
│       └── js/
│           └── script.js         # Vanilla JavaScript (quantity limits & message auto-fade)
│
└── media/                        # User & admin uploaded media (git-ignored)
    └── products/                 # Uploaded product imagery
```

---

## 🚀 Installation & Local Setup

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd CodeAlpha_SimpleEcommerceStore
```

### 2. Create and Activate a Python Virtual Environment

* **On Windows (PowerShell):**
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
* **On macOS/Linux:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations
```bash
python manage.py migrate
```

### 5. Create a Superuser Account (for Django Admin access)
```bash
python manage.py createsuperuser
```
*(Enter your desired username, email, and password).*

### 6. Start the Development Server
```bash
python manage.py runserver
```

Open your browser and navigate to:
* **Storefront:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* **Admin Portal:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🧪 Running the Test Suite

The project includes an automated test suite with **29 comprehensive unit tests** covering views, models, session cart management, inventory stock decrementing, authentication, atomic checkout transactions, and security permissions.

To execute all tests:
```bash
python manage.py test
```

Expected output:
```text
Ran 29 tests in 6.460s

OK
Destroying test database for alias 'default'...
```

To run Django system configuration checks:
```bash
python manage.py check
```

---

## 🛡️ Security Features Implemented

* **SQL Injection Prevention:** All queries use Django's ORM parameterized queries.
* **XSS Prevention:** Django Template Engine automatically escapes dynamic variables.
* **CSRF Protection:** Form submissions require verified CSRF tokens (`{% csrf_token %}`).
* **Secure Authentication:** Passwords hashed with PBKDF2 + SHA-256 with individual salts.
* **Order Isolation:** Users can strictly view only their own order receipts.
* **Concurrency Protection:** Row-level locks (`select_for_update`) and atomic transactions ensure stock is verified and decremented safely during checkout.

---

## 👤 Author

Developed for **CodeAlpha Full Stack Web Development Internship &bull; Task 1**.
