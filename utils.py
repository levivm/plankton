import os
import yaml

def get_config():
    conf_file = os.path.dirname(os.path.abspath(__file__)) + "/config.yml"
    with open(conf_file, 'r') as y:
        return yaml.load(y)
