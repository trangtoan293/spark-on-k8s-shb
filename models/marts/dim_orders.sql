{{ config(
    materialized='table',
    file_format='parquet'
) }}

SELECT 
    order_id,
    customer_id,
    order_date,
    status,
    amount,
    CASE 
        WHEN amount >= 100 THEN 'High Value'
        WHEN amount >= 50 THEN 'Medium Value'
        ELSE 'Low Value'
    END AS order_category,
    loaded_at
FROM {{ ref('stg_orders') }}