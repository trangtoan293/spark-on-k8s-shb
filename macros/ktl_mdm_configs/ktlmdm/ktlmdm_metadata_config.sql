{%- macro ktlmdm_metadata_config_yml() -%}
    {%- set config_map = {
        'KTL_MDM': shb_metadata_config_yml().get('KTL_MDM')
    } -%}
    {{ return(config_map) }}
{%- endmacro -%}
