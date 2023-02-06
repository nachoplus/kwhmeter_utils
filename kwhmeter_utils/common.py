from pathlib import Path
import yaml
from yaml.loader import SafeLoader
import os
import logging
from kwhmeter import data_dir

kwhmeter_pvpc_config=f'{data_dir}/kwhmeter_pvpc_config.yml'

if os.path.exists(kwhmeter_pvpc_config):
    with open(kwhmeter_pvpc_config) as f:
        config_pvpc = yaml.load(f, Loader=SafeLoader)
else:
    import pkg_resources
    logging.warning(f"{kwhmeter_pvpc_config} do not exists. Using default one")
    with pkg_resources.resource_stream(__name__, 'data/kwhmeter_pvpc_config.yml') as f:
        config_pvpc = yaml.load(f, Loader=SafeLoader)
    with open(kwhmeter_pvpc_config,'w') as f:                    
        f.write(yaml.dump(config_pvpc))

kwhmeter_influxDB_config=f'{data_dir}/kwhmeter_influxDB_config.yml'

if os.path.exists(kwhmeter_influxDB_config):
    with open(kwhmeter_influxDB_config) as f:
        config_export2 = yaml.load(f, Loader=SafeLoader)
else:
    import pkg_resources
    logging.warning(f"{kwhmeter_influxDB_config} do not exists. Using default one")
    with pkg_resources.resource_stream(__name__, 'data/kwhmeter_influxDB_config.yml') as f:
        config_export2 = yaml.load(f, Loader=SafeLoader)
    with open(kwhmeter_influxDB_config,'w') as f:                    
        f.write(yaml.dump(config_export2))        