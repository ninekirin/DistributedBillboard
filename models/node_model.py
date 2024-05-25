from utils.config import load_config, save_config
import utils.log as logger
from jsonrpclib import Server

config = load_config()

class NodeModel:

    def __init__(self):
        self.peer_nodes = config.get('nodes', [])

    def get_nodes(self):
        return self.peer_nodes

    def add_node(self, node_url):
        if not self.peer_nodes:
            self.peer_nodes = []
        if node_url and node_url not in self.peer_nodes:
            self.peer_nodes.append(node_url)
            config['nodes'] = self.peer_nodes
            save_config(config)
            logger.log_action(f"Added node {node_url}")
            return True
        return False

    def remove_node(self, node_url):
        if node_url in self.peer_nodes:
            self.peer_nodes.remove(node_url)
            config['nodes'] = self.peer_nodes
            save_config(config)
            logger.log_action(f"Removed node {node_url}")
            return True
        return False
    
    def is_node_online(self, node_url):
        try:
            server = Server(node_url)
            return server.pong() == 'pong'
        except Exception as e:
            logger.log_error(f"Error pinging {node_url}: {e}")
            return False

