import oracledb
import pandas as pd
import json
from datetime import datetime
import yaml

class CustomDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(CustomDumper, self).increase_indent(flow, False)

def get_oracle_connection():  
    # Đặt các thông tin kết nối  
    user = 'LAKEHOUSE'  
    password = 'l@ke246'  
    dsn = '192.168.1.58:1521/DATALAKE'  # DSN (Data Source Name)  

    # Kết nối đến cơ sở dữ liệu  
    connection = oracledb.connect(user=user, password=password, dsn=dsn)  
    return connection 

def get_data_table_oracle(_connection, sql_query:str):
    connection_db = _connection
    cursor = connection_db.cursor()

    try:
        cursor.execute(sql_query)

        # Fetch all rows from the executed query
        rows = cursor.fetchall()

        # Get column names from the cursor description
        column_names = [col[0] for col in cursor.description]

        # Convert the fetched data to a pandas DataFrame
        df = pd.DataFrame(rows, columns=column_names)
        return df
   
    except Exception as e:
        return {'success': False, 'message': str(e)}
    finally:
        cursor.close()
        # connection_db.close()

def get_rules(df_rule_field_config, column_name, rule_type):
        return df_rule_field_config.loc[
            (df_rule_field_config['COLUMN_APPLY'].str.contains(column_name, na=False)) & 
            (rule_type == df_rule_field_config['RULE_TYPE']),
            'RULE_CODE'
        ].tolist()

def gen_mdm_config_rule(_table_info_metadata, 
                        _table_rule_config,
                        _source,
                        _col_operating_sys = "OPERATING_SYSTEM"
                        ):

    _table_source = _table_info_metadata[_table_info_metadata[_col_operating_sys] == _source]
    
    # filter table rule_config for source
    _table_rule_config_source = _table_rule_config[_table_rule_config[_col_operating_sys] == _source]

    for source, group in _table_source.groupby(_col_operating_sys):
        columns_list = []

        for _, row in group.iterrows():
            clean_rules = get_rules(df_rule_field_config= _table_rule_config_source, column_name= row['COLUMN_NAME'], rule_type= 'CLEAN')
            validation_rules = get_rules(df_rule_field_config= _table_rule_config_source, column_name= row['COLUMN_NAME'], rule_type = 'VALIDATION')

            column_dict = {
                'target': row['COLUMN_NAME'],
                'dtype': row['COLUMN_TYPE'],
                'source': {
                    'name': row['SOURCE_COLUMN_NAME'],
                    'dtype': row['SOURCE_COLUMN_TYPE']
                    }
            }

            if row['IS_PK'] == 'Y':
                column_dict['key_type'] = 'primary_key'

            if row['IS_MASTER_KEY'] == 'Y':
                column_dict['column_type'] = 'master_column'

            if row['HAS_CDT'] == 'Y':
                column_dict['extend_columns'] = {
                    'change_date': row['COLUMN_NAME'] + "_cdt",
                    'error_count': row['COLUMN_NAME'] + "_err_cnt"
                } 

            if clean_rules:
                column_dict['cleansing_rule'] = clean_rules
            
            if validation_rules:
                column_dict['validate_rule'] = validation_rules

            merge_priority_os = _table_rule_config_source.loc[(_table_rule_config_source['RULE_CODE']==row['COLUMN_NAME']) & (_table_rule_config_source['RULE_TYPE']=='MERGE'), 'MERGE_PRIORITY_OS'].values
            merge_master_os = _table_rule_config_source.loc[(_table_rule_config_source['RULE_CODE']==row['COLUMN_NAME']) & (_table_rule_config_source['RULE_TYPE']=='MERGE'), 'MERGE_MASTER_OS'].values
            
            if merge_priority_os.size > 0:
                merge_is_use_time_priority = _table_rule_config_source.loc[(_table_rule_config_source['RULE_CODE']==row['COLUMN_NAME']) & (_table_rule_config_source['RULE_TYPE']=='MERGE'),'MERGE_IS_USE_TIME_PRIORITY'].values
                merge_is_use_time_priority_trim = [item.strip() for item in merge_priority_os[0].split(",")]
                column_dict['merge_rule'] = {
                    'master_table': merge_master_os[0],
                    'table_priority': merge_is_use_time_priority_trim,
                    'time_priority': True if merge_is_use_time_priority=='Y' else False 
                }
            
            columns_list.append(column_dict)

    matchs_list = []
    for _, row in _table_rule_config_source[_table_rule_config_source['RULE_TYPE'] == 'MATCH'].iterrows():
        
        list_col_apply_strip = [item.strip() for item in row['COLUMN_APPLY'].split(",")]

        fuzzy_list = []
        similar_list = []
        for item in list_col_apply_strip:
            list_item = item.split(":")
            if len(list_item) == 1:
                similar_list.append(list_item[0])

                match_dict = {
                    'name': row['RULE_CODE'],
                    'match_type': 'auto',
                    'similar_cols': similar_list
                }
            else :
                fuzzy_list.append({list_item[0]:int(list_item[1])})

                match_dict = {
                    'name': row['RULE_CODE'],
                    'match_type': 'auto',
                    'similar_cols': similar_list,
                    'fuzzy_cols': fuzzy_list
                }

        matchs_list.append(match_dict)

    yaml_dict = {
        'operation_system': _source,
        'columns': columns_list,
        'match_rule': matchs_list
    }
    
    return yaml_dict

def write_format_file_yaml(yaml_dict, path_yaml_save = 'data_output.yaml'):

    with open(path_yaml_save, 'w') as file:  
        file.write(f"operation_system: {yaml_dict['operation_system']}\n")
        
        file.write("columns:\n")  
        for column in yaml_dict['columns']:  
            yaml.dump([column], file, Dumper=CustomDumper, default_flow_style=False, sort_keys=False, allow_unicode=True, indent=2)  
            file.write("\n")  # Thêm một dòng trống giữa các mục

        file.write(f"match_rule:\n")
        for match_rule in yaml_dict['match_rule']:
            yaml.dump([match_rule], file, Dumper=CustomDumper, default_flow_style=False, sort_keys=False, allow_unicode=True, indent=2)
    
if __name__ == "__main__":
    #get connection db oracle 
    connection = get_oracle_connection()
    #get table mdm_info_metadata
    source = "COREBANK"
    query_mdm_info_metadata = f""" SELECT * FROM LAKEHOUSE.MDM_INFO_METADATA WHERE OPERATING_SYSTEM = '{source}' ORDER BY COLUMN_ORD"""

    df_mdm_info_metadata = get_data_table_oracle(_connection= connection, sql_query=query_mdm_info_metadata)

    #get table mdm_rule_field_config
    query_mdm_rule_field_config = f""" SELECT * FROM LAKEHOUSE.MDM_INFO_RULE_FIELD_CONFIG WHERE OPERATING_SYSTEM = '{source}' """
    df_mdm_rule_field_config = get_data_table_oracle(_connection = connection, sql_query=query_mdm_rule_field_config)
    
    connection.close()

    
    # gen config mdm yaml
    yaml_dict = gen_mdm_config_rule(_table_info_metadata= df_mdm_info_metadata,
                                    _table_rule_config= df_mdm_rule_field_config,
                                    _source= "COREBANK"
                        )

    write_format_file_yaml(yaml_dict)






    # yaml_data = yaml.dump(yaml_dict, Dumper=CustomDumper, sort_keys=False, default_flow_style=False, indent=2)
    # with open('data_output.yaml', 'w') as file:
    #     file.write(yaml_data)
