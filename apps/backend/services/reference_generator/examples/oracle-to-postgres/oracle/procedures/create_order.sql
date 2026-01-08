-- Create Order Stored Procedure
-- ==============================
--
-- Creates a new order with items, validates stock, and calculates totals.

CREATE OR REPLACE PROCEDURE SP_CREATE_ORDER (
    p_customer_id    IN NUMBER,
    p_items          IN SYS.ODCIVARCHAR2LIST,  -- Array of 'product_id:quantity' strings
    p_shipping_addr  IN VARCHAR2,
    p_notes          IN CLOB DEFAULT NULL,
    p_order_id       OUT NUMBER,
    p_order_number   OUT VARCHAR2,
    p_status         OUT VARCHAR2,
    p_error_message  OUT VARCHAR2
) AS
    v_order_id       NUMBER;
    v_order_number   VARCHAR2(50);
    v_total_amount   NUMBER(10,2) := 0;
    v_product_id     NUMBER;
    v_quantity       NUMBER;
    v_unit_price     NUMBER(10,2);
    v_line_total     NUMBER(10,2);
    v_stock_qty      NUMBER;
    v_item           VARCHAR2(100);
    v_pos            NUMBER;
BEGIN
    p_status := 'SUCCESS';
    p_error_message := NULL;
    
    -- Validate customer exists
    DECLARE
        v_customer_exists NUMBER;
    BEGIN
        SELECT COUNT(*) INTO v_customer_exists
        FROM customers
        WHERE customer_id = p_customer_id;
        
        IF v_customer_exists = 0 THEN
            p_status := 'ERROR';
            p_error_message := 'Customer not found: ' || p_customer_id;
            RETURN;
        END IF;
    END;
    
    -- Generate order ID and number
    SELECT orders_seq.NEXTVAL INTO v_order_id FROM DUAL;
    v_order_number := 'ORD-' || TO_CHAR(SYSDATE, 'YYYYMMDD') || '-' || LPAD(v_order_id, 6, '0');
    
    -- Create the order header
    INSERT INTO orders (
        order_id,
        customer_id,
        order_number,
        status,
        total_amount,
        shipping_address,
        notes,
        created_at,
        updated_at
    ) VALUES (
        v_order_id,
        p_customer_id,
        v_order_number,
        'PENDING',
        0,
        p_shipping_addr,
        p_notes,
        SYSTIMESTAMP,
        SYSTIMESTAMP
    );
    
    -- Process each item
    FOR i IN 1..p_items.COUNT LOOP
        v_item := p_items(i);
        v_pos := INSTR(v_item, ':');
        
        IF v_pos = 0 THEN
            ROLLBACK;
            p_status := 'ERROR';
            p_error_message := 'Invalid item format: ' || v_item;
            RETURN;
        END IF;
        
        v_product_id := TO_NUMBER(SUBSTR(v_item, 1, v_pos - 1));
        v_quantity := TO_NUMBER(SUBSTR(v_item, v_pos + 1));
        
        -- Get product price and check stock
        BEGIN
            SELECT unit_price, stock_quantity
            INTO v_unit_price, v_stock_qty
            FROM products
            WHERE product_id = v_product_id;
            
            IF v_stock_qty < v_quantity THEN
                ROLLBACK;
                p_status := 'ERROR';
                p_error_message := 'Insufficient stock for product: ' || v_product_id;
                RETURN;
            END IF;
        EXCEPTION
            WHEN NO_DATA_FOUND THEN
                ROLLBACK;
                p_status := 'ERROR';
                p_error_message := 'Product not found: ' || v_product_id;
                RETURN;
        END;
        
        -- Calculate line total
        v_line_total := v_unit_price * v_quantity;
        v_total_amount := v_total_amount + v_line_total;
        
        -- Insert order item
        INSERT INTO order_items (
            item_id,
            order_id,
            product_id,
            quantity,
            unit_price,
            line_total,
            created_at
        ) VALUES (
            order_items_seq.NEXTVAL,
            v_order_id,
            v_product_id,
            v_quantity,
            v_unit_price,
            v_line_total,
            SYSTIMESTAMP
        );
    END LOOP;
    
    -- Update order total
    UPDATE orders
    SET total_amount = v_total_amount
    WHERE order_id = v_order_id;
    
    COMMIT;
    
    p_order_id := v_order_id;
    p_order_number := v_order_number;
    
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        p_status := 'ERROR';
        p_error_message := SQLERRM;
END SP_CREATE_ORDER;
/
