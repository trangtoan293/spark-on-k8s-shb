
{%- set hub_indi  = dv_config('hub_indi') -%}
{%- set dv_system = var("dv_system") -%}

{{ ktl_autovault.hub_transform(model=hub_indi, dv_system=dv_system, include_ghost_record=true) }}
