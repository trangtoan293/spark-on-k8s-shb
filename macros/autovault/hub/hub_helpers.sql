{# 
==============================================
Hub Helper Macros
==============================================
Helper functions for Hub transformation to break down complexity.
#}

{%- macro build_hub_source_select(model, dv_system) -%}
    {#
    Builds the SELECT clause for Hub source CTE.
    
    Returns all columns needed for Hub:
        - Hash key (generated from business keys)
        - Business keys (with casting/aliasing)
        - System columns (CDC timestamps, etc.)
        - Collision code
    
    Args:
        model (dict): Hub configuration
        dv_system (dict): System column configuration
    
    Returns:
        SQL SELECT clause (columns only, no SELECT keyword)
    #}
    
    {# Hash key generation #}
    {{ generate_hash_key_hub(model) }},
    
    {# Business keys with proper casting #}
    {%- set biz_keys = get_biz_key_columns(model) -%}
    {%- for biz_key in biz_keys %}
        {%- set source_col = biz_key.get('source') -%}
        {%- set target_name = biz_key.get('target') -%}
        
        {%- if biz_key.get('dtype') == 'string' -%}
            {# String business keys are normalized (same as hash input) #}
            {{ normalize_column_for_hash(source_col.get('name'), upper=True) }} as {{ target_name }},
        {%- else -%}
            {# Non-string business keys just cast #}
            {{ render_column_alias(source_col, target_name) }},
        {%- endif -%}
    {%- endfor %}
    
    {# System columns (timestamps, CDC ops, etc.) #}
    {%- for sys_col in dv_system.get('columns') %}
        {%- set source = sys_col.get('source') -%}
        {%- set target = sys_col.get('target') -%}
        {{ render_column_alias(source, target) }},
    {%- endfor %}
    
    {# Collision code #}
    '{{ get_collision_code(model) }}' as {{ dv_collision_code_column() }}
{%- endmacro -%}


{%- macro build_hub_source_where(model) -%}
    {#
    Builds the WHERE clause to filter null business keys.
    
    In Data Vault, we cannot have null business keys in Hub.
    This ensures all source columns used in hash are not null.
    
    Args:
        model (dict): Hub configuration
    
    Returns:
        SQL WHERE clause
    
    Example:
        WHERE 1 = 1
            AND customer_id IS NOT NULL
            AND account_id IS NOT NULL
    #}
    
    {%- set hash_col = get_hash_key_column(model, 'hash_key_hub') -%}
    {%- set source = hash_col.get('source') -%}
    
    WHERE 1 = 1
    {%- if source is iterable and source is not string -%}
        {%- for src_col in source %}
            AND {{ src_col }} IS NOT NULL
        {%- endfor %}
    {%- endif -%}
{%- endmacro -%}


{%- macro build_hub_dedup_window(hash_key_name, ldt_columns) -%}
    {#
    Builds window function for deduplication.
    
    Keep only the EARLIEST record per hash key based on load timestamps.
    This follows Data Vault 2.0 standard: first appearance wins.
    
    Args:
        hash_key_name (str): Name of the hash key column
        ldt_columns (list): List of load timestamp column names for ordering
    
    Returns:
        SQL window function expression
    
    Example:
        row_number() over (
            partition by dv_hkey_hub_customer
            order by dv_kaf_ldt asc, dv_src_ldt asc
        ) as row_num
    #}
    
    row_number() over (
        partition by {{ hash_key_name }}
        order by
            {%- for ldt in ldt_columns %}
                {{ ldt }} asc{{ ',' if not loop.last }}
            {%- endfor %}
    ) as row_num
{%- endmacro -%}


{%- macro build_hub_final_select(model, dv_system) -%}
    {#
    Builds the final SELECT clause for Hub output.
    
    Returns:
        - Hash key
        - Business keys
        - System columns
        - Collision code
    
    Args:
        model (dict): Hub configuration
        dv_system (dict): System column configuration
    
    Returns:
        SQL SELECT clause
    #}
    
    SELECT
        {%- set hash_col = get_hash_key_column(model, 'hash_key_hub') %}
        {{ hash_col.get('target') }},
        
        {%- set biz_keys = get_biz_key_columns(model) %}
        {%- for biz_key in biz_keys %}
            {{ biz_key.get('target') }},
        {%- endfor %}
        
        {%- set sys_cols = get_system_column_names(dv_system) %}
        {%- for sys_col in sys_cols %}
            {{ sys_col }},
        {%- endfor %}
        
        {{ dv_collision_code_column() }}
    
    FROM deduplicated
{%- endmacro -%}
