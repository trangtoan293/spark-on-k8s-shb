{# 
==============================================
Hash Normalization Functions
==============================================
Column normalization for consistent hash generation.

⚠️ CRITICAL: This logic is COPIED EXACTLY from derive_columns.sql
DO NOT modify unless absolutely necessary as it affects existing hash keys.
#}

{%- macro normalize_column_for_hash(source_column, error_code="'-1'", upper=False) -%}
    {#
    Normalizes a column value for hash generation.
    
    ⚠️ EXACT COPY of _render_hash_component_transformation() from derive_columns.sql
    
    Process:
        1. Cast to string
        2. Optionally uppercase  
        3. Trim whitespace (rtrim)
        4. Replace empty string with null (nullif)
        5. Replace null with error_code (coalesce)
    
    Args:
        source_column (str): Column name or expression
        error_code (str): Replacement for null/empty (default: '-1')
        upper (bool): Convert to uppercase (default: false)
    
    Returns:
        SQL expression with normalization
    
    Example:
        {{ normalize_column_for_hash('customer_id', upper=true) }}
        -- Returns: coalesce(nullif(rtrim(upper(cast(customer_id as string))), ''), '-1')
    
    Hash Impact:
        - Used in ALL hash key generation
        - ANY change breaks existing hash keys
        - Test thoroughly before modifying
    #}
    
    {%- if upper -%}
        coalesce(nullif(rtrim(upper(cast({{ source_column }} as string))), ''), {{ error_code }})
    {%- else -%}
        coalesce(nullif(rtrim(cast({{ source_column }} as string)), ''), {{ error_code }})
    {%- endif -%}
{%- endmacro -%}


{%- macro build_hash_string_from_columns(columns, collision_code) -%}
    {#
    Builds the concatenated string for hash input.
    
    ⚠️ EXACT COPY of logic from _render_hash_key_transformation() in derive_columns.sql
    
    Process:
        1. For each column config:
           - If source is mapping: normalize without uppercase
           - If source is list: normalize each with uppercase
        2. Join with separator '||' and '#~!' delimiter
        3. Append collision code
    
    Args:
        columns (list): List of column configurations
        collision_code (str): Source system identifier
    
    Returns:
        SQL expression for concatenated string (without sha2 wrapper)
    
    Example:
        {{ build_hash_string_from_columns(columns, 'CORE') }}
        -- Returns: coalesce(...) || '#~!' || coalesce(...) || '#~!' || 'CORE'
    
    Hash Impact:
        - Separator '#~!' is CRITICAL
        - Order of columns matters
        - DO NOT change without testing
    #}
    
    {%- set parts = [] -%}
    
    {%- for column in columns -%}
        {%- set source = column.get('source') -%}
        
        {%- if source is mapping -%}
            {# Single column from mapping: {name: 'COL', dtype: 'string'} #}
            {%- do parts.append(normalize_column_for_hash(source.get('name'), upper=False)) -%}
            
        {%- elif source is iterable and source is not string -%}
            {# Multiple columns from list: ['COL1', 'COL2'] #}
            {%- for source_column in source -%}
                {%- do parts.append(normalize_column_for_hash(source_column, upper=True)) -%}
            {%- endfor -%}
        {%- endif -%}
    {%- endfor -%}
    
    {# Join parts with separator and add collision code #}
    {%- set separator = dv_hash_separator() -%}
    {{ parts | join(" || '" ~ separator ~ "' || ") }} || '{{ separator }}' || '{{ collision_code }}'
{%- endmacro -%}
