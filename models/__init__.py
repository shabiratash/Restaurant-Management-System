"""Domain models as lightweight dataclasses."""
from models.user import User
from models.food import Category, Food
from models.customer import Customer
from models.table import RestaurantTable
from models.inventory import InventoryItem
from models.order import Order, OrderItem

__all__ = [
    "User", "Category", "Food", "Customer",
    "RestaurantTable", "InventoryItem", "Order", "OrderItem",
]
