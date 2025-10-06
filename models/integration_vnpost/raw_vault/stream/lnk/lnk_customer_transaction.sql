
{%- set model = dv_config('lnk_customer_transaction') -%}
{%- set dv_system = var("dv_system") -%}


{{ ktl_autovault.lnk_transform(model=model, dv_system=dv_system) }}
