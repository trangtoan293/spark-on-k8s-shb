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

{# Get Config #}
{%- set general_conf = ktl_mdm_utils_get_general_config(project) -%}
{%- set rule_desc_conf = ktl_mdm_utils_get_rule_desc_config(project) -%}
{%- set rule_template_config = ktl_mdm_utils_get_rule_template_config(project) -%}

{%- set metadata_conf = ktl_mdm_utils_metadata_get_metadata_config(project,product,source) -%}
{%- set rule_apply = ktl_mdm_utils_get_rule_field_apply_config(project,product,source,'MATCH') -%}

{# Input Table #}
{%- set arrange_tbl = ref('KTLMDM_COREBANK_INDIVIDUAL_MATCHED_ARRANGE_MASTERLIST') -%}

{{ ktl_mdm_auto_match_tracking(general_conf,metadata_conf,rule_apply,arrange_tbl) }}
