{{ config(
    materialized='table'
) }}

SELECT 
    count(*) as total_customer,
    gender
FROM {{ ref('stg_customer') }}
group by gender