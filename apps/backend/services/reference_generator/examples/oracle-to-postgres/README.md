# Oracle to AWS PostgreSQL Migration Example

This example demonstrates how to use the Reference-Based Code Generation feature
to migrate an Oracle-based Order Management system to AWS PostgreSQL with Python.

## Scenario

**Source System:**
- Oracle Database with PL/SQL stored procedures
- SQL-based business logic
- Traditional JDBC data access

**Target System:**
- AWS PostgreSQL (RDS/Aurora)
- Python with async SQLAlchemy 2.0
- Repository/Service pattern

## Reference Structure

```
oracle-to-postgres/
├── requirements/
│   └── order-management.md      # Original feature requirements
│
├── oracle/                      # Oracle source (reference)
│   ├── schema.sql               # CREATE TABLE with Oracle types
│   └── procedures/
│       ├── create_order.sql     # SP_CREATE_ORDER
│       └── update_order_status.sql
│
└── expected-output/             # Generated PostgreSQL/Python
    ├── schema/
    │   └── postgres_schema.sql  # PostgreSQL schema with ENUMs
    ├── models/
    │   └── order.py             # SQLAlchemy models
    ├── repositories/
    │   └── order_repository.py  # Async repository pattern
    └── services/
        └── order_service.py     # Business logic service
```

## Usage

### Step 1: Load the Oracle reference

```bash
python -m services.reference_generator.service \
    --action load \
    --reference apps/backend/services/reference_generator/examples/oracle-to-postgres \
    --name oracle-order-management
```

### Step 2: Create new requirements

Create a requirements file for a new feature (e.g., `inventory-management.md`):

```markdown
# Inventory Management Requirements

## Features
- Track product stock levels
- Record stock movements (in/out)
- Generate low stock alerts
- Audit trail for all changes

## Data Model
- Inventory: product_id, quantity, location, last_counted
- StockMovement: movement_type, quantity, reference, timestamp
```

### Step 3: Generate PostgreSQL/Python implementation

```bash
python -m services.reference_generator.service \
    --action generate \
    --name oracle-order-management \
    --requirements inventory-management.md \
    --entity-mapping '{"reference": "Order", "new": "Inventory"}' \
    --output generated/inventory-postgres
```

### Step 4: Review generated code

The generator produces:
- `postgres_schema.sql` - Tables using PostgreSQL types
- `inventory.py` - SQLAlchemy models with relationships
- `inventory_repository.py` - Async repository with proper queries
- `inventory_service.py` - Business logic replacing stored procedures
- `test_inventory.py` - Test templates

## Transformations Applied

### Data Type Conversions

| Oracle | PostgreSQL |
|--------|------------|
| `NUMBER(10)` | `INTEGER` / `SERIAL` |
| `NUMBER(10,2)` | `DECIMAL(10,2)` |
| `VARCHAR2(255)` | `VARCHAR(255)` |
| `SYSTIMESTAMP` | `CURRENT_TIMESTAMP` |
| `SYSDATE` | `CURRENT_DATE` |
| `CLOB` | `TEXT` |
| `BLOB` | `BYTEA` |

### Stored Procedure to Python Mapping

| Oracle Procedure | Python Method |
|-----------------|---------------|
| `SP_CREATE_ORDER` | `OrderService.create_order()` |
| `SP_UPDATE_ORDER_STATUS` | `OrderService.update_order_status()` |
| `SP_GET_ORDER_DETAILS` | `OrderService.get_order_details()` |

### Pattern Conversions

1. **Sequences → SERIAL**: Oracle sequences become PostgreSQL SERIAL/IDENTITY
2. **Triggers → Functions**: Oracle triggers become PostgreSQL trigger functions
3. **Cursors → Query Results**: SYS_REFCURSOR becomes async query results
4. **NVL → COALESCE**: Oracle NVL becomes standard COALESCE

## Key Benefits

1. **Pattern Consistency**: New features follow the same patterns as the reference
2. **Tech Stack Migration**: Oracle concepts translate to PostgreSQL/Python equivalents
3. **Async Support**: Generated code uses async/await patterns
4. **Modern Python**: Type hints, dataclasses, and modern SQLAlchemy 2.0
5. **Test Coverage**: Automatic test template generation
