#!/usr/bin/env python3
"""
Order Models
============

SQLAlchemy models for the Order Management system.
Converted from Oracle schema to PostgreSQL/Python.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .customer import Customer
    from .product import Product


class OrderStatus(str, Enum):
    """Order status enumeration."""

    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

    @classmethod
    def valid_transitions(cls) -> dict["OrderStatus", list["OrderStatus"]]:
        """Return valid status transitions."""
        return {
            cls.PENDING: [cls.CONFIRMED, cls.CANCELLED],
            cls.CONFIRMED: [cls.SHIPPED, cls.CANCELLED],
            cls.SHIPPED: [cls.DELIVERED],
            cls.DELIVERED: [],
            cls.CANCELLED: [],
        }

    def can_transition_to(self, new_status: "OrderStatus") -> bool:
        """Check if transition to new status is valid."""
        return new_status in self.valid_transitions().get(self, [])


class Order(Base):
    """
    Order model.

    Represents a customer order with multiple items.
    """

    __tablename__ = "orders"

    order_id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.customer_id"),
        nullable=False,
    )
    order_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )
    status: Mapped[OrderStatus] = mapped_column(
        default=OrderStatus.PENDING,
        nullable=False,
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0"),
    )
    shipping_address: Mapped[str | None] = mapped_column(String(500))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    customer: Mapped["Customer"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )

    # Indexes
    __table_args__ = (
        Index("idx_orders_customer", "customer_id"),
        Index("idx_orders_status", "status"),
        Index("idx_orders_created", "created_at"),
    )

    def calculate_total(self) -> Decimal:
        """Calculate and update total amount from items."""
        self.total_amount = sum(item.line_total for item in self.items)
        return self.total_amount

    def can_modify(self) -> bool:
        """Check if order can be modified."""
        return self.status in (OrderStatus.PENDING, OrderStatus.CONFIRMED)

    def __repr__(self) -> str:
        return f"<Order {self.order_number} ({self.status.value})>"


class OrderItem(Base):
    """
    Order item model.

    Represents a single line item in an order.
    """

    __tablename__ = "order_items"

    item_id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.order_id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.product_id"),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    line_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship()

    # Constraints
    __table_args__ = (
        CheckConstraint("quantity > 0", name="chk_quantity"),
        Index("idx_items_order", "order_id"),
    )

    def calculate_line_total(self) -> Decimal:
        """Calculate line total from quantity and unit price."""
        self.line_total = self.unit_price * self.quantity
        return self.line_total

    def __repr__(self) -> str:
        return f"<OrderItem {self.item_id}: {self.quantity}x product {self.product_id}>"
