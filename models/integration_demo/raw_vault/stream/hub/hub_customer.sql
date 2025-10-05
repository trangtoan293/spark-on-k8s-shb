
{%- set hub_customer = dv_config('hub_customer') -%}
{%- set dv_system = var("dv_system") -%}

{{ ktl_autovault.hub_transform(model=hub_customer, dv_system=dv_system, include_ghost_record=true) }}
