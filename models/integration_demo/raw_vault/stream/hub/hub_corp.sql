
{%- set hub_corp = dv_config('hub_corp') -%}
{%- set dv_system = var("dv_system") -%}

{{ ktl_autovault.hub_transform(model=hub_corp, dv_system=dv_system, include_ghost_record=true) }}
