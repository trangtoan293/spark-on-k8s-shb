{{
    config(
        materialized='table',
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
{%- set rule_apply = ktl_mdm_utils_get_rule_field_apply_config(project_name = project, product = product, source = source, component='match') -%}
{%- set validate_tbl_incre = ref('KTLMDM_SHB_INDIVIDUAL_VALIDATE') -%}
{%- set dup_tbl = ref('KTLMDM_SHB_INDIVIDUAL_MATCH_DUPLICATE') -%}
{%- set auto_match_tbl = ref('KTLMDM_SHB_INDIVIDUAL_MATCH_AUTO') -%}
{{ ktl_mdm_match_matched(general_conf, metadata_conf, rule_apply, validate_tbl_incre, dup_tbl, auto_match_tbl) }}
