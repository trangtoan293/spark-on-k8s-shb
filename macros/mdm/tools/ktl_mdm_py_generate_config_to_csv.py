import numpy as np
import pandas as pd
import yaml
import re
from typing import List


def parse_info_file_yaml(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        sql_content = file.read()

    # Regex to extract  YAML middle `{%- set yml -%}` and `{%- endset -%}`
    pattern = r"{%- set yml -%}(.*?){%- endset -%}"
    match = re.search(pattern, sql_content, re.DOTALL)
    
    if match:
        yaml_content = match.group(1).strip()  # get content YAML
        # Parse YAML to Python dict
        parsed_yaml = yaml.safe_load(yaml_content)
        return parsed_yaml
    else:
        return None


def get_list_config_rule_field_apply(parsed_yml) -> List[object]:
    data_info_config = []
    rule_type_mapping = {'cleansing': 'CLEAN', 'validate': 'VALIDATE'}
                
    for item in parsed_yml.get('KTL_MDM', []):
        _product = item.get('product')
        for config_rule in item.get('source_system', []):
            _source  = config_rule.get('name')

            for rule_type in ['cleansing', 'validate']:

                if config_rule.get(rule_type) is not None:
                    for rule in config_rule.get(rule_type):
                        _rule_code = rule.get('name')
                        _list_column = "|".join(rule.get('list_column', []))

                        data_info_config.append({
                            'product':_product, 
                            'source_system':_source, 
                            'rule_type': rule_type_mapping[rule_type], 
                            'rule_code':_rule_code, 
                            'column_apply':_list_column
                        })
    return data_info_config

def get_list_config_rule_desc(parsed_yml) -> List[object]:

    data_rule_desc = []
    rule_type_mapping = {'cleansing': 'CLEAN', 'validate': 'VALIDATE'}
    keys_to_remove = ['code', 'description', 'rule_template']  

    for rule_type in ['cleansing', 'validate']:
        for item in parsed_yml.get(rule_type, []):
            
            filtered_config = {k: v for k, v in item.items() if k not in keys_to_remove}
            combined_values = "|".join(str(value) for value in filtered_config.values()) 

            data_rule_desc.append({ 
                'component': rule_type_mapping[rule_type],
                'code': item.get('code', []),
                'template_name': item.get('rule_template', []),
                'condition': combined_values if len(combined_values) !=0 else None,
                'description': item.get('description', [])
            })
    
    return data_rule_desc

if __name__ == "__main__":

    # Đường dẫn file .sql
    file_path = "ktl_dbt/macros/ktl_mdm_configs/ktlmdm/ktlmdm_rule_field_apply.sql"

    data_info_config = get_list_config_rule_field_apply(parsed_yml = parse_info_file_yaml(file_path)) 

    df_finish = pd.DataFrame(data_info_config)
    
    df_finish.to_csv('ktl_dbt/seeds/mdm/config/MDM_INFO_RULE_FIELD_APPLY.csv', index=False, encoding='utf-8')

    data_rule_desc = get_list_config_rule_desc(parsed_yml = parse_info_file_yaml('ktl_dbt/macros/ktl_mdm_configs/ktlmdm/ktlmdm_rule_desc.sql')) 
    df_rule_desc = pd.DataFrame(data_rule_desc)
    df_rule_desc['from_date'] = None
    df_rule_desc['to_date'] = None
    df_rule_desc.to_csv('MDM_INFO_RULE_DESC.csv', index=False, encoding='utf-8')