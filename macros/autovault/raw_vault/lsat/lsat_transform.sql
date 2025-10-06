{%- macro lsat_transform(model, dv_system) -%}

    {{-
        config(
            materialized="incremental"
        )
    -}}

    -- depends_on: {{ get_ref_der_table(model) }}
    {% if not is_incremental() -%}

        {{ lsat_transform_initial(model=model, dv_system=dv_system) }}

    {%- elif is_incremental() -%}

        {{ lsat_transform_incremental(model=model, dv_system=dv_system) }}

    {%- endif -%}

{%- endmacro -%}
