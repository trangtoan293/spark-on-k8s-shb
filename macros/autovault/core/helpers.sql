{# 
==============================================
Autovault Helper Macros
==============================================
Shared utility macros used across Hub, Satellite, and Link transformations.
#}

{%- macro get_source_reference(model) -%}
    {#
    Gets the source table reference for a model.
    Uses source() for batch processing.
    
    Args:
        model (dict): Model configuration from YAML
    
    Returns:
        Source table reference
    
    Example:
        {{ get_source_reference(model) }}
        -- Returns: source('source', 'corebank_customer')
    #}
    
    {%- set source_schema = model.get('source_schema', 'source') -%}
    {%- set source_table = model.get('source_table') -%}
    
    {{ source(source_schema, source_table) }}
{%- endmacro -%}


{%- macro get_hash_key_column(model, key_type='hash_key_hub') -%}
    {#
    Extracts hash key column configuration from model.
    
    Args:
        model (dict): Model configuration
        key_type (str): Type of hash key to extract
            Options: 'hash_key_hub', 'hash_key_sat', 'hash_key_lnk'
    
    Returns:
        Column configuration dict
    
    Example:
        {%- set hash_col = get_hash_key_column(model, 'hash_key_hub') -%}
        {{ hash_col.get('target') }}  -- dv_hkey_hub_customer
    #}
    
    {%- set column = model.get('columns') | selectattr('key_type', 'equalto', key_type) | first -%}
    {{ return(column) }}
{%- endmacro -%}


{%- macro get_biz_key_columns(model) -%}
    {#
    Extracts business key column configurations from model.
    
    Args:
        model (dict): Model configuration
    
    Returns:
        List of business key column configurations
    
    Example:
        {%- set biz_keys = get_biz_key_columns(model) -%}
        {%- for biz_key in biz_keys %}
            {{ biz_key.get('target') }}
        {%- endfor %}
    #}
    
    {%- set columns = model.get('columns') | selectattr('key_type', 'equalto', 'biz_key') | list -%}
    {{ return(columns) }}
{%- endmacro -%}


{%- macro get_attribute_columns(model) -%}
    {#
    Extracts attribute (non-key) columns from model.
    Used for Satellite descriptive data.
    
    Args:
        model (dict): Model configuration
    
    Returns:
        List of attribute column configurations
    
    Example:
        {%- set attrs = get_attribute_columns(model) -%}
    #}
    
    {%- set columns = model.get('columns') | selectattr('key_type', 'undefined') | list -%}
    {{ return(columns) }}
{%- endmacro -%}


{%- macro get_system_column_names(dv_system) -%}
    {#
    Extracts system column names from dv_system config.
    
    Args:
        dv_system (dict): System column configuration from dbt_project.yml
    
    Returns:
        List of system column target names
    
    Example:
        {%- set sys_cols = get_system_column_names(dv_system) -%}
        -- ['dv_kaf_ldt', 'dv_src_ldt', 'dv_cdc_ops', 'dv_ldt']
    #}
    
    {%- set column_names = dv_system.get('columns') | map(attribute='target') | list -%}
    {{ return(column_names) }}
{%- endmacro -%}


{%- macro get_ldt_column_names(dv_system) -%}
    {#
    Extracts load datetime column names from dv_system config.
    Used for deduplication ordering.
    
    Args:
        dv_system (dict): System column configuration
    
    Returns:
        List of LDT column names
    
    Example:
        {%- set ldt_cols = get_ldt_column_names(dv_system) -%}
        -- ['dv_kaf_ldt', 'dv_src_ldt']
    #}
    
    {%- set ldt_columns = [] -%}
    {%- for col in dv_system.get('columns') -%}
        {%- if 'ldt' in col.get('target').lower() -%}
            {%- do ldt_columns.append(col.get('target')) -%}
        {%- endif -%}
    {%- endfor -%}
    
    {{ return(ldt_columns) }}
{%- endmacro -%}


{%- macro get_collision_code(model) -%}
    {#
    Gets collision code from model configuration.
    
    Args:
        model (dict): Model configuration
    
    Returns:
        Collision code string
    
    Example:
        {%- set ccd = get_collision_code(model) -%}
        -- 'CORE'
    #}
    
    {{ return(model.get('collision_code')) }}
{%- endmacro -%}


{%- macro render_column_alias(source_col, target_name) -%}
    {#
    Renders a column with proper type casting and aliasing.
    
    Args:
        source_col (dict): Source column configuration
            {name: 'COL_NAME', dtype: 'string'}
        target_name (str): Target column name
    
    Returns:
        SQL expression with casting and alias
    
    Example:
        {{ render_column_alias(
            {'name': 'CUS_ID', 'dtype': 'int'},
            'CUSTOMER_ID'
        ) }}
        -- Returns: cast(CUS_ID as int) as CUSTOMER_ID
    #}
    
    {%- if source_col.get('name') == target_name and source_col.get('dtype') -%}
        {# No casting needed if name and type match #}
        {{ target_name }}
    {%- elif not source_col.get('dtype') -%}
        {# No dtype specified, just alias #}
        {{ source_col.get('name') }} as {{ target_name }}
    {%- else -%}
        {# Cast to target dtype #}
        cast({{ source_col.get('name') }} as {{ source_col.get('dtype') }}) as {{ target_name }}
    {%- endif -%}
{%- endmacro -%}
