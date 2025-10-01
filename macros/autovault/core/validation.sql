{# 
==============================================
Autovault Config Validation
==============================================
Validates YAML configurations before processing to provide helpful error messages.
#}

{%- macro validate_hub_config(model) -%}
    {#
    Validates Hub YAML configuration structure.
    
    Args:
        model (dict): Hub configuration from YAML
    
    Raises:
        CompilerError if required fields are missing
    
    Returns:
        true if validation passes
    #}
    
    {# Check required top-level fields #}
    {%- set required_fields = ['target_schema', 'target_table', 'target_entity_type'] -%}
    {%- for field in required_fields -%}
        {%- if field not in model -%}
            {{ exceptions.raise_compiler_error(
                "Hub config validation failed: Missing required field '" ~ field ~ "' in " ~ 
                model.get('target_table', 'unknown table')
            ) }}
        {%- endif -%}
    {%- endfor -%}
    
    {# Validate entity type #}
    {%- if model.get('target_entity_type') != 'hub' -%}
        {{ exceptions.raise_compiler_error(
            "Hub config validation failed: Expected entity_type='hub', got '" ~ 
            model.get('target_entity_type') ~ "'"
        ) }}
    {%- endif -%}
    
    {# Validate has columns #}
    {%- if 'columns' not in model or model.get('columns') | length == 0 -%}
        {{ exceptions.raise_compiler_error(
            "Hub config validation failed: Missing 'columns' in " ~ model.get('target_table')
        ) }}
    {%- endif -%}
    
    {# Validate has hash_key_hub #}
    {%- set hash_key_cols = model.get('columns') | selectattr('key_type', 'equalto', 'hash_key_hub') | list -%}
    {%- if hash_key_cols | length == 0 -%}
        {{ exceptions.raise_compiler_error(
            "Hub config validation failed: No hash_key_hub column defined in " ~ model.get('target_table')
        ) }}
    {%- endif -%}
    
    {# Validate has biz_key #}
    {%- set biz_key_cols = model.get('columns') | selectattr('key_type', 'equalto', 'biz_key') | list -%}
    {%- if biz_key_cols | length == 0 -%}
        {{ exceptions.raise_compiler_error(
            "Hub config validation failed: No biz_key column defined in " ~ model.get('target_table')
        ) }}
    {%- endif -%}
    
    {# Validate has collision_code #}
    {%- if 'collision_code' not in model -%}
        {{ exceptions.raise_compiler_error(
            "Hub config validation failed: Missing 'collision_code' in " ~ model.get('target_table')
        ) }}
    {%- endif -%}
    
    {{ return(true) }}
{%- endmacro -%}


{%- macro validate_sat_config(model) -%}
    {#
    Validates Satellite YAML configuration structure.
    
    Args:
        model (dict): Satellite configuration from YAML
    
    Raises:
        CompilerError if required fields are missing
    
    Returns:
        true if validation passes
    #}
    
    {# Check required fields #}
    {%- set required_fields = ['target_schema', 'target_table', 'target_entity_type', 'parent_table'] -%}
    {%- for field in required_fields -%}
        {%- if field not in model -%}
            {{ exceptions.raise_compiler_error(
                "Satellite config validation failed: Missing required field '" ~ field ~ "' in " ~ 
                model.get('target_table', 'unknown table')
            ) }}
        {%- endif -%}
    {%- endfor -%}
    
    {# Validate entity type #}
    {%- if model.get('target_entity_type') != 'sat' -%}
        {{ exceptions.raise_compiler_error(
            "Satellite config validation failed: Expected entity_type='sat', got '" ~ 
            model.get('target_entity_type') ~ "'"
        ) }}
        {%- endif -%}
    
    {# Validate has columns #}
    {%- if 'columns' not in model or model.get('columns') | length == 0 -%}
        {{ exceptions.raise_compiler_error(
            "Satellite config validation failed: Missing 'columns' in " ~ model.get('target_table')
        ) }}
    {%- endif -%}
    
    {# Validate has hash_key_hub (parent reference) #}
    {%- set hash_key_cols = model.get('columns') | selectattr('key_type', 'equalto', 'hash_key_hub') | list -%}
    {%- if hash_key_cols | length == 0 -%}
        {{ exceptions.raise_compiler_error(
            "Satellite config validation failed: No hash_key_hub column defined in " ~ model.get('target_table')
        ) }}
    {%- endif -%}
    
    {# Validate has hash_diff #}
    {%- set hash_diff_cols = model.get('columns') | selectattr('key_type', 'equalto', 'hash_diff') | list -%}
    {%- if hash_diff_cols | length == 0 -%}
        {{ exceptions.raise_compiler_error(
            "Satellite config validation failed: No hash_diff column defined in " ~ model.get('target_table')
        ) }}
    {%- endif -%}
    
    {{ return(true) }}
{%- endmacro -%}


{%- macro validate_lnk_config(model) -%}
    {#
    Validates Link YAML configuration structure.
    
    Args:
        model (dict): Link configuration from YAML
    
    Raises:
        CompilerError if required fields are missing
    
    Returns:
        true if validation passes
    #}
    
    {# Check required fields #}
    {%- set required_fields = ['target_schema', 'target_table', 'target_entity_type'] -%}
    {%- for field in required_fields -%}
        {%- if field not in model -%}
            {{ exceptions.raise_compiler_error(
                "Link config validation failed: Missing required field '" ~ field ~ "' in " ~ 
                model.get('target_table', 'unknown table')
            ) }}
        {%- endif -%}
    {%- endfor -%}
    
    {# Validate entity type #}
    {%- if model.get('target_entity_type') != 'lnk' -%}
        {{ exceptions.raise_compiler_error(
            "Link config validation failed: Expected entity_type='lnk', got '" ~ 
            model.get('target_entity_type') ~ "'"
        ) }}
    {%- endif -%}
    
    {# Validate has hash_key_lnk #}
    {%- set hash_key_cols = model.get('columns') | selectattr('key_type', 'equalto', 'hash_key_lnk') | list -%}
    {%- if hash_key_cols | length == 0 -%}
        {{ exceptions.raise_compiler_error(
            "Link config validation failed: No hash_key_lnk column defined in " ~ model.get('target_table')
        ) }}
    {%- endif -%}
    
    {{return(true) }}
{%- endmacro -%}
