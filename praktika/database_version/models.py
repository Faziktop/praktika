from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Customer:
    id: int
    name: str
    email: str
    phone: str

@dataclass
class Product:
    id: int
    name: str
    price: float
    quantity: int

@dataclass
class Order:
    id: int
    customer_id: int
    products: List[dict]
    total_amount: float
    status: str
    created_date: datetime