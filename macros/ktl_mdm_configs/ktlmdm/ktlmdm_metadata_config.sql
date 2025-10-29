{%- macro ktlmdm_metadata_config_yml() -%}
    {%- set config_map = {} -%}
    {%- set config_map = config_map | combine({
        'shb': shb_metadata_config_yml().get('KTL_MDM')
    }) -%}
    {{ return(config_map) }}
{%- endmacro -%}
