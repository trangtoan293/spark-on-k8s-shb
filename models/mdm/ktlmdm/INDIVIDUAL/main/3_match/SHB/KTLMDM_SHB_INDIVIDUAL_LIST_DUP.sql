{%- set project = 'KTLMDM' -%}
{%- set product = 'INDIVIDUAL' -%}
{%- set source = 'SHB' -%}

{%- set general_conf = ktl_mdm_utils_get_general_config(project) -%}
{%- set metadata_conf = ktl_mdm_utils_metadata_get_metadata_config(project_name = project, product_name = product, source = source, default = 'shb') -%}
{%- set rule_apply = ktl_mdm_utils_get_rule_field_apply_config(project_name = project, product = product, source = source, component='match') -%}

{%- set validate_tbl_lastest = ref('KTLMDM_SHB_INDIVIDUAL_VALIDATE_LASTEST') -%}
{%- set validate_tbl_incre = ref('KTLMDM_SHB_INDIVIDUAL_VALIDATE') -%}

{{ ktl_mdm_match_list_dup(general_conf, metadata_conf, rule_apply, validate_tbl_lastest, validate_tbl_incre) }}
