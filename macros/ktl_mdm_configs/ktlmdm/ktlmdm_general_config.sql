{%- macro ktlmdm_general_config_yml() -%}
    {%- set config_map = {
        'run_date_config': {
            'cob_date': None
        }
    } -%}
    {{ return(config_map) }}
{%- endmacro -%}
