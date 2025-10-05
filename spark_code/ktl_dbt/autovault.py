import os
import requests
import json
import yaml
import logging

logger = logging.getLogger(__name__)

def _save_ktl_autovault_configs_from_json(config_dir, autovault_configs):
    if isinstance(autovault_configs, str):
        autovault_configs = json.loads(autovault_configs)

    for model_name, config in autovault_configs.items():
        model_name = model_name.lower()

        # Search for existing file with model_name in config_dir
        existing_file = None
        for root, _, files in os.walk(config_dir):
            for file in files:
                if file.lower() in [f"{model_name}.yml", f"{model_name}.yaml"]:
                    existing_file = os.path.join(root, file)
                    break
            if existing_file:
                break

        # If found, use that path, otherwise create new one in config_dir
        if existing_file:
            file_path = existing_file
        else:
            file_path = os.path.join(config_dir, f"{model_name}.yml")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Write the config to the file
        with open(file_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2, sort_keys=False)


def _get_ktl_autovault_config_dir(dbt_project_dir):
    return os.path.join(dbt_project_dir, 'ktl_autovault_configs')


def load_ktl_autovault_configs(dbt_project_dir, autovault_configs=None):
    config_dir = _get_ktl_autovault_config_dir(dbt_project_dir)
    macro_dir = os.path.join(dbt_project_dir, 'macros/ktl_autovault_configs')

    if autovault_configs:
        os.makedirs(config_dir, exist_ok=True)
        _save_ktl_autovault_configs_from_json(config_dir, autovault_configs)

    if not os.path.exists(config_dir):
        return

    os.makedirs(macro_dir, exist_ok=True)

    for root, _, files in os.walk(config_dir):
        for file in files:
            if file.endswith('.yml') or file.endswith('.yaml'):
                yml_file = os.path.join(root, file)
                process_yaml_config_file(yml_file, macro_dir)

    create_dv_config_macro(config_dir, macro_dir)


def process_yaml_config_file(yml_file, macro_dir):
    filename = os.path.basename(yml_file).rsplit('.', 1)[0].lower()
    macro_file = os.path.join(macro_dir, f"{filename}_dv_config.sql")

    with open(yml_file, 'r') as yf:
        yml_content = yf.read()

    new_content = f"""

{{%- macro {filename}_dv_config() -%}}
    {{%- set model_yml -%}}

{yml_content}

    {{%- endset -%}}

    {{%- set model = fromyaml(model_yml) -%}}
    {{{{ return(model) }}}}

{{%- endmacro -%}}

"""
    with open(macro_file, 'w') as nf:
        nf.write(new_content)


def create_dv_config_macro(config_dir, macro_dir):
    output_file = os.path.join(macro_dir, 'dv_config.sql')

    with open(output_file, 'w') as of:
        
        of.write("""
{%- macro dv_config(model_name) -%}

    {%- set model_name_lower = model_name.lower() -%}
    {%- set all = [] -%}
""")

        for root, _, files in os.walk(config_dir):
            for file in files:
                if file.endswith('.yml'):
                    filename = os.path.basename(file).rsplit('.', 1)[0].lower()

                    of.write(f"""
    {{%- if model_name_lower == "{filename}" -%}}
        {{{{ return({filename}_dv_config()) }}}}
    {{%- endif -%}}
    {{%- do all.append({filename}_dv_config()) -%}}
""")

        of.write("""
    {%- if model_name_lower == "all" -%}
        {{ return(all) }}
    {%- endif -%}

    {{ exceptions.raise_compiler_error("Not found model '" + model_name + "', please ensure it is defined in directory 'ktl_autovault_configs' and rerun 'ktl load-autovault-configs'.") }}

{%- endmacro -%}
""")


def init_ktl_autovault_models(dbt_project_dir, force=False):
    config_dir = _get_ktl_autovault_config_dir(dbt_project_dir)
    model_dir = os.path.join(dbt_project_dir, 'models')

    def __init_ktl_autovault_model(yml_file):
        with open(yml_file, 'r') as yf:
            model_config = yaml.safe_load(yf)

        if not model_config.get('init_model', False):
            return
        
        model_name = os.path.basename(yml_file)[:-4]

        for root, _, files in os.walk(model_dir):
            for file in files:
                if file == model_name+'.sql':
                    full_path = os.path.join(root, file)
                    if force:
                        os.remove(full_path)
                    else:
                        logger.warning(f'Model {model_name} existed in {full_path}. Use option --force to overwrite it.')
                        return

        macro = model_config['macro']
        args = {'model': f"dv_config('{model_name}')"}
        args.update(model_config.get('extra_args', {}))
        args = [f'{k}={v}' for k,v in args.items()]

        model_content = f"""{{{{ {macro}({', '.join(args)}) }}}}"""
        model_file = yml_file.replace(config_dir, model_dir).replace('.yml', '.sql')

        os.makedirs(os.path.dirname(model_file), exist_ok=True)
        with open(model_file, 'w') as mf:
            mf.write(model_content)

    for root, _, files in os.walk(config_dir):
        for file in files:
            if file.endswith('.yml'):
                yml_file = os.path.join(root, file)
                __init_ktl_autovault_model(yml_file)
