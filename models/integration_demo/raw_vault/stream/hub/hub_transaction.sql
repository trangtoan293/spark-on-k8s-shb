
{%- set hub_transaction  = dv_config('hub_transaction') -%}
{%- set dv_system = var("dv_system") -%}

{{ ktl_autovault.hub_transform(model=hub_transaction, dv_system=dv_system, include_ghost_record=true) }}
