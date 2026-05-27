from dataclasses import dataclass, field
from typing import Dict, List
from models import CartItem


class Cart:
    TAX_RATE = 0.12

    def __init__(self, items: Dict[int, CartItem] = None, discount: float = 0.0):
        self.items: Dict[int, CartItem] = items or {}
        self.discount = discount

    def add_item(self, item: CartItem):
        if item.product_id in self.items:
            existing = self.items[item.product_id]
            existing.quantity += item.quantity
            if item.unit_price:
                existing.unit_price = item.unit_price
        else:
            self.items[item.product_id] = item

    def item_count(self) -> int:
        return sum(item.quantity for item in self.items.values())

    def update_quantity(self, product_id: int, quantity: int):
        if product_id in self.items:
            if quantity <= 0:
                self.remove_item(product_id)
            else:
                self.items[product_id].quantity = quantity

    def remove_item(self, product_id: int):
        if product_id in self.items:
            del self.items[product_id]

    def subtotal(self) -> float:
        return round(sum(item.line_total for item in self.items.values()), 2)

    def tax(self) -> float:
        return round(self.subtotal() * self.TAX_RATE, 2)

    def total(self) -> float:
        return round(self.subtotal() + self.tax() - self.discount, 2)

    def is_empty(self) -> bool:
        return len(self.items) == 0

    def to_dict(self):
        return {
            "items": [
                {
                    "product_id": item.product_id,
                    "barcode": item.barcode,
                    "name": item.name,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                }
                for item in self.items.values()
            ],
            "discount": self.discount,
        }

    @classmethod
    def from_session(cls, session_cart):
        items = {}
        for item_data in session_cart.get("items", []):
            item = CartItem(
                product_id=int(item_data["product_id"]),
                barcode=item_data["barcode"],
                name=item_data["name"],
                quantity=int(item_data["quantity"]),
                unit_price=float(item_data["unit_price"]),
            )
            items[item.product_id] = item
        discount = float(session_cart.get("discount", 0.0))
        return cls(items=items, discount=discount)
