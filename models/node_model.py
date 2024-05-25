from utils.config import load_config, save_config
import utils.log as logger
from jsonrpclib import Server
import socket

config = load_config()

ping_timeout = config.get('ping_timeout', 1)

class NodeModel:

    def __init__(self):
        self.peer_nodes = config.get('nodes', [])

    def get_nodes(self):
        return self.peer_nodes

    def add_node(self, node_url):
        if not self.peer_nodes:
            self.peer_nodes = []
        if node_url and node_url not in self.peer_nodes:
            if not node_url.startswith('http'):
                node_url = f'http://{node_url}'
            # check if node is online
            if not self.is_node_online(node_url):
                logger.log_error(f"Failed to add node {node_url}: Node is offline")
                return False
            self.peer_nodes.append(node_url)
            config['nodes'] = self.peer_nodes
            save_config(config)
            logger.log_action(f"Added node {node_url}")
            return True
        logger.log_error(f"Failed to add node {node_url}: Node already exists")
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
            # WinSock will stuck there if the node is offline
            # so we need to set a timeout and use threading
            server = Server(node_url)
            socket.setdefaulttimeout(ping_timeout)
            pong = server.pong()
            socket.setdefaulttimeout(None)
            return pong == 'pong'
        except Exception as e:
            logger.log_error(f"Error pinging {node_url}: {e}")
            return False