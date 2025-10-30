{%- set project = 'KTLMDM' -%}
{%- set product = 'INDIVIDUAL' -%}
{%- set source = 'SHB' -%}

{%- set general_conf = ktl_mdm_utils_get_general_config(project) -%}
{%- set metadata_conf = ktl_mdm_utils_metadata_get_metadata_config(project_name = project, product_name = product, source = source, default = 'shb') -%}
{%- set rule_apply = ktl_mdm_utils_get_rule_field_apply_config(project_name = project, product = product, source = source, component='match') -%}

{%- set validate_tbl_lastest = ref('KTLMDM_SHB_INDIVIDUAL_VALIDATE_LASTEST') -%}
{%- set dup_tbl = ref('KTLMDM_SHB_INDIVIDUAL_MATCH_DUPLICATE') -%}

{{ ktl_mdm_match_arrange_masterlist(general_conf, metadata_conf, rule_apply, validate_tbl_lastest, dup_tbl) }}
