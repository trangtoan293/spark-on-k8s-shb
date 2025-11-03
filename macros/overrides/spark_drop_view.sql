{%- macro spark__drop_view(relation) -%}
  {# no-op: project uses only tables; avoid Iceberg DROP VIEW path #}
{%- endmacro -%}
