{%- macro hub_transform(model, dv_system, materialized="streaming") -%}

    {{- config(materialized=materialized) -}}

    {%- set hkey_name = render_hash_key_hub_name(model) -%}
    {%- set ldt_keys = render_list_dv_system_ldt_key_name(dv_system) -%}

    with
        cte_stg_hub as (
            select
                {{ render_hash_key_hub_treatment(model) }},

                {% for expr in render_list_biz_key_treatment(model) -%}
                    {{ expr }},
                {% endfor %}

                {% for expr in render_list_dv_system_column_treatment(dv_system) -%}
                    {{ expr }},
                {% endfor %}

                {{ render_collision_code_treatment(model) }}

            from
                {% if materialized == "streaming" -%}
                    {{ render_source_table_view_name(model) }}
                {%- else -%}
                    {{ render_source_table_full_name(model) }}
                {%- endif %}
            where
                1 = 1
                {% for expr in render_list_hash_key_hub_component(model) -%}
                    and {{ expr }} is not null
                {% endfor %}
        ),

        cte_stg_hub_latest_records as (
            select *
            from
                (
                    select
                        *,

                        row_number() over (
                            partition by {{ hkey_name }}
                            order by
                                {% for key in ldt_keys -%}
                                    {{ key }} asc {{- ',' if not loop.last }}
                                {% endfor %}
                        ) as row_num

                    from cte_stg_hub
                )
            where row_num = 1
        )

        {%- if is_streaming() -%}
            ,

            cte_stg_hub_existed_keys as (
                select {{ hkey_name }}
                from cte_stg_hub src
                where
                    exists (
                        select 1
                        from {{ this }} tgt
                        where tgt.{{ hkey_name }} = src.{{ hkey_name }}
                    )
            )

        {%- endif %}

    select
        {{ hkey_name }},

        {% for expr in render_list_biz_key_name(model) -%}
            {{ expr }},
        {% endfor %}

        {% for expr in render_list_dv_system_column_name(dv_system) -%}
            {{ expr }},
        {% endfor %}

        {{ render_collision_code_name() }}

    from cte_stg_hub_latest_records src

    {%- if is_streaming() %}

        where
            not exists (
                select 1
                from cte_stg_hub_existed_keys tgt
                where tgt.{{ hkey_name }} = src.{{ hkey_name }}
            )

    {%- endif %}

{%- endmacro -%}
