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

{%- set metadata_conf = ktl_mdm_utils_metadata_get_metadata_config(project,product,'COREBANK') -%}
{%- set rule_apply = ktl_mdm_utils_get_rule_field_apply_config(project,product,source,'MERGE') -%}

{# Input Table #}
{%- set mrlpivot_tbl = ref('KTLMDM_MDM_INDIVIDUAL_MERGE_LIST_PIVOT') -%}
{%- set mrtrack_tbl = ref('KTLMDM_MDM_INDIVIDUAL_MERGE_TRACKING') -%}
{%- set match_tbl_dict = {
                            'COREBANK': ref('KTLMDM_COREBANK_INDIVIDUAL_MATCHED'),
                            'CORECARD': ref('KTLMDM_CORECARD_INDIVIDUAL_MATCHED'),
                            'CRM': ref('KTLMDM_CRM_INDIVIDUAL_MATCHED'),
                         } -%}

{{ ktl_mdm_merge_merged(general_conf,metadata_conf,rule_apply,mrlpivot_tbl,mrtrack_tbl,match_tbl_dict) }}
