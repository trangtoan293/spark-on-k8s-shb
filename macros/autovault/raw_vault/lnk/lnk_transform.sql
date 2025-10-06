{%- macro lnk_transform(model, dv_system, materialized="streaming") -%}

    {{- config(materialized=materialized) -}}

    {%- set hkey_name = render_hash_key_lnk_name(model) -%}
    {%- set ldt_keys = render_list_dv_system_ldt_key_name(dv_system) -%}

    with
        cte_stg_lnk as (
            select
                {{ render_hash_key_lnk_treatment(model) }},

                {% for expr in render_list_hash_key_hub_treatment(model) -%}
                    {{ expr }},
                {% endfor %}

                {% for expr in render_list_dv_system_column_treatment(dv_system) -%}
                    {{ expr }} {{- ',' if not loop.last }}
                {% endfor %}

            from
                {% if materialized == "streaming" -%}
                    {{ render_source_table_view_name(model) }}
                {%- else -%}
                    {{ render_source_table_full_name(model) }}
                {%- endif %}
            where
                1 = 1
                {% for expr in render_list_hash_key_lnk_component(model) -%}
                    and {{ expr }} is not null
                {% endfor %}
        ),
        
        cte_stg_lnk_latest_records as (
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
                    from cte_stg_lnk
                )
            where row_num = 1
        )

        {%- if is_streaming() -%}
            ,

            cte_stg_lnk_existed_keys as (
                select {{ hkey_name }}
                from cte_stg_lnk src
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

        {% for expr in render_list_hash_key_hub_name(model) -%}
            {{ expr }},
        {% endfor %}

        {% for expr in render_list_dv_system_column_name(dv_system) -%}
            {{ expr }} {{- ',' if not loop.last }}
        {% endfor %}

    from cte_stg_lnk_latest_records src
    
    {%- if is_streaming() %}

        where
            not exists (
                select 1
                from cte_stg_lnk_existed_keys tgt
                where tgt.{{ hkey_name }} = src.{{ hkey_name }}
            )

    {%- endif %}

{%- endmacro -%}
