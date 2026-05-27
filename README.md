# Inventory & POS System

A student project Inventory and Point-of-Sale system built with Python, Flask, SQLite, and Bootstrap. It demonstrates Object-Oriented Programming, Linked Lists, File I/O, and database persistence.

## Features

- Secure login with `Admin` and `Cashier` roles
- Product inventory management with barcode, category, supplier, price, stock, and restock threshold
- Product search by name, category, or barcode
- Shopping cart and checkout workflow
- Receipt generation with PDF export
- Daily and monthly sales reports, analytics, and revenue summaries
- Low-stock alerts and restock functionality
- Persistent SQLite database storage plus JSON backups
- Payment gateway simulation supporting Card, Mobile Money, Bank Transfer, and PayPal
- Transaction records, payment status tracking, and sales history
- Responsive Bootstrap dashboard and menu-driven workflow

## Setup Instructions

1. Install Python 3.9+.
2. Open a terminal in the workspace folder.
3. Create a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
4. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
5. Initialize the database and seed sample data:
   ```powershell
   python setup_db.py
   ```
6. Start the application:
   ```powershell
   python app.py
   ```
7. Open `http://127.0.0.1:5000` in your browser.

## Default Accounts

- Admin: `admin` / `admin123`
- Cashier: `cashier` / `cashier123`

## Project Structure

- `app.py` - Flask application routes and workflow
- `database.py` - SQLite database manager and backups
- `auth.py` - authentication manager
- `inventory.py` - inventory manager with linked list storage
- `cart.py` - shopping cart domain model
- `payment.py` - payment gateway simulation and transaction records
- `reports.py` - daily/monthly sales analytics
- `utils.py` - helper utilities and PDF receipt generation
- `templates/` - HTML templates
- `static/` - static CSS and JS assets
- `data/` - SQLite database and backups

## Testing & Demo Data

- Run `python setup_db.py` to populate sample products.
- Use the `Reports`, `Orders`, and `Backup` views to verify database persistence.

## Notes

- The system is designed for student projects and demonstrates secure login, real-time stock updates, receipt generation, and payment simulation.
- For production use, extend the authentication, database security, and payment integration layers.
