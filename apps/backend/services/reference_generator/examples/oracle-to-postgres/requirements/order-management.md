# Order Management System Requirements

## Overview

A complete order management system that handles:
- Order creation and lifecycle management
- Order item management
- Status tracking and transitions
- Customer order history

## Features

### Order Creation
- Create new orders with multiple items
- Validate customer exists before order creation
- Validate product stock availability
- Calculate order totals automatically

### Order Status Management
- Track order status (PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED)
- Status transition validation
- Automatic timestamp updates

### Order Details
- Retrieve complete order information
- Include all order items with product details
- Support order search by customer

## Data Model

### Orders Table
| Column | Type | Description |
|--------|------|-------------|
| order_id | NUMBER(10) | Primary key |
| customer_id | NUMBER(10) | Foreign key to customers |
| order_number | VARCHAR2(50) | Unique order reference |
| status | VARCHAR2(20) | Order status |
| total_amount | NUMBER(10,2) | Calculated total |
| shipping_address | VARCHAR2(500) | Delivery address |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

### Order Items Table
| Column | Type | Description |
|--------|------|-------------|
| item_id | NUMBER(10) | Primary key |
| order_id | NUMBER(10) | Foreign key to orders |
| product_id | NUMBER(10) | Foreign key to products |
| quantity | NUMBER(5) | Item quantity |
| unit_price | NUMBER(10,2) | Price at time of order |
| line_total | NUMBER(10,2) | Calculated line total |

## Acceptance Criteria

1. Orders can be created with valid customer and products
2. Stock is validated before order confirmation
3. Order totals are calculated correctly
4. Status transitions follow business rules
5. All operations are audited with timestamps
6. API responds within 200ms for single order operations
