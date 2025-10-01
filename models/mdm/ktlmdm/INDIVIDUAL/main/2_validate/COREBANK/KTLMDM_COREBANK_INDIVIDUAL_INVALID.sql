{{
    config(
        pre_hook = [
            "DROP TABLE {{this}} purge",
        ]
    )
}}


{%-set project = 'KTLMDM' -%}
{%-set product = 'INDIVIDUAL' -%}
{%-set source = 'COREBANK' -%}

{%- set general_conf = ktl_mdm_utils_get_general_config(project) -%}
{%- set metadata_conf = ktl_mdm_utils_metadata_get_metadata_config(project,product,source) -%}

{# get info column apply using rule cleansing #}
{%- set rule_apply = ktl_mdm_utils_get_rule_field_apply_config(project_name = project, product = product, source = source, component='validate')-%}

{%- set table_source = ref('KTLMDM_COREBANK_INDIVIDUAL_CLEANSING') -%}

{{ ktl_mdm_validate_invalid(general_conf, metadata_conf, rule_apply = rule_apply, table_source = table_source) }}