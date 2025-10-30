
{%- macro ktl_mdm_utils_get_rule_field_apply_config(project_name,product,source,component) -%}
    {%- for product_item in context[project_name|lower+'_rule_field_apply_config_yml']().get('KTL_MDM') -%}
        {%- if product_item.get('product')|lower == product|lower -%}
            {%- if component|lower == 'merge' -%}
            {%- else -%}
                {%- for source_item in product_item.get('source_system') -%}
                    {%- if source_item.get('name')|lower == source|lower -%}
                        {%- set conf = source_item.get(component|lower) -%}
                        {# If conf already a mapping with matched_by_rules, return as-is #}
                        {%- if conf is mapping and conf.get('matched_by_rules') is not none -%}
                            {{ return(conf) }}
                        {%- endif -%}
                        {# If conf is a list of rules, wrap into expected structure #}
                        {%- if conf is sequence and (conf is not string) -%}
                            {{ return({'matched_by_rules': conf}) }}
                        {%- endif -%}
                        {{ return(conf) }}
                    {%- endif -%}
                {%- endfor -%}
            {%- endif -%}
        {%- endif -%}
    {%- endfor -%}
{%- endmacro -%}


{# get list column apply rule available #}
{%- macro ktl_mdm_get_column_available(lst_col_metadata, lst_col_rule_apply) -%}
    {%- set result = [] -%}

    {%- for item in lst_col_rule_apply -%}
        {%- if item in lst_col_metadata -%}
            {%- do result.append(item) -%}
        {%- endif -%}
    {%- endfor -%}

    {{ return(result) }}
{%- endmacro -%}