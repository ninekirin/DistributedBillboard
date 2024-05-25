import os
import yaml

# Configuration file
config_file = "config.yaml"

def load_config():
    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            yaml.dump({"endpoint_ipaddr": "0.0.0.0", 
                       "endpoint_port": 8000, 
                       "fullscreen": False,
                       "background_color": "black",
                       "image_switch_interval": 5, 
                       "ping_interval": 15,
                       "ping_timeout": 1,
                       "nodes": ["http://localhost:8001"]}, f)
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    return config

def save_config(config):
    with open(config_file, 'w') as f:
        yaml.dump(config, f)

def update_config(key, value):
    config = load_config()
    config[key] = value
    save_config(config)

def get_config(key, default=None):
    config = load_config()
    return config.get(key, default)