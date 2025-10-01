{# 
==============================================
Hash Key Generation
==============================================
SHA-256 hash key generation for Data Vault entities.

⚠️ CRITICAL: This logic is COPIED EXACTLY from derive_columns.sql
DO NOT modify unless absolutely necessary as it affects existing data.
#}

{%- macro generate_hash_key_hub(model) -%}
    {#
    Generates Hub hash key.
    
    ⚠️ EXACT COPY of render_hash_key_hub_treatment() logic from derive_columns.sql
    
    Args:
        model (dict): Hub model configuration
    
    Returns:
        SQL expression: sha2(...) as hash_key_name
    
    Example:
        {{ generate_hash_key_hub(model) }}
        -- Returns: sha2(coalesce(...) || '#~!' || 'CORE', 256) as dv_hkey_hub_customer
    #}
    
    {%- set column = model.get('columns') | selectattr("key_type", "equalto", "hash_key_hub") | first -%}
    {%- set collision_code = model.get('collision_code') -%}
    {%- set hash_string = build_hash_string_from_columns([column], collision_code) -%}
    
    sha2({{ hash_string }}, 256) as {{ column.get('target') }}
{%- endmacro -%}


{%- macro generate_hash_key_sat(model, dv_system) -%}
    {#
    Generates Satellite hash key.
    
    ⚠️ EXACT COPY of render_hash_key_sat_treatment() logic from derive_columns.sql
    
    Components:
        1. Hub hash key columns
        2. Dependent key columns
        3. System columns: dv_src_ldt, dv_kaf_ldt, dv_kaf_ofs
    
    Args:
        model (dict): Satellite model configuration
        dv_system (dict): System column configuration
    
    Returns:
        SQL expression: sha2(...) as hash_key_sat_name
    
    Example:
        {{ generate_hash_key_sat(model, dv_system) }}
    #}
    
    {# Collect all columns for hash #}
    {%- set columns = model.get('columns') | selectattr("key_type", "equalto", "hash_key_hub") | list -%}
    
    {# Add dependent keys if any #}
    {%- do columns.extend(model.get('columns') | selectattr("key_type", "equalto", "dependent_key") | list) -%}
    
    {# Add system columns #}
    {%- for key in ('dv_src_ldt', 'dv_kaf_ldt', 'dv_kaf_ofs') -%}
        {%- do columns.append(dv_system.get('columns') | selectattr('target', 'equalto', key) | first) -%}
    {%- endfor -%}
    
    {%- set target = (model.get('columns') | selectattr("key_type", "equalto", "hash_key_sat") | first).get('target') -%}
    {%- set collision_code = model.get('collision_code') -%}
    {%- set hash_string = build_hash_string_from_columns(columns, collision_code) -%}
    
    sha2({{ hash_string }}, 256) as {{ target }}
{%- endmacro -%}


{%- macro generate_hash_key_lnk(model) -%}
    {#
    Generates Link hash key.
    
    ⚠️ EXACT COPY of render_hash_key_lnk_treatment() logic from derive_columns.sql
    
    Args:
        model (dict): Link model configuration
    
    Returns:
        SQL expression: sha2(...) as hash_key_lnk_name
    #}
    
    {%- set column = model.get('columns') | selectattr("key_type", "equalto", "hash_key_lnk") | first -%}
    {%- set collision_code = model.get('collision_code') -%}
    {%- set hash_string = build_hash_string_from_columns([column], collision_code) -%}
    
    sha2({{ hash_string }}, 256) as {{ column.get('target') }}
{%- endmacro -%}


{%- macro generate_hash_key_lsat(model, dv_system) -%}
    {#
    Generates Link-Satellite hash key.
    
    ⚠️ EXACT COPY of render_hash_key_lsat_treatment() logic from derive_columns.sql
    
    Components:
        1. Link hash key columns
        2. Dependent key columns
        3. System columns: dv_src_ldt, dv_kaf_ldt, dv_kaf_ofs
    
    Args:
        model (dict): Link-Satellite model configuration
        dv_system (dict): System column configuration
    
    Returns:
        SQL expression: sha2(...) as hash_key_lsat_name
    #}
    
    {# Collect all columns for hash #}
    {%- set columns = model.get('columns') | selectattr("key_type", "equalto", "hash_key_lnk") | list -%}
    
    {# Add dependent keys if any #}
    {%- do columns.extend(model.get('columns') | selectattr("key_type", "equalto", "dependent_key") | list) -%}
    
    {# Add system columns #}
    {%- for key in ('dv_src_ldt', 'dv_kaf_ldt', 'dv_kaf_ofs') -%}
        {%- do columns.append(dv_system.get('columns') | selectattr('target', 'equalto', key) | first) -%}
    {%- endfor -%}
    
    {%- set target = (model.get('columns') | selectattr("key_type", "equalto", "hash_key_sat") | first).get('target') -%}
    {%- set collision_code = model.get('collision_code') -%}
    {%- set hash_string = build_hash_string_from_columns(columns, collision_code) -%}
    
    sha2({{ hash_string }}, 256) as {{ target }}
{%- endmacro -%}


{%- macro generate_hash_diff(model) -%}
    {#
    Generates hash diff for Satellite change detection.
    
    ⚠️ EXACT COPY of render_hash_diff_treatment() logic from derive_columns.sql
    
    Process:
        1. Get hash_diff column config
        2. If no source specified, auto-extract from attribute columns
        3. Build hash from attribute column values
        4. Use different error_code: repeat('0', 16) instead of '-1'
    
    Args:
        model (dict): Satellite model configuration
    
    Returns:
        SQL expression: sha2(...) as hash_diff_name
    
    Example:
        {{ generate_hash_diff(model) }}
        -- Returns: sha2(coalesce(...) || '#~!' || coalesce(...), 256) as dv_hsh_dif
    #}
    
    {%- set column = model.get('columns') | selectattr("key_type", "equalto", "hash_diff") | first -%}
    
    {# Auto-extract attribute columns if source not specified #}
    {%- if 'source' not in column -%}
        {%- set column = column.copy() -%}
        {%- do column.update({'source': []}) -%}
        {%- for attr_column in model.get('columns') | selectattr('key_type', 'undefined') -%}
            {%- do column.get('source').append(attr_column.get('source').get('name')) -%}
        {%- endfor -%}
    {%- endif -%}
    
    {# Build hash with different error code #}
    {%- set parts = [] -%}
    {%- for source_column in column.get('source') -%}
        {%- do parts.append(normalize_column_for_hash(source_column, error_code="repeat('0', 16)")) -%}
    {%- endfor -%}
    
    sha2({{ parts | join(" || '#~!' || ") }}, 256) as {{ column.get('target') }}
{%- endmacro -%}


{%- macro generate_hash_key_drv(model) -%}
    {#
    Generates Derived Hub/Link hash key.
    
    ⚠️ EXACT COPY of render_hash_key_drv_treatment() logic from derive_columns.sql
    
    Args:
        model (dict): Model configuration with hash_key_drv
    
    Returns:
        SQL expression: sha2(...) as hash_key_drv_name
    #}
    
    {%- set column = model.get('columns') | selectattr("key_type", "equalto", "hash_key_drv") | first -%}
    {%- set collision_code = model.get('collision_code') -%}
    {%- set hash_string = build_hash_string_from_columns([column], collision_code) -%}
    
    sha2({{ hash_string }}, 256) as {{ column.get('target') }}
{%- endmacro -%}
