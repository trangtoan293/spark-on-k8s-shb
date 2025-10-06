
{%- macro render_list_hash_key_hub_component(model) -%}
    {%- set column = model.get('columns') | selectattr("key_type", "equalto", "hash_key_hub") | first -%}
    {{ return(column.get('source') | list) }}
{%- endmacro -%}

{%- macro render_list_hash_key_lnk_component(model) -%}
    {%- set column = model.get('columns') | selectattr("key_type", "equalto", "hash_key_lnk") | first -%}
    {{ return(column.get('source') | list) }}
{%- endmacro -%}

{%- macro render_list_source_dependent_key_name(model) -%}
    {%- set outs = [] -%}
    {%- for column in model.get('columns') | selectattr("key_type", "equalto", "dependent_key") | list -%}
        {%- do outs.append(column.get('source').get('name')) -%}
    {%- endfor -%}
    {{ return(outs) }}
{%- endmacro -%}

{%- macro render_list_source_ldt_key_name(dv_system) -%}
    {%- set outs = [] -%}
    {%- for key in ('dv_src_ldt', 'dv_kaf_ldt', 'dv_kaf_ofs') -%}
        {%- set tmp = (dv_system.get('columns') | selectattr('target', 'equalto', key) | first).get('source').get('name') -%}
        {%- do outs.append(tmp) -%}
    {%- endfor -%}
    {{ return(outs) }}
{%- endmacro -%}