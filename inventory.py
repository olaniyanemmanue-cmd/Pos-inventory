from datetime import datetime
from models import Product, LinkedList


class InventoryManager:
    def __init__(self, db):
        self.db = db
        self.products = LinkedList()
        self.reload()

    def reload(self):
        self.products = LinkedList()
        rows = self.db.fetchall("SELECT * FROM products ORDER BY name")
        for row in rows:
            product = Product.from_row(row)
            self.products.append(product)

    def add_product(self, barcode: str, name: str, category: str, supplier: str, price: float, stock_quantity: int, restock_threshold: int):
        created_at = datetime.now().isoformat()
        self.db.execute(
            "INSERT INTO products (barcode, name, category, supplier, price, stock_quantity, restock_threshold, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (barcode, name, category, supplier, price, stock_quantity, restock_threshold, created_at),
        )
        self.reload()

    def update_product(self, product_id: int, barcode: str, name: str, category: str, supplier: str, price: float, stock_quantity: int, restock_threshold: int):
        self.db.execute(
            "UPDATE products SET barcode=?, name=?, category=?, supplier=?, price=?, stock_quantity=?, restock_threshold=? WHERE id=?",
            (barcode, name, category, supplier, price, stock_quantity, restock_threshold, product_id),
        )
        self.reload()

    def remove_product(self, product_id: int):
        self.db.execute("DELETE FROM products WHERE id=?", (product_id,))
        self.reload()

    def search(self, query: str = "", category: str = "", barcode: str = ""):
        query = query.lower().strip()
        category = category.lower().strip()
        barcode = barcode.strip()
        results = []
        for product in self.products:
            if barcode and barcode != product.barcode:
                continue
            if category and category not in product.category.lower():
                continue
            if query and query not in product.name.lower():
                continue
            results.append(product)
        return results if results else self.products.to_list()

    def get_product_by_id(self, product_id: int):
        return self.products.find(lambda p: p.id == product_id)

    def get_product_by_barcode(self, barcode: str):
        return self.products.find(lambda p: p.barcode == barcode)

    def reduce_stock(self, product_id: int, quantity: int) -> bool:
        product = self.get_product_by_id(product_id)
        if not product or product.stock_quantity < quantity:
            return False
        new_stock = product.stock_quantity - quantity
        self.db.execute("UPDATE products SET stock_quantity = ? WHERE id = ?", (new_stock, product_id))
        self.reload()
        return True

    def low_stock_items(self):
        return [product for product in self.products if product.stock_quantity <= product.restock_threshold]

    def restock(self, product_id: int, additional_quantity: int):
        product = self.get_product_by_id(product_id)
        if not product:
            return False
        new_stock = product.stock_quantity + additional_quantity
        self.db.execute("UPDATE products SET stock_quantity = ? WHERE id = ?", (new_stock, product_id))
        self.reload()
        return True

    def all_products(self):
        return self.products.to_list()
