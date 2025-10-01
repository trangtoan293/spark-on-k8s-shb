{# 
==============================================
Autovault Config Loader
==============================================
Centralized configuration loading for Data Vault models.
Automatically loads YAML configs based on model name.
#}

{%- macro load_autovault_config(entity_type, entity_name) -%}
    {#
    Loads Autovault configuration from centralized YAML configs.
    
    **Purpose:**
    - Eliminates need for individual var() definitions per model
    - Centralizes all configs in dbt_project.yml
    - Auto-discovers config based on entity type and name
    
    **Args:**
        entity_type (str): Type of entity ('hub', 'sat', 'lnk', 'lsat')
        entity_name (str): Name of entity (e.g., 'customer', 'account')
    
    **Returns:**
        dict: Parsed YAML configuration
    
    **Usage:**
        ```sql
        -- models/hub_customer.sql
        {{ hub_transform(
            model=load_autovault_config('hub', 'customer'),
            dv_system=var('dv_system')
        ) }}
        ```
    
    **Config Structure in dbt_project.yml:**
        ```yaml
        vars:
          autovault_configs:
            hub:
              customer:
                target_schema: raw_vault
                target_table: hub_customer
                ...
              account:
                target_schema: raw_vault
                target_table: hub_account
                ...
            sat:
              customer_details:
                ...
        ```
    
    **Alternative: Load from File**
        If you prefer separate YAML files:
        ```yaml
        vars:
          autovault_config_path: 'ktl_autovault_configs'
        ```
        
        Then this macro will look for:
        `ktl_autovault_configs/hub/customer.yml`
    #}
    
    {# Try to load from centralized config first #}
    {%- set all_configs = var('autovault_configs', none) -%}
    
    {%- if all_configs is not none -%}
        {# Load from dbt_project.yml vars #}
        {%- set entity_configs = all_configs.get(entity_type, {}) -%}
        {%- set config = entity_configs.get(entity_name, none) -%}
        
        {%- if config is none -%}
            {{ exceptions.raise_compiler_error(
                "Autovault config not found: " ~ entity_type ~ "." ~ entity_name ~ 
                "\nExpected in vars.autovault_configs." ~ entity_type ~ "." ~ entity_name
            ) }}
        {%- endif -%}
        
        {{ return(config) }}
    
    {%- else -%}
        {# Fallback: Try individual var #}
        {%- set var_name = entity_type ~ '_' ~ entity_name ~ '_config' -%}
        {%- set config = var(var_name, none) -%}
        
        {%- if config is none -%}
            {{ exceptions.raise_compiler_error(
                "Autovault config not found: " ~ var_name ~ 
                "\nEither define vars.autovault_configs or vars." ~ var_name
            ) }}
        {%- endif -%}
        
        {# Parse if it's a YAML string #}
        {%- if config is string -%}
            {{ return(fromyaml(config)) }}
        {%- else -%}
            {{ return(config) }}
        {%- endif -%}
    {%- endif -%}
{%- endmacro -%}


{%- macro get_dv_system_config() -%}
    {#
    Gets Data Vault system column configuration.
    
    **Returns:**
        dict: System column configuration
    
    **Usage:**
        ```sql
        {{ hub_transform(
            model=load_autovault_config('hub', 'customer'),
            dv_system=get_dv_system_config()
        ) }}
        ```
    #}
    
    {%- set config = var('dv_system', none) -%}
    
    {%- if config is none -%}
        {{ exceptions.raise_compiler_error(
            "Data Vault system config not found.\n" ~
            "Define vars.dv_system in dbt_project.yml"
        ) }}
    {%- endif -%}
    
    {{ return(config) }}
{%- endmacro -%}


{%- macro autovault(entity_type, entity_name) -%}
    {#
    **SHORTHAND MACRO** - One-liner for Autovault models.
    
    Automatically:
    - Loads config for entity
    - Loads system config
    - Calls appropriate transform macro
    
    **Args:**
        entity_type (str): 'hub', 'sat', 'lnk', or 'lsat'
        entity_name (str): Entity name (e.g., 'customer')
    
    **Usage:**
        ```sql
        -- models/hub_customer.sql
        {{ autovault('hub', 'customer') }}
        
        -- models/sat_customer_details.sql
        {{ autovault('sat', 'customer_details') }}
        
        -- models/lnk_customer_account.sql
        {{ autovault('lnk', 'customer_account') }}
        ```
    
    **That's it! No need to specify model= or dv_system=**
    #}
    
    {%- set model = load_autovault_config(entity_type, entity_name) -%}
    {%- set dv_system = get_dv_system_config() -%}
    
    {%- if entity_type == 'hub' -%}
        {{ hub_transform(model, dv_system) }}
    
    {%- elif entity_type == 'sat' -%}
        {{ sat_transform(model, dv_system) }}
    
    {%- elif entity_type == 'lnk' -%}
        {{ lnk_transform(model, dv_system) }}
    
    {%- elif entity_type == 'lsat' -%}
        {{ lsat_transform(model, dv_system) }}
    
    {%- else -%}
        {{ exceptions.raise_compiler_error(
            "Unknown entity type: " ~ entity_type ~ 
            "\nSupported: hub, sat, lnk, lsat"
        ) }}
    {%- endif -%}
{%- endmacro -%}
