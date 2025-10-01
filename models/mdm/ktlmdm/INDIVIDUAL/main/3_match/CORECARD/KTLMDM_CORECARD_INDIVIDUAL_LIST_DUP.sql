{%-set project = 'KTLMDM' -%}
{%-set product = 'INDIVIDUAL' -%}
{%-set source = 'CORECARD' -%}

{# Get Config #}
{%- set general_conf = ktl_mdm_utils_get_general_config(project) -%}
{%- set rule_desc_conf = ktl_mdm_utils_get_rule_desc_config(project) -%}
{%- set rule_template_config = ktl_mdm_utils_get_rule_template_config(project) -%}

{%- set metadata_conf = ktl_mdm_utils_metadata_get_metadata_config(project,product,source) -%}
{%- set rule_apply = ktl_mdm_utils_get_rule_field_apply_config(project,product,source,'MATCH') -%}

{# Input Table #}
{%- set validate_tbl_lastest = ref('KTLMDM_CORECARD_INDIVIDUAL_VALIDATE_LASTEST') -%}
{%- set validate_tbl_incre = ref('KTLMDM_CORECARD_INDIVIDUAL_VALIDATE') -%}

{{ ktl_mdm_match_list_dup(general_conf,metadata_conf,rule_apply,validate_tbl_lastest,validate_tbl_incre) }}



