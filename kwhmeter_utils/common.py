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
    import pkg_resources
    logging.warning(f"{kwhmeter_util_config} do not exists. Using default one")
    with pkg_resources.resource_stream(__name__, 'data/kwhmeter_util_config.yml') as f:
        config = yaml.load(f, Loader=SafeLoader)
    with open(kwhmeter_util_config,'w') as f:                    
        f.write(yaml.dump(config))