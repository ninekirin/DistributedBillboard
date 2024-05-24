import logging
from models.config_model import load_config, save_config
from models.log_model import log_action

config = load_config()
peer_nodes = config.get('nodes', [])

def log_action(action):
    logging.info(action)

class NodeModel:
    def get_nodes(self):
        return peer_nodes

    def add_node(self, node_url):
        if node_url and node_url not in peer_nodes:
            peer_nodes.append(node_url)
            config['nodes'] = peer_nodes
            save_config(config)
            log_action(f"Added node {node_url}")
            return True
        return False

    def remove_node(self, node_url):
        if node_url in peer_nodes:
            peer_nodes.remove(node_url)
            config['nodes'] = peer_nodes
            save_config(config)
            log_action(f"Removed node {node_url}")
            return True
        return False
