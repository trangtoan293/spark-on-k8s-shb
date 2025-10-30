{{
    config(
        pre_hook = [
            "DROP VIEW IF EXISTS {{ this }}",
            "DROP TABLE IF EXISTS {{ this }}"
        ]
    )
}}
{%- set project = 'KTLMDM' -%}
{%- set product = 'INDIVIDUAL' -%}
{%- set source = 'SHB' -%}
{%- set general_conf = ktl_mdm_utils_get_general_config(project) -%}
{%- set metadata_conf = ktl_mdm_utils_metadata_get_metadata_config(project_name = project, product_name = product, source = source, default = 'shb') -%}
{%- set rule_apply = ktl_mdm_utils_get_rule_field_apply_config(project_name = project, product = product, source = source, component='merge') -%}
{%- set cleansing_tbl = ref('KTLMDM_SHB_INDIVIDUAL_CLEANSING') -%}
{%- set invalid_tbl = ref('KTLMDM_SHB_INDIVIDUAL_INVALID') -%}
{%- set match_tbl = ref('KTLMDM_SHB_INDIVIDUAL_MATCH') -%}
{{ ktl_mdm_validate_merge(general_conf, metadata_conf, rule_apply, cleansing_tbl, invalid_tbl, match_tbl) }}
