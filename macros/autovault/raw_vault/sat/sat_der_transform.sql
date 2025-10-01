{%- macro sat_der_transform(model, dv_system) -%}

    {%- set src_hkey_hub = render_list_hash_key_hub_component(model) -%}
    {%- set src_dep_keys = render_list_source_dependent_key_name(model) -%}
    {%- set src_ldt_keys = render_list_source_ldt_key_name(dv_system) -%}

    {%- set initial_date = var('initial_date', run_started_at.astimezone(modules.pytz.timezone("Asia/Ho_Chi_Minh")).strftime('%Y-%m-%d')) -%}

    select
        {{ render_hash_key_sat_treatment(model, dv_system) }},
        {{ render_hash_key_hub_treatment(model) }},
        {{ render_hash_diff_treatment(model) }},

        {% for expr in render_list_dependent_key_treatment(model) -%}
            {{ expr }},
        {% endfor %}

        {% for expr in render_list_attr_column_treatment(model) -%}
            {{ expr }},
        {% endfor %}

        {% for expr in render_list_dv_system_column_treatment(dv_system) -%}
            {{ expr }} {{- ',' if not loop.last }}
        {% endfor %}

    from {{ render_source_table_view_name(model) }}
    where
        {{ src_ldt_keys[0] }} >= {{ "date'" + initial_date + "'" }}

        {% for expr in src_hkey_hub + src_dep_keys -%}
            and {{ expr }} is not null
        {% endfor %}

{%- endmacro -%}
