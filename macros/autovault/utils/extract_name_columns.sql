{%- macro render_collision_code_name(with_dtype=false) -%}
    dv_ccd {%- if with_dtype %} string {%- endif -%}
{%- endmacro -%}


{%- macro render_hash_key_hub_name(model, with_dtype=false) -%}
    {%- set column = model.get('columns') | selectattr("key_type", "equalto", "hash_key_hub") | first -%}
    {{ column.get('target') }}
    {%- if with_dtype %} {{ column.get('dtype') }} {%- endif -%}
{%- endmacro -%}


{%- macro render_list_hash_key_hub_name(model, with_dtype=false) -%}
    {%- set outs = [] -%}
    {%- for column in model.get('columns') | selectattr("key_type", "equalto", "hash_key_hub") | list + model.get('columns') | selectattr("key_type", "equalto", "hash_key_drv") | list -%}
        {%- set tmp -%}
            {{column.get('target')}} {%- if with_dtype %} {{column.get('dtype')}} {%- endif -%}
        {%- endset -%}
        {% do outs.append(tmp) %}
    {%- endfor -%}
    {{ return(outs) }}
{%- endmacro -%}


{%- macro render_hash_key_lnk_name(model, with_dtype=false) -%}
    {%- set column = model.get('columns') | selectattr("key_type", "equalto", "hash_key_lnk") | first -%}
    {{ column.get('target') }}
    {%- if with_dtype %} {{ column.get('dtype') }} {%- endif -%}
{%- endmacro -%}


{%- macro render_hash_key_drv_name(model, with_dtype=false) -%}
    {%- set column = model.get('columns') | selectattr("key_type", "equalto", "hash_key_drv") | first -%}
    {{ column.get('target') }}
    {%- if with_dtype %} {{ column.get('dtype') }} {%- endif -%}
{%- endmacro -%}


{%- macro render_hash_key_sat_name(model, with_dtype=false) -%}
    {%- set column = model.get('columns') | selectattr("key_type", "equalto", "hash_key_sat") | first -%}
    {{ column.get('target') }}
    {%- if with_dtype %} {{ column.get('dtype') }} {%- endif -%}
{%- endmacro -%}


{%- macro render_hash_key_lsat_name(model, with_dtype=false) -%}
    {{ render_hash_key_sat_name(model, with_dtype) }}
{%- endmacro -%}


{%- macro render_hash_diff_name(model, with_dtype=false) -%}
    {%- set column = model.get('columns') | selectattr("key_type", "equalto", "hash_diff") | first -%}
    {{ column.get('target') }}
    {%- if with_dtype %} {{ column.get('dtype') }} {%- endif -%}
{%- endmacro -%}


{%- macro render_list_biz_key_name(model, with_dtype=false) -%}
    {%- set outs = [] -%}
    {%- for column in model.get('columns') | selectattr("key_type", "equalto", "biz_key") -%}
        {%- set tmp -%}
            {{column.get('target')}} {%- if with_dtype %} {{column.get('dtype')}} {%- endif -%}
        {%- endset -%}
        {% do outs.append(tmp) %}
    {%- endfor -%}
    {{ return(outs) }}
{%- endmacro -%}


{%- macro render_list_dependent_key_name(model, with_dtype=false) -%}
    {%- set outs = [] -%}
    {%- for column in model.get('columns') | selectattr('key_type', 'equalto', "dependent_key") -%}
        {%- set tmp -%}
            {{column.get('target')}} {%- if with_dtype %} {{column.get('dtype')}} {%- endif -%}
        {%- endset -%}
        {% do outs.append(tmp) %}
    {%- endfor -%}
    {{ return(outs) }}
{%- endmacro -%}


{%- macro render_list_attr_column_name(model, with_dtype=false) -%}
    {%- set outs = [] -%}
    {%- for column in model.get('columns') | selectattr('key_type', 'undefined') -%}
        {%- set tmp -%}
            {{column.get('target')}} {%- if with_dtype %} {{column.get('dtype')}} {%- endif -%}
        {%- endset -%}
        {% do outs.append(tmp) %}
    {%- endfor -%}
    {{ return(outs) }}
{%- endmacro -%}


{%- macro render_list_dv_system_column_name(dv_system, with_dtype=false) -%}
    {%- set outs = [] -%}
    {%- for column in dv_system.get('columns') -%}
        {%- set tmp -%}
            {{column.get('target')}} {%- if with_dtype %} {{column.get('dtype')}}{%- endif -%}
        {%- endset -%}
        {% do outs.append(tmp) %}
    {%- endfor -%}
    {{ return(outs) }}
{%- endmacro -%}


{%- macro render_list_dv_system_ldt_key_name(dv_system) -%}
    {%- set outs = [] -%}
    {%- for key in ('dv_src_ldt', 'dv_kaf_ldt', 'dv_kaf_ofs') -%}
        {%- set tmp = (dv_system.get('columns') | selectattr('target', 'equalto', key) | first).get('target') -%}
        {%- do outs.append(tmp) -%}
    {%- endfor -%}
    {{ return(outs) }}
{%- endmacro -%}


{%- macro render_dv_system_cdc_ops_name(dv_system) -%}
    {{ (dv_system.get('columns') | selectattr('target', 'equalto', 'dv_cdc_ops') | first).get('target') }}
{%- endmacro -%}
