import random
from datetime import datetime


class PaymentManager:
    SUPPORTED_METHODS = ["Card", "Mobile Money", "Bank Transfer", "PayPal"]

    def __init__(self, db):
        self.db = db

    def simulate_gateway(self, method: str, amount: float) -> dict:
        if method not in self.SUPPORTED_METHODS:
            return {"status": "failed", "reference": "INVALID_METHOD"}

        success = random.random() > 0.08
        status = "completed" if success else "failed"
        reference = f"PAY-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000,9999)}"
        return {"status": status, "reference": reference}

    def record_payment(self, order_id: int, method: str, amount: float, status: str, reference: str):
        created_at = datetime.now().isoformat()
        self.db.execute(
            "INSERT INTO payments (order_id, method, amount, status, reference, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (order_id, method, amount, status, reference, created_at),
        )
        return status
