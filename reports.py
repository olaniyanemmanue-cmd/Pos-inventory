from datetime import datetime


class SalesManager:
    def __init__(self, db):
        self.db = db

    def get_sales_history(self):
        rows = self.db.fetchall("SELECT * FROM orders ORDER BY created_at DESC")
        return [dict(row) for row in rows]

    def get_order_items(self, order_id: int):
        rows = self.db.fetchall("SELECT * FROM order_items WHERE order_id = ?", (order_id,))
        return [dict(row) for row in rows]

    def get_daily_report(self, date_str: str = None):
        date_str = date_str or datetime.now().strftime("%Y-%m-%d")
        rows = self.db.fetchall(
            "SELECT * FROM orders WHERE date(created_at) = ? ORDER BY created_at DESC",
            (date_str,),
        )
        return self._build_report(rows)

    def get_monthly_report(self, year: int = None, month: int = None):
        today = datetime.now()
        year = year or today.year
        month = month or today.month
        rows = self.db.fetchall(
            "SELECT * FROM orders WHERE strftime('%Y', created_at) = ? AND strftime('%m', created_at) = ? ORDER BY created_at DESC",
            (str(year), f"{month:02d}"),
        )
        return self._build_report(rows)

    def _build_report(self, rows):
        orders = [dict(row) for row in rows]
        total_revenue = sum(order["total"] for order in orders)
        total_tax = sum(order["tax"] for order in orders)
        total_discount = sum(order["discount"] for order in orders)
        total_orders = len(orders)
        average = round(total_revenue / total_orders, 2) if total_orders else 0.0
        return {
            "orders": orders,
            "total_revenue": round(total_revenue, 2),
            "total_tax": round(total_tax, 2),
            "total_discount": round(total_discount, 2),
            "total_orders": total_orders,
            "average_order_value": average,
        }
