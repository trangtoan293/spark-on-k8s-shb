{{ config(materialized='view') }}
    
SELECT 
    CAST(order_id AS INTEGER) AS order_id,
    CAST(customer_id AS INTEGER) AS customer_id,
    CAST(order_date AS DATE) AS order_date,
    UPPER(TRIM(status)) AS status,
    CAST(amount AS DECIMAL(10,2)) AS amount,
    CURRENT_TIMESTAMP() AS loaded_at
FROM {{ ref('sample_orders') }}
WHERE order_id IS NOT NULL