from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, Generator, List


@dataclass
class Product:
    id: int
    barcode: str
    name: str
    category: str
    supplier: str
    price: float
    stock_quantity: int
    restock_threshold: int
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "barcode": self.barcode,
            "name": self.name,
            "category": self.category,
            "supplier": self.supplier,
            "price": self.price,
            "stock_quantity": self.stock_quantity,
            "restock_threshold": self.restock_threshold,
            "created_at": self.created_at,
        }

    @classmethod
    def from_row(cls, row: Any) -> "Product":
        if row is None:
            return None
        return cls(
            id=row["id"],
            barcode=row["barcode"],
            name=row["name"],
            category=row["category"],
            supplier=row["supplier"],
            price=float(row["price"]),
            stock_quantity=int(row["stock_quantity"]),
            restock_threshold=int(row["restock_threshold"]),
            created_at=row["created_at"],
        )


@dataclass
class User:
    id: int
    username: str
    password_hash: str
    role: str
    full_name: str


@dataclass
class CartItem:
    product_id: int
    barcode: str
    name: str
    quantity: int
    unit_price: float

    @property
    def line_total(self) -> float:
        return round(self.quantity * self.unit_price, 2)


@dataclass
class Order:
    id: Optional[int]
    order_code: str
    customer_name: str
    customer_email: str
    created_at: str
    subtotal: float
    tax: float
    discount: float
    total: float
    status: str
    payment_method: str
    payment_status: str
    payment_reference: str
    items: List[CartItem] = field(default_factory=list)


class LinkedListNode:
    def __init__(self, data: Any):
        self.data = data
        self.next: Optional[LinkedListNode] = None


class LinkedList:
    def __init__(self):
        self.head: Optional[LinkedListNode] = None
        self.size = 0

    def append(self, data: Any) -> None:
        node = LinkedListNode(data)
        if not self.head:
            self.head = node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = node
        self.size += 1

    def __iter__(self) -> Generator[Any, None, None]:
        current = self.head
        while current:
            yield current.data
            current = current.next

    def find(self, predicate) -> Optional[Any]:
        current = self.head
        while current:
            if predicate(current.data):
                return current.data
            current = current.next
        return None

    def remove(self, predicate) -> bool:
        current = self.head
        prev = None
        while current:
            if predicate(current.data):
                if prev:
                    prev.next = current.next
                else:
                    self.head = current.next
                self.size -= 1
                return True
            prev = current
            current = current.next
        return False

    def to_list(self) -> List[Any]:
        return [item for item in self]
