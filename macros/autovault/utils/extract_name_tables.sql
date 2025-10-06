{%- macro get_ref_der_table(model) -%}
    {{ return(ref(model.get('target_table').replace("sat_", "sat_der_"))) }}
{%- endmacro -%}

{%- macro render_target_der_table_full_name(model) -%}
    {{ get_ref_der_table(model) }}
{%- endmacro -%}


{%- macro get_ref_snp_table(model) -%}
    {{ return(ref(model.get('target_table').replace("sat_", "sat_snp_"))) }}
{%- endmacro -%}

{%- macro render_target_snp_table_full_name(model) -%}
    {{ get_ref_snp_table(model) }}
{%- endmacro -%}


{%- macro render_target_lsate_table_full_name(model) -%}
    {{ ref(model.get('target_table').replace("lnk_", "lsate_")) }}
{%- endmacro -%}


{%- macro render_source_table_full_name(model) -%}
    {{ source(model.get('source_schema'), model.get('source_table')) }}
{%- endmacro -%}


{%- macro render_source_table_view_name(model) -%}
    {{ source_view(model.get('source_schema'), model.get('source_table')) }}
{%- endmacro -%}


{%- macro render_parent_table_full_name(model, target_column=None) -%}
    {%- if column_name == None -%} {{ model.get('parent_table') }}
    {%- else -%}
        {%- set column = model.get('columns') | selectattr("target", "equalto", target_column) | first -%}
        {%- if column.parent is defined -%} {{ column.get('parent') }}
        {%- else -%} {{ model.get('parent_table') }}
        {%- endif -%}
    {%- endif -%}
{%- endmacro -%}
