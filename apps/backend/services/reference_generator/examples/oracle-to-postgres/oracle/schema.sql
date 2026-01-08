-- Oracle Order Management Schema
-- ================================
-- 
-- This schema defines the core order management tables
-- using Oracle-specific data types and syntax.

-- Orders table
CREATE TABLE orders (
    order_id NUMBER(10) PRIMARY KEY,
    customer_id NUMBER(10) NOT NULL,
    order_number VARCHAR2(50) NOT NULL UNIQUE,
    status VARCHAR2(20) DEFAULT 'PENDING' NOT NULL,
    total_amount NUMBER(10,2) DEFAULT 0,
    shipping_address VARCHAR2(500),
    notes CLOB,
    created_at TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT fk_orders_customer 
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    CONSTRAINT chk_order_status 
        CHECK (status IN ('PENDING', 'CONFIRMED', 'SHIPPED', 'DELIVERED', 'CANCELLED'))
);

-- Create sequence for order_id
CREATE SEQUENCE orders_seq
    START WITH 1
    INCREMENT BY 1
    NOCACHE
    NOCYCLE;

-- Order items table
CREATE TABLE order_items (
    item_id NUMBER(10) PRIMARY KEY,
    order_id NUMBER(10) NOT NULL,
    product_id NUMBER(10) NOT NULL,
    quantity NUMBER(5) NOT NULL,
    unit_price NUMBER(10,2) NOT NULL,
    line_total NUMBER(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT fk_items_order 
        FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    CONSTRAINT fk_items_product 
        FOREIGN KEY (product_id) REFERENCES products(product_id),
    CONSTRAINT chk_quantity 
        CHECK (quantity > 0)
);

-- Create sequence for item_id
CREATE SEQUENCE order_items_seq
    START WITH 1
    INCREMENT BY 1
    NOCACHE
    NOCYCLE;

-- Create index for common queries
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created ON orders(created_at);
CREATE INDEX idx_items_order ON order_items(order_id);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE TRIGGER trg_orders_updated
BEFORE UPDATE ON orders
FOR EACH ROW
BEGIN
    :NEW.updated_at := SYSTIMESTAMP;
END;
/
