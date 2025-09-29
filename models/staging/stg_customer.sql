{{ config(materialized='view') }}
    
SELECT 
    CST_NO as customer_id,
    CST_NM as customer_name,
    CREATE_DT as created_at,
    case when SEX = 'M' then 'Male' else 'Female' end as gender,
    ID_NUMBER as id_number,
    TYPE_OF_ID as id_type,
    DATE_OF_ISSUE as id_issue_date,
    MAIL_TYPCD as mail_address,
    current_timestamp() as loaded_at,
    current_date() as updated_at
FROM {{ source('raw_data', 'customers_stream_test0000') }}
where 1=1 
