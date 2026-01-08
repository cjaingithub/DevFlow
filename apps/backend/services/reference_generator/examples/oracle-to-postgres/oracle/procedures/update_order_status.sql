-- Update Order Status Stored Procedure
-- =====================================
--
-- Updates order status with validation of allowed transitions.

CREATE OR REPLACE PROCEDURE SP_UPDATE_ORDER_STATUS (
    p_order_id       IN NUMBER,
    p_new_status     IN VARCHAR2,
    p_updated_by     IN VARCHAR2 DEFAULT NULL,
    p_success        OUT NUMBER,  -- 1 = success, 0 = failure
    p_error_message  OUT VARCHAR2
) AS
    v_current_status VARCHAR2(20);
    v_valid_transition NUMBER := 0;
BEGIN
    p_success := 1;
    p_error_message := NULL;
    
    -- Get current status
    BEGIN
        SELECT status INTO v_current_status
        FROM orders
        WHERE order_id = p_order_id;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            p_success := 0;
            p_error_message := 'Order not found: ' || p_order_id;
            RETURN;
    END;
    
    -- Validate status transition
    -- PENDING -> CONFIRMED, CANCELLED
    -- CONFIRMED -> SHIPPED, CANCELLED
    -- SHIPPED -> DELIVERED
    -- DELIVERED -> (none)
    -- CANCELLED -> (none)
    
    CASE v_current_status
        WHEN 'PENDING' THEN
            IF p_new_status IN ('CONFIRMED', 'CANCELLED') THEN
                v_valid_transition := 1;
            END IF;
        WHEN 'CONFIRMED' THEN
            IF p_new_status IN ('SHIPPED', 'CANCELLED') THEN
                v_valid_transition := 1;
            END IF;
        WHEN 'SHIPPED' THEN
            IF p_new_status = 'DELIVERED' THEN
                v_valid_transition := 1;
            END IF;
        ELSE
            v_valid_transition := 0;
    END CASE;
    
    IF v_valid_transition = 0 THEN
        p_success := 0;
        p_error_message := 'Invalid status transition: ' || v_current_status || ' -> ' || p_new_status;
        RETURN;
    END IF;
    
    -- Update the status
    UPDATE orders
    SET status = p_new_status,
        updated_at = SYSTIMESTAMP
    WHERE order_id = p_order_id;
    
    -- If cancelling, restore stock
    IF p_new_status = 'CANCELLED' THEN
        FOR item IN (
            SELECT product_id, quantity
            FROM order_items
            WHERE order_id = p_order_id
        ) LOOP
            UPDATE products
            SET stock_quantity = stock_quantity + item.quantity
            WHERE product_id = item.product_id;
        END LOOP;
    END IF;
    
    COMMIT;
    
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        p_success := 0;
        p_error_message := SQLERRM;
END SP_UPDATE_ORDER_STATUS;
/
