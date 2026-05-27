import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from database import DatabaseManager
from auth import AuthManager
from inventory import InventoryManager
from cart import Cart, CartItem
from payment import PaymentManager
from reports import SalesManager
from utils import ReceiptGenerator
from models import Order

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

# Managers
DB = DatabaseManager()
AUTH = AuthManager(DB)
INVENTORY = InventoryManager(DB)
PAYMENTS = PaymentManager(DB)
SALES = SalesManager(DB)


def current_user():
    return session.get("user")


def login_required(view):
    def wrapped(*args, **kwargs):
        if not current_user():
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    wrapped.__name__ = view.__name__
    return wrapped


def admin_required(view):
    def wrapped(*args, **kwargs):
        user = current_user()
        if not user or user.get("role") != "Admin":
            flash("Admin access required.", "warning")
            return redirect(url_for("dashboard"))
        return view(*args, **kwargs)
    wrapped.__name__ = view.__name__
    return wrapped


def get_cart():
    return Cart.from_session(session.get("cart", {}))


def save_cart(cart: Cart):
    session["cart"] = cart.to_dict()


def add_product_to_cart(cart: Cart, product, quantity: int) -> bool:
    if quantity < 1:
        return False
    if quantity > product.stock_quantity:
        flash(f"Insufficient stock for {product.name}.", "warning")
        return False

    cart.add_item(CartItem(
        product_id=product.id,
        barcode=product.barcode,
        name=product.name,
        quantity=quantity,
        unit_price=product.price,
    ))
    return True


