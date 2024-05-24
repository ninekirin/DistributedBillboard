import os
import yaml

# 加载或初始化配置
config_file = "config.yaml"

def load_config():
    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            yaml.dump({"nodes": ["http://localhost:8001"], "endpoint_port": 8000}, f)
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    return config

def save_config(config):
    with open(config_file, 'w') as f:
        yaml.dump(config, f)