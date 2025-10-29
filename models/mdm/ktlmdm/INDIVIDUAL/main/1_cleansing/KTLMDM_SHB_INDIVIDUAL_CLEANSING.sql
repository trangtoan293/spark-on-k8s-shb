{%- set project = 'KTLMDM' -%}
{%- set product = 'INDIVIDUAL' -%}
{%- set source = 'SHB' -%}
{%- set metadata_conf = ktl_mdm_utils_metadata_get_metadata_config(project_name = project, product_name = product, source = source, default = 'shb') -%}
{%- set lst_column_metadata = ktl_mdm_utils_metadata_get_metadata_column_lst(metadata_conf) -%}
{%- set lst_column_metadata_cdt = ktl_mdm_utils_metadata_get_cdt_column_lst(metadata_conf) -%}
{%- set lst_column_model = lst_column_metadata + lst_column_metadata_cdt -%}
{%- set rule_apply = ktl_mdm_utils_get_rule_field_apply_config(project_name = project, product = product, source = source, component='cleansing') -%}
{%- set table_source = ref(var('shb_input_table')) -%}
{{ cleansing_handle(lst_column_model = lst_column_model, rule_apply = rule_apply, table_source = table_source, product_type = product, system = source, type_mode = 'cleansing') }}