@app.route("/")
def index():
    if current_user():
        return redirect(url_for("dashboard"))
    return render_template("welcome.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        user = AUTH.authenticate(username, password)
        if user:
            session["user"] = {"id": user.id, "username": user.username, "role": user.role, "full_name": user.full_name}
            flash(f"Welcome back, {user.full_name}!", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid login credentials.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("cart", None)
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    products = INVENTORY.all_products()
    low_stock = INVENTORY.low_stock_items()
    recent_orders = SALES.get_sales_history()[:5]
    return render_template(
        "dashboard.html",
        user=user,
        total_products=len(products),
        low_stock=low_stock,
        recent_orders=recent_orders,
        summary={
            "low_stock": len(low_stock),
            "active_cart": get_cart().item_count(),
            "today_sales": SALES.get_daily_report()["total_revenue"],
        },
    )


@app.route("/products")
@login_required
def products():
    query = request.args.get("search", "")
    category = request.args.get("category", "")
    barcode = request.args.get("barcode", "")
    products = INVENTORY.search(query=query, category=category, barcode=barcode)
    return render_template("products.html", user=current_user(), products=products, query=query, category=category, barcode=barcode)


@app.route("/products/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_product():
    if request.method == "POST":
        INVENTORY.add_product(
            barcode=request.form["barcode"].strip(),
            name=request.form["name"].strip(),
            category=request.form["category"].strip(),
            supplier=request.form["supplier"].strip(),
            price=float(request.form["price"]),
            stock_quantity=int(request.form["stock_quantity"]),
            restock_threshold=int(request.form["restock_threshold"]),
        )
        flash("Product added successfully.", "success")
        return redirect(url_for("products"))
    return render_template("product_form.html", user=current_user(), product=None)


@app.route("/products/edit/<int:product_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_product(product_id):
    product = INVENTORY.get_product_by_id(product_id)
    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for("products"))
    if request.method == "POST":
        INVENTORY.update_product(
            product_id=product.id,
            barcode=request.form["barcode"].strip(),
            name=request.form["name"].strip(),
            category=request.form["category"].strip(),
            supplier=request.form["supplier"].strip(),
            price=float(request.form["price"]),
            stock_quantity=int(request.form["stock_quantity"]),
            restock_threshold=int(request.form["restock_threshold"]),
        )
        flash("Product updated successfully.", "success")
        return redirect(url_for("products"))
    return render_template("product_form.html", user=current_user(), product=product)


@app.route("/products/delete/<int:product_id>")
@login_required
@admin_required
def delete_product(product_id):
    INVENTORY.remove_product(product_id)
    flash("Product removed.", "info")
    return redirect(url_for("products"))


@app.route("/cart")
@login_required
def view_cart():
    cart = get_cart()
    return render_template("cart.html", user=current_user(), cart=cart)


@app.route("/cart/add/<int:product_id>", methods=["POST"])
@login_required
def add_to_cart(product_id):
    quantity = int(request.form.get("quantity", 1))
    product = INVENTORY.get_product_by_id(product_id)
    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for("products"))

    cart = get_cart()
    if add_product_to_cart(cart, product, quantity):
        save_cart(cart)
        flash("Item added to cart.", "success")
    return redirect(url_for("view_cart"))


@app.route("/cart/add-multiple", methods=["POST"])
@login_required
def add_multiple_to_cart():
    product_ids = request.form.getlist("product_ids")
    if not product_ids:
        flash("Select at least one product to add.", "warning")
        return redirect(url_for("products"))

    cart = get_cart()
    added_count = 0

    for product_id in product_ids:
        product = INVENTORY.get_product_by_id(int(product_id))
        if not product:
            continue
        quantity = int(request.form.get(f"quantity_{product_id}", 1) or 1)
        if add_product_to_cart(cart, product, quantity):
            added_count += 1

    save_cart(cart)
    if added_count:
        flash(f"Added {added_count} product(s) to cart.", "success")
    else:
        flash("No valid products were added.", "warning")
    return redirect(url_for("view_cart"))


@app.route("/cart/update", methods=["POST"])
@login_required
def update_cart():
    cart = get_cart()
    for key, quantity in request.form.items():
        if key.startswith("quantity_"):
            product_id = int(key.replace("quantity_", ""))
            cart.update_quantity(product_id, int(quantity))
    save_cart(cart)
    flash("Cart updated.", "success")
    return redirect(url_for("view_cart"))


@app.route("/cart/remove/<int:product_id>")
@login_required
def remove_from_cart(product_id):
    cart = get_cart()
    cart.remove_item(product_id)
    save_cart(cart)
    flash("Item removed.", "info")
    return redirect(url_for("view_cart"))


@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    cart = get_cart()
    if cart.is_empty():
        flash("Your cart is empty.", "warning")
        return redirect(url_for("products"))
    if request.method == "POST":
        customer_name = request.form.get("customer_name", "Walk-in Customer").strip()
        customer_email = request.form.get("customer_email", "").strip()
        discount = float(request.form.get("discount", 0.0))
        cart.discount = discount
        payment_method = request.form.get("payment_method", "Card")
        total_amount = cart.total()

        order_code = f"POS-{datetime.now().strftime('%Y%m%d%H%M%S')}-{current_user()['id']}"
        created_at = datetime.now().isoformat()
        order_id = DB.execute(
            "INSERT INTO orders (order_code, customer_name, customer_email, created_at, subtotal, tax, discount, total, status, payment_method, payment_status, payment_reference) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (order_code, customer_name, customer_email, created_at, cart.subtotal(), cart.tax(), cart.discount, total_amount, "pending", payment_method, "pending", ""),
        ).lastrowid

        for item in cart.items.values():
            DB.execute(
                "INSERT INTO order_items (order_id, product_id, barcode, name, quantity, unit_price, line_total) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (order_id, item.product_id, item.barcode, item.name, item.quantity, item.unit_price, item.line_total),
            )
            INVENTORY.reduce_stock(item.product_id, item.quantity)

        payment_response = PAYMENTS.simulate_gateway(payment_method, total_amount)
        PAYMENTS.record_payment(order_id, payment_method, total_amount, payment_response["status"], payment_response["reference"])
        DB.execute(
            "UPDATE orders SET status = ?, payment_status = ?, payment_reference = ? WHERE id = ?",
            ("completed" if payment_response["status"] == "completed" else "failed", payment_response["status"], payment_response["reference"], order_id),
        )
        session.pop("cart", None)

        flash("Checkout complete. Receipt generated.", "success")
        return redirect(url_for("order_detail", order_id=order_id))
    return render_template("checkout.html", user=current_user(), cart=cart, payment_methods=PAYMENTS.SUPPORTED_METHODS)


@app.route("/orders")
@login_required
def orders():
    history = SALES.get_sales_history()
    return render_template("orders.html", user=current_user(), orders=history)


@app.route("/order/<int:order_id>")
@login_required
def order_detail(order_id):
    order_row = DB.fetchone("SELECT * FROM orders WHERE id = ?", (order_id,))
    if not order_row:
        flash("Order not found.", "danger")
        return redirect(url_for("orders"))
    order = dict(order_row)
    items = SALES.get_order_items(order_id)
    receipt_path = os.path.join("data", "receipts", f"receipt_{order['order_code']}.pdf")
    ReceiptGenerator.create_pdf_receipt(order, items, receipt_path)
    return render_template("order_detail.html", user=current_user(), order=order, items=items, receipt_path=receipt_path)


@app.route("/download/receipt/<int:order_id>")
@login_required
def download_receipt(order_id):
    order_row = DB.fetchone("SELECT * FROM orders WHERE id = ?", (order_id,))
    if not order_row:
        flash("Order not found.", "danger")
        return redirect(url_for("orders"))
    order = dict(order_row)
    receipt_path = os.path.join("data", "receipts", f"receipt_{order['order_code']}.pdf")
    if not os.path.exists(receipt_path):
        items = SALES.get_order_items(order_id)
        ReceiptGenerator.create_pdf_receipt(order, items, receipt_path)
    return send_file(receipt_path, as_attachment=True)


@app.route("/reports")
@login_required
def reports():
    date_filter = request.args.get("date", datetime.now().strftime("%Y-%m-%d"))
    year = int(request.args.get("year", datetime.now().year))
    month = int(request.args.get("month", datetime.now().month))
    daily = SALES.get_daily_report(date_filter)
    monthly = SALES.get_monthly_report(year, month)
    return render_template("reports.html", user=current_user(), daily=daily, monthly=monthly, selected_date=date_filter, selected_year=year, selected_month=month)


@app.route("/backup")
@login_required
def backup():
    products_file = DB.backup_table_json("products")
    orders_file = DB.backup_table_json("orders")
    payments_file = DB.backup_table_json("payments")
    flash("Backup complete: %s, %s, %s" % (os.path.basename(products_file), os.path.basename(orders_file), os.path.basename(payments_file)), "info")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True)
