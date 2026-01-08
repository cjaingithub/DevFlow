#!/usr/bin/env python3
"""
Order Repository
================

Data access layer for Order entities.
Uses async SQLAlchemy for PostgreSQL.
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.order import Order, OrderStatus


class OrderRepository:
    """
    Repository for Order entity operations.

    Provides async data access methods for orders.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize repository with database session.

        Args:
            session: Async database session
        """
        self.session = session

    async def create(self, order: Order) -> Order:
        """
        Create a new order.

        Args:
            order: Order entity to create

        Returns:
            Created order with ID
        """
        self.session.add(order)
        await self.session.flush()
        return order

    async def get_by_id(self, order_id: int) -> Order | None:
        """
        Get order by ID.

        Args:
            order_id: Order ID

        Returns:
            Order if found, None otherwise
        """
        stmt = select(Order).where(Order.order_id == order_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_with_items(self, order_id: int) -> Order | None:
        """
        Get order by ID with items eagerly loaded.

        Args:
            order_id: Order ID

        Returns:
            Order with items if found, None otherwise
        """
        stmt = (
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.order_id == order_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_order_number(self, order_number: str) -> Order | None:
        """
        Get order by order number.

        Args:
            order_number: Unique order number

        Returns:
            Order if found, None otherwise
        """
        stmt = select(Order).where(Order.order_number == order_number)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_customer(
        self,
        customer_id: int,
        status: OrderStatus | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Order]:
        """
        Get orders for a customer.

        Args:
            customer_id: Customer ID
            status: Optional status filter
            limit: Max results
            offset: Result offset

        Returns:
            List of orders
        """
        stmt = (
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.customer_id == customer_id)
            .order_by(Order.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        if status:
            stmt = stmt.where(Order.status == status)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_status(
        self,
        status: OrderStatus,
        limit: int = 100,
    ) -> list[Order]:
        """
        Get orders by status.

        Args:
            status: Order status to filter by
            limit: Max results

        Returns:
            List of orders
        """
        stmt = (
            select(Order)
            .where(Order.status == status)
            .order_by(Order.created_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, order: Order) -> Order:
        """
        Update an order.

        Args:
            order: Order with updates

        Returns:
            Updated order
        """
        await self.session.flush()
        return order

    async def delete(self, order: Order) -> None:
        """
        Delete an order.

        Args:
            order: Order to delete
        """
        await self.session.delete(order)

    async def exists(self, order_id: int) -> bool:
        """
        Check if order exists.

        Args:
            order_id: Order ID

        Returns:
            True if exists
        """
        stmt = select(Order.order_id).where(Order.order_id == order_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def count_by_customer(self, customer_id: int) -> int:
        """
        Count orders for a customer.

        Args:
            customer_id: Customer ID

        Returns:
            Order count
        """
        from sqlalchemy import func

        stmt = (
            select(func.count())
            .select_from(Order)
            .where(Order.customer_id == customer_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0
