{%- macro sat_transform_incremental(model, dv_system) -%}

    {%- set hkey_hub_name = render_hash_key_hub_name(model) -%}
    {%- set dep_keys = render_list_dependent_key_name(model) -%}
    {%- set ldt_keys = render_list_dv_system_ldt_key_name(dv_system) -%}
    {%- set cdc_ops = render_dv_system_cdc_ops_name(dv_system) -%}
    {%- set hash_diff = render_hash_diff_name(model) -%}

    {%- set start_date = var('incre_start_date', None) -%}
    {%- set end_date = var('incre_end_date', run_started_at.astimezone(modules.pytz.timezone("Asia/Ho_Chi_Minh")).strftime('%Y-%m-%d')) -%}

    with
        cte_sat_der_latest_records as (
            select *
            from
                (
                    select
                        *,

                        row_number() over (
                            partition by
                                {% for key in [hkey_hub_name] + dep_keys -%}
                                    {{ key }} {{- ',' if not loop.last }}
                                {% endfor %}
                            order by
                                {% for key in ldt_keys -%}
                                    {{ key }} desc {{- ',' if not loop.last }}
                                {%- endfor %}
                        ) as row_num

                    from {{ render_target_der_table_full_name(model) }}
                    where
                        {% if start_date -%}
                            {{ ldt_keys[0] }} >= {{ "date'" + start_date + "'" }}
                        {% else -%} 1 = 1
                        {% endif -%}
                        
                        and {{ ldt_keys[0] }} < {{ "date'" + end_date + "'" }}
                )
            where row_num = 1
        ),

        cte_sat_latest_records as (
            select *
            from
                (
                    select
                        *,

                        row_number() over (
                            partition by
                                {% for key in [hkey_hub_name] + dep_keys -%}
                                    {{ key }} {{- ',' if not loop.last }}
                                {% endfor %}
                            order by
                                {% for key in ldt_keys -%}
                                    {{ key }} desc {{- ',' if not loop.last }}
                                {%- endfor %}
                        ) as row_num

                    from {{ this }}
                )
            where row_num = 1
        )

    select
        {{ render_hash_key_sat_name(model) }},
        {{ render_hash_key_hub_name(model) }},
        {{ render_hash_diff_name(model) }},

        {% for name in render_list_dependent_key_name(model) -%}
            {{ name }},
        {% endfor %}

        {% for name in render_list_attr_column_name(model) -%}
            {{ name }},
        {% endfor %}

        {% for name in render_list_dv_system_column_name(dv_system) -%}
            {{ name }} {{- ',' if not loop.last }}
        {% endfor %}

    from cte_sat_der_latest_records sat_der
    where
        not exists (
            select 1
            from cte_sat_latest_records sat
            where
                sat_der.{{ hkey_hub_name }} = sat.{{ hkey_hub_name }}

                {% for column in dep_keys -%}
                    and sat_der.{{ column }} = sat.{{ column }}
                {% endfor %}

                and sat_der.{{ hash_diff }} = sat.{{ hash_diff }}
                and lower(sat_der.{{ cdc_ops }}) not in ('d', 't')
                and lower(sat.{{ cdc_ops }}) not in ('d', 't')
        )

{%- endmacro -%}
