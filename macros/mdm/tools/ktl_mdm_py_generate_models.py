import argparse
import os
import yaml

PATH_DICT = {'root':'models/mdm'}

def create_folder(directory_name):
    try:
        os.mkdir(directory_name)
        print(f"Directory '{directory_name}' created successfully.")
    except FileExistsError:
        print(f"Directory '{directory_name}' already exists.")
    except PermissionError:
        print(f"Permission denied: Unable to create '{directory_name}'.")
    except Exception as e:
        print(f"An error occurred: {e}")
        
def create_file_model(directory_name, type=None):
    if type is None:
        if os.path.isfile(directory_name):
            print(f"Directory '{directory_name}' already exists.")
        else:
            f = open(directory_name, "w")
            f.close()

def generate_models(**kwargs):
    config_file_name = kwargs['name']
    print(config_file_name)
    
    with open(config_file_name, 'r') as file:
        config_yml = yaml.safe_load(file)
    
    print(config_yml)
    ktl_mdm_yml = config_yml['KTL_MDM']
    prefix_table_name = config_yml['prefix_table_name']
    
    # Create parent folder
    directory_name = PATH_DICT['root'] + '/' + config_yml['name']
    PATH_DICT['parent'] = directory_name
    create_folder(directory_name)
        
    # Create product folder
    for product in ktl_mdm_yml:
        product_name = product['product']
        directory_name = PATH_DICT['parent'] + '/' + product_name
        path_product_key = 'product_'+product_name
        PATH_DICT[path_product_key] = directory_name
        create_folder(directory_name)
        
        # Create main folder
        directory_name = PATH_DICT['parent'] + '/' + product_name + '/main'
        path_main_key = path_product_key + '_main'
        PATH_DICT[path_main_key] = directory_name
        create_folder(directory_name)
        
        ## Create ingest folder
        directory_name = PATH_DICT[path_main_key] + '/0_ingest'
        path_ingest_key = path_main_key + '_ingest'
        PATH_DICT[path_ingest_key] = directory_name
        create_folder(directory_name)
        
        ### Create ingest model
        for source in product['source_system']:
            if "INGEST" in source['component']:
                source_name = source['name'].upper()
                directory_name = PATH_DICT[path_ingest_key] +'/'+'VW_'+prefix_table_name+'_'+source_name+'_'+product_name+'_INGEST.sql'
                create_file_model(directory_name)
                

        ## Create clean folder
        directory_name = PATH_DICT[path_main_key] + '/1_cleansing'
        path_cleansing_key = path_main_key + '_cleansing'
        PATH_DICT[path_cleansing_key] = directory_name
        create_folder(directory_name)
        
        ### Create clean model
        for source in product['source_system']:
            if "CLEAN" in source['component']:
                source_name = source['name'].upper()
                directory_name = PATH_DICT[path_cleansing_key] + '/' +prefix_table_name+'_'+source_name+'_'+product_name+'_CLEANSING.sql'
                create_file_model(directory_name)
        
        ## Create validate folder
        directory_name = PATH_DICT[path_main_key] + '/2_validate'
        path_validate_key = path_main_key + '_validate'
        PATH_DICT[path_validate_key] = directory_name
        create_folder(directory_name)
        
        ### Create validate model
        for source in product['source_system']:
            if "VALIDATE" in source['component']:
                source_name = source['name'].upper()
                
                directory_name = PATH_DICT[path_validate_key] + '/' + source_name
                path_validate_src_key = path_validate_key + '_' + source_name
                PATH_DICT[path_validate_src_key] = directory_name
                create_folder(directory_name)
                
                directory_name = PATH_DICT[path_validate_src_key] + '/' +prefix_table_name+'_'+source_name+'_'+product_name+'_INVALID.sql'
                create_file_model(directory_name)
                directory_name = PATH_DICT[path_validate_src_key] + '/' +prefix_table_name+'_'+source_name+'_'+product_name+'_VALIDATE.sql'
                create_file_model(directory_name)
                directory_name = PATH_DICT[path_validate_src_key] + '/' +prefix_table_name+'_'+source_name+'_'+product_name+'_VALIDATE_LASTEST.sql'
                create_file_model(directory_name)
        
        ## Create match folder
        directory_name = PATH_DICT[path_main_key] + '/3_match'
        path_match_key = path_main_key + '_match'
        PATH_DICT[path_match_key] = directory_name
        create_folder(directory_name)
        
        ### Create match model
        for source in product['source_system']:
            if "MATCH" in source['component']:
                source_name = source['name'].upper()
                
                directory_name = PATH_DICT[path_match_key] + '/' + source_name
                path_match_src_key = path_match_key + '_' + source_name
                PATH_DICT[path_match_src_key] = directory_name
                create_folder(directory_name)
                
                directory_name = PATH_DICT[path_match_src_key] + '/' +prefix_table_name+'_'+source_name+'_'+product_name+'_LIST_DUP.sql'
                create_file_model(directory_name)
                directory_name = PATH_DICT[path_match_src_key] + '/' +prefix_table_name+'_'+source_name+'_'+product_name+'_DUPLICATE_NOT_RULE_ORDER.sql'
                create_file_model(directory_name)
                directory_name = PATH_DICT[path_match_src_key] + '/' +prefix_table_name+'_'+source_name+'_'+product_name+'_DUPLICATE.sql'
                create_file_model(directory_name)
                directory_name = PATH_DICT[path_match_src_key] + '/' +prefix_table_name+'_'+source_name+'_'+product_name+'_MATCHED_ARRANGE_MASTERLIST.sql'
                create_file_model(directory_name)
                directory_name = PATH_DICT[path_match_src_key] + '/' +prefix_table_name+'_'+source_name+'_'+product_name+'_AUTO_MATCH_TRACKING.sql'
                create_file_model(directory_name)
                directory_name = PATH_DICT[path_match_src_key] + '/' +prefix_table_name+'_'+source_name+'_'+product_name+'_AUTO_MATCH.sql'
                create_file_model(directory_name)
                directory_name = PATH_DICT[path_match_src_key] + '/' +prefix_table_name+'_'+source_name+'_'+product_name+'_MATCHED.sql'
                create_file_model(directory_name)
                directory_name = PATH_DICT[path_match_src_key] + '/' +prefix_table_name+'_'+source_name+'_'+product_name+'_MATCHED_LASTEST.sql'
                create_file_model(directory_name)
        
        ## Create merge folder
        directory_name = PATH_DICT[path_main_key] + '/4_merge'
        path_merge_key = path_main_key + '_merge'
        PATH_DICT[path_merge_key] = directory_name
        create_folder(directory_name)
        
        ## Create golden folder
        directory_name = PATH_DICT[path_main_key] + '/5_golden'
        path_golden_key = path_main_key + '_golden'
        PATH_DICT[path_golden_key] = directory_name
        create_folder(directory_name)
        
        
        # Create snapshot folder
        directory_name = PATH_DICT['parent'] + '/' + product_name + '/snapshot'
        path_snapshot_key = path_product_key + '_snapshot'
        PATH_DICT[path_snapshot_key] = directory_name
        create_folder(directory_name)
        
        
        


        
    
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", help="Config File Name", default='macros/ktl_mdm_configs/ktlmdm/ktlmdm_general.yml')
    
    args = parser.parse_args()
    generate_models(**vars(args))
    