{{
    config(
        pre_hook = [
            "{% if adapter.get_relation(this.database, this.schema, this.identifier) is not none %}"
            "  DROP VIEW IF EXISTS {{ this }}",
            "  DROP TABLE IF EXISTS {{ this }} PURGE",
            "{% endif %}"
        ]
    )
}}
{%- set project = 'KTLMDM' -%}
{%- set product = 'INDIVIDUAL' -%}
{%- set source = 'SHB' -%}
{%- set general_conf = ktl_mdm_utils_get_general_config(project) -%}
{%- set metadata_conf = ktl_mdm_utils_metadata_get_metadata_config(project_name = project, product_name = product, source = source, default = 'shb') -%}
{%- set rule_apply = ktl_mdm_utils_get_rule_field_apply_config(project_name = project, product = product, source = source, component='validate') -%}
{%- set table_source = ref('KTLMDM_SHB_INDIVIDUAL_CLEANSING') -%}
{{ ktl_mdm_validate_invalid(general_conf, metadata_conf, rule_apply = rule_apply, table_source = table_source, product_type = product, source = source, type_mode = 'validate') }}
