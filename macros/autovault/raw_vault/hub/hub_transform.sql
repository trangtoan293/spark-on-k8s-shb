{# 
==============================================
Hub Transformation Macro - REFACTORED
==============================================
Generates Data Vault Hub tables from YAML configuration.
Batch/incremental processing only (no streaming).
#}

{%- macro hub_transform(model, dv_system) -%}
    {#
    **Hub Transformation - Batch Processing**
    
    Generates a Data Vault Hub table with:
        - SHA-256 hash keys from business keys
        - Business key columns
        - System columns (timestamps, CDC operations)
        - Collision code for source identification
    
    **Data Vault Logic:**
        1. Extract source data with all required columns
        2. Filter out records with null business keys
        3. Deduplicate by hash key (keep earliest record)
        4. Output unique Hub records
    
    **Args:**
        model (dict): Hub configuration from YAML file
            Required fields:
                - target_schema: Target schema name
                - target_table: Target table name
                - target_entity_type: Must be 'hub'
                - collision_code: Source system identifier (e.g. 'CORE', 'CARD')
                - source_schema: Source schema (default: 'source')
                - source_table: Source table name
                - columns: List of column configurations
                    Each column needs:
                        - key_type: 'hash_key_hub' or 'biz_key'
                        - source: Column name or list of names
                        - target: Target column name
                        - dtype: Data type
        
        dv_system (dict): System column configuration from dbt_project.yml
            Contains definitions for:
                - dv_kaf_ldt: Kafka load datetime
                - dv_src_ldt: Source load datetime
                - dv_cdc_ops: CDC operation type
                - dv_ccd: Collision code
    
    **Returns:**
        SQL query for Hub table creation with incremental materialization
    
    **YAML Config Example:**
        ```yaml
        target_schema: raw_vault
        target_table: hub_customer
        target_entity_type: hub
        collision_code: CORE
        source_schema: source
        source_table: corebank_customer
        columns:
          - key_type: hash_key_hub
            source: [CUSTOMER_ID]  # List for composite keys
            target: dv_hkey_hub_customer
            dtype: string
          - key_type: biz_key
            source:
              name: CUSTOMER_ID
              dtype: int
            target: CUSTOMER_ID
            dtype: int
        ```
    
    **Usage:**
        ```sql
        -- models/raw_vault/hub_customer.sql
        {{ hub_transform(
            model=fromyaml(var('hub_customer_config')),
            dv_system=var('dv_system')
        ) }}
        ```
    
    **Important Notes:**
        - Hash generation logic MUST NOT be modified (affects existing data)
        - Deduplication keeps EARLIEST record per hash key
        - Business keys cannot be null
        - Incremental loads append new hash keys only
    #}
    
    {# Validate configuration before processing #}
    {{ validate_hub_config(model) }}
    
    {# Configure as incremental table (batch processing) #}
    {{ config(materialized='incremental', unique_key=get_hash_key_column(model, 'hash_key_hub').get('target')) }}
    
    {# Extract metadata for processing #}
    {%- set hash_col = get_hash_key_column(model, 'hash_key_hub') -%}
    {%- set hash_key_name = hash_col.get('target') -%}
    {%- set ldt_columns = get_ldt_column_names(dv_system) -%}
    
    {# 
    ========================================
    CTE 1: Source Data Extraction
    ========================================
    Extract all required columns from source:
        - Generate hash key from business keys
        - Cast business keys to target types
        - Include system columns (timestamps, CDC)
        - Add collision code
        - Filter out null business keys
    #}
    WITH source_data AS (
        SELECT
            {{ build_hub_source_select(model, dv_system) }}
        FROM {{ get_source_reference(model) }}
        {{ build_hub_source_where(model) }}
    ),
    
    {# 
    ========================================
    CTE 2: Deduplication
    ========================================
    Keep only the earliest record per hash key.
    Data Vault rule: First appearance wins.
    Uses window function with load timestamps for ordering.
    #}
    deduplicated AS (
        SELECT *
        FROM (
            SELECT
                *,
                {{ build_hub_dedup_window(hash_key_name, ldt_columns) }}
            FROM source_data
        )
        WHERE row_num = 1
    )
    
    {# 
    ========================================
    Final Output
    ========================================
    Select all Hub columns.
    For incremental runs, dbt automatically handles new records.
    #}
    {{ build_hub_final_select(model, dv_system) }}

{%- endmacro -%}
