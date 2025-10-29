{%- set project = 'KTLMDM' -%}
{%- set product = 'INDIVIDUAL' -%}
{%- set source_system = 'SHB' -%}
{%- set metadata_conf = ktl_mdm_utils_metadata_get_metadata_config(project_name = project, product_name = product, source = source_system, default = 'shb') -%}
{%- set lst_column_metadata = ktl_mdm_utils_metadata_get_metadata_column_lst(metadata_conf) -%}
{%- set lst_column_metadata_cdt = ktl_mdm_utils_metadata_get_cdt_column_lst(metadata_conf) -%}
{%- set lst_column_model = lst_column_metadata + lst_column_metadata_cdt -%}
{%- set rule_apply = ktl_mdm_utils_get_rule_field_apply_config(project_name = project, product = product, source = source_system, component='cleansing') -%}
{%- set shb_input_identifier = var('shb_input_table') -%}
{%- set shb_input_parts = shb_input_identifier.split('.') -%}
{%- if shb_input_parts | length == 2 -%}
    {%- set table_source = source(shb_input_parts[0], shb_input_parts[1]) -%}
{%- else -%}
    {%- set table_source = ref(shb_input_identifier) -%}
{%- endif -%}
{{ cleansing_handle(lst_column_model = lst_column_model, rule_apply = rule_apply, table_source = table_source, product_type = product, system = source_system, type_mode = 'cleansing') }}
