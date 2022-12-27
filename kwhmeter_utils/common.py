from pathlib import Path
import yaml
from yaml.loader import SafeLoader
import os
import logging
from kwhmeter import data_dir

kwhmeter_util_config=f'{data_dir}/kwhmeter_util_config.yml'

if os.path.exists(kwhmeter_util_config):
    with open(kwhmeter_util_config) as f:
        config = yaml.load(f, Loader=SafeLoader)
else:
    logging.error(f"{kwhmeter_util_config} do not exists")
    exit(1)