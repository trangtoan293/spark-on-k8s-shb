{{
    config(
        pre_hook = [
            "DROP TABLE {{this}} purge",
        ]
    )
}}
{%- set project = 'KTLMDM' -%}
{%- set product = 'INDIVIDUAL' -%}
{%- set source = 'SHB' -%}
{%- set general_conf = ktl_mdm_utils_get_general_config(project) -%}
{%- set metadata_conf = ktl_mdm_utils_metadata_get_metadata_config(project_name = project, product = product, source = source, default = 'shb') -%}
{%- set rule_desc_conf = ktl_mdm_utils_get_rule_desc_config(project_name = project) -%}
{%- set rule_template_config = ktl_mdm_utils_get_rule_template_config(project) -%}
{%- set rule_apply = ktl_mdm_utils_get_rule_field_apply_config(project_name = project, product = product, source = source, component='validate') -%}
{%- set cleansing_tbl = ref('KTLMDM_SHB_INDIVIDUAL_CLEANSING') -%}
{%- set invalid_tbl = ref('KTLMDM_SHB_INDIVIDUAL_INVALID') -%}
{{ ktl_mdm_validate_validate(general_conf, metadata_conf, rule_apply, cleansing_tbl, invalid_tbl) }}
