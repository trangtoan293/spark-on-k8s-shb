{# 
==============================================
Autovault Constants
==============================================
Centralized constants for Data Vault automation.
These values are used across all hash generation and column transformation macros.
#}

{%- macro dv_hash_separator() -%}
    {#
    Hash component separator - used between fields in hash concatenation.
    ⚠️ CRITICAL: Value '#~!' is hard-coded in original implementation.
    DO NOT CHANGE - will break all existing hash keys!
    Value: '#~!'
    Used in: Hash key generation for Hub, Link, Satellite
    #}
    {{ return('#~!') }}
{%- endmacro -%}


{%- macro dv_null_value() -%}
    {#
    Standard replacement for NULL or empty values in hash generation.
    Value: '-1'
    Used in: Business key normalization
    #}
    {{ return('-1') }}
{%- endmacro -%}


{%- macro dv_hash_error_value() -%}
    {#
    Error value for hash diff generation.
    Value: repeat('0', 16)
    Used in: Hash diff calculation for Satellites
    #}
    {{ return("repeat('0', 16)") }}
{%- endmacro -%}


{%- macro dv_hash_algorithm() -%}
    {#
    Hash algorithm configuration.
    Function: sha2
    Bits: 256 (SHA-256)
    
    Returns: {function: 'sha2', bits: 256}
    #}
    {{ return({'function': 'sha2', 'bits': 256}) }}
{%- endmacro -%}


{%- macro dv_collision_code_column() -%}
    {#
    Standard name for collision code column.
    Value: 'dv_ccd'
    #}
    {{ return('dv_ccd') }}
{%- endmacro -%}
