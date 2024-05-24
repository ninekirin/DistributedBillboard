import logging
from models.config_model import load_config, save_config
from models.log_model import log_action

config = load_config()

class NodeModel:

    def __init__(self):
        self.peer_nodes = config.get('nodes', [])

    def get_nodes(self):
        return self.peer_nodes

    def add_node(self, node_url):
        if node_url and node_url not in self.peer_nodes:
            self.peer_nodes.append(node_url)
            config['nodes'] = self.peer_nodes
            save_config(config)
            log_action(f"Added node {node_url}")
            return True
        return False

    def remove_node(self, node_url):
        if node_url in self.peer_nodes:
            self.peer_nodes.remove(node_url)
            config['nodes'] = self.peer_nodes
            save_config(config)
            log_action(f"Removed node {node_url}")
            return True
        return False
