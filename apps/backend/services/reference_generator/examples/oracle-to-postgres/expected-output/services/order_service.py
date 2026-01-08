#!/usr/bin/env python3
"""
Order Service
=============

Business logic service for Order Management.
Replaces Oracle stored procedures with Python async methods.

Original procedures replaced:
- SP_CREATE_ORDER -> create_order()
- SP_UPDATE_ORDER_STATUS -> update_order_status()
- SP_GET_ORDER_DETAILS -> get_order_details()
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.order import Order, OrderItem, OrderStatus
from ..repositories.order_repository import OrderRepository


# =============================================================================
# RESULT TYPES
# =============================================================================


@dataclass
class CreateOrderResult:
    """Result of order creation."""

    success: bool
    order_id: int | None = None
    order_number: str | None = None
    error_message: str | None = None


@dataclass
class UpdateStatusResult:
    """Result of status update."""

    success: bool
    error_message: str | None = None


@dataclass
class OrderItemInput:
    """Input for an order item."""

    product_id: int
    quantity: int


# =============================================================================
# ORDER SERVICE
# =============================================================================


class OrderService:
    """
    Order management service.

    Provides business logic for order operations,
    replacing Oracle stored procedures.
    """

    def __init__(
        self,
        session: AsyncSession,
        order_repo: OrderRepository,
        customer_repo: Any = None,  # CustomerRepository
        product_repo: Any = None,  # ProductRepository
    ) -> None:
        """
        Initialize order service.

        Args:
            session: Database session
            order_repo: Order repository
            customer_repo: Customer repository
            product_repo: Product repository
        """
        self.session = session
        self.order_repo = order_repo
        self.customer_repo = customer_repo
        self.product_repo = product_repo

    async def create_order(
        self,
        customer_id: int,
        items: list[OrderItemInput],
        shipping_address: str,
        notes: str | None = None,
    ) -> CreateOrderResult:
        """
        Create a new order with items.

        Replaces Oracle SP_CREATE_ORDER procedure.

        Args:
            customer_id: Customer ID
            items: List of order items
            shipping_address: Delivery address
            notes: Optional notes

        Returns:
            CreateOrderResult with order details or error
        """
        # Validate customer exists
        if self.customer_repo:
            customer_exists = await self.customer_repo.exists(customer_id)
            if not customer_exists:
                return CreateOrderResult(
                    success=False,
                    error_message=f"Customer not found: {customer_id}",
                )

        # Validate stock for all items
        if self.product_repo:
            for item in items:
                has_stock = await self.product_repo.check_stock(
                    item.product_id, item.quantity
                )
                if not has_stock:
                    return CreateOrderResult(
                        success=False,
                        error_message=f"Insufficient stock for product: {item.product_id}",
                    )

        try:
            # Generate order number
            order_number = self._generate_order_number()

            # Create order
            order = Order(
                customer_id=customer_id,
                order_number=order_number,
                status=OrderStatus.PENDING,
                shipping_address=shipping_address,
                notes=notes,
                total_amount=Decimal("0"),
            )

            # Add items
            for item_input in items:
                product = None
                if self.product_repo:
                    product = await self.product_repo.get_by_id(item_input.product_id)

                unit_price = product.unit_price if product else Decimal("0")
                line_total = unit_price * item_input.quantity

                order_item = OrderItem(
                    product_id=item_input.product_id,
                    quantity=item_input.quantity,
                    unit_price=unit_price,
                    line_total=line_total,
                )
                order.items.append(order_item)

            # Calculate total
            order.calculate_total()

            # Save order
            await self.order_repo.create(order)
            await self.session.commit()

            return CreateOrderResult(
                success=True,
                order_id=order.order_id,
                order_number=order.order_number,
            )

        except Exception as e:
            await self.session.rollback()
            return CreateOrderResult(
                success=False,
                error_message=str(e),
            )

    async def update_order_status(
        self,
        order_id: int,
        new_status: OrderStatus,
    ) -> UpdateStatusResult:
        """
        Update order status with transition validation.

        Replaces Oracle SP_UPDATE_ORDER_STATUS procedure.

        Args:
            order_id: Order ID
            new_status: New status to set

        Returns:
            UpdateStatusResult with success or error
        """
        # Get order
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            return UpdateStatusResult(
                success=False,
                error_message=f"Order not found: {order_id}",
            )

        # Validate transition
        if not order.status.can_transition_to(new_status):
            return UpdateStatusResult(
                success=False,
                error_message=f"Invalid status transition: {order.status.value} -> {new_status.value}",
            )

        try:
            # Update status
            order.status = new_status
            order.updated_at = datetime.utcnow()

            # If cancelling, restore stock
            if new_status == OrderStatus.CANCELLED and self.product_repo:
                for item in order.items:
                    await self.product_repo.restore_stock(
                        item.product_id, item.quantity
                    )

            await self.session.commit()

            return UpdateStatusResult(success=True)

        except Exception as e:
            await self.session.rollback()
            return UpdateStatusResult(
                success=False,
                error_message=str(e),
            )

    async def get_order_details(self, order_id: int) -> dict[str, Any] | None:
        """
        Get complete order details with items.

        Args:
            order_id: Order ID

        Returns:
            Order details dict or None if not found
        """
        order = await self.order_repo.get_by_id_with_items(order_id)
        if not order:
            return None

        return {
            "order_id": order.order_id,
            "order_number": order.order_number,
            "customer_id": order.customer_id,
            "status": order.status.value,
            "total_amount": float(order.total_amount),
            "shipping_address": order.shipping_address,
            "notes": order.notes,
            "created_at": order.created_at.isoformat(),
            "updated_at": order.updated_at.isoformat(),
            "items": [
                {
                    "item_id": item.item_id,
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": float(item.unit_price),
                    "line_total": float(item.line_total),
                }
                for item in order.items
            ],
        }

    async def get_customer_orders(
        self,
        customer_id: int,
        status: OrderStatus | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        Get orders for a customer.

        Args:
            customer_id: Customer ID
            status: Optional status filter
            limit: Max results
            offset: Result offset

        Returns:
            List of order summaries
        """
        orders = await self.order_repo.get_by_customer(
            customer_id=customer_id,
            status=status,
            limit=limit,
            offset=offset,
        )

        return [
            {
                "order_id": order.order_id,
                "order_number": order.order_number,
                "status": order.status.value,
                "total_amount": float(order.total_amount),
                "created_at": order.created_at.isoformat(),
                "item_count": len(order.items),
            }
            for order in orders
        ]

    def _generate_order_number(self) -> str:
        """Generate a unique order number."""
        from datetime import datetime
        import random

        date_part = datetime.now().strftime("%Y%m%d")
        random_part = str(random.randint(100000, 999999))
        return f"ORD-{date_part}-{random_part}"
