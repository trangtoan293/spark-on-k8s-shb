{%- macro ktlmdm_general_config_yml() -%}
    {%- set config_map = {
        'KTL_MDM': {
            'run_date_config': {
                'cob_date': None
            }
        }
    } -%}
    {{ return(config_map) }}
{%- endmacro -%}
