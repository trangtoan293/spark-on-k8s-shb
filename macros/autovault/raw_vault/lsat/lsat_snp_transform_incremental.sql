{%- macro lsat_snp_transform_incremental(model, dv_system) -%}

    {%- set hkey_lnk_name = render_hash_key_lnk_name(model) -%}
    {%- set dep_keys = render_list_dependent_key_name(model) -%}
    {%- set ldt_keys = render_list_dv_system_ldt_key_name(dv_system) -%}
    {%- set cdc_ops = render_dv_system_cdc_ops_name(dv_system) -%}
    {%- set hash_diff = render_hash_diff_name(model) -%}
    
    {%- set start_date = env_var('INCRE_START_DATE', '') -%}
    {%- set end_date = env_var('INCRE_END_DATE', run_started_at.astimezone(modules.pytz.timezone("Asia/Ho_Chi_Minh")).strftime('%Y-%m-%d')) -%}

    {{- config(unique_key=[hkey_lnk_name]+dep_keys) -}}

    with
        cte_lsat_der_latest_records as (
            select *
            from
                (
                    select
                        *,

                        row_number() over (
                            partition by
                                {% for key in [hkey_lnk_name] + dep_keys -%}
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

        cte_lsat_snp_latest_records as (
            select *
            from
                (
                    select
                        *,

                        row_number() over (
                            partition by
                                {% for key in [hkey_lnk_name] + dep_keys -%}
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
        {{ render_hash_key_lsat_name(model) }},
        {{ render_hash_key_lnk_name(model) }},
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

    from cte_lsat_der_latest_records lsat_der
    where
        not exists (
            select 1
            from cte_lsat_snp_latest_records lsat_snp
            where
                lsat_der.{{ hkey_lnk_name }} = lsat_snp.{{ hkey_lnk_name }}

                {% for column in dep_keys -%}
                    and lsat_der.{{ column }} = lsat_snp.{{ column }}
                {% endfor %}

                and lsat_der.{{ hash_diff }} = lsat_snp.{{ hash_diff }}
                and lower(lsat_der.{{ cdc_ops }}) not in ('d', 't')
                and lower(lsat_snp.{{ cdc_ops }}) not in ('d', 't')
        )

{%- endmacro -%}
