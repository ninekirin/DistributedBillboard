from utils.config import update_config
import utils.log as logger
from jsonrpclib import Server
import socket

class NodeModel:

    def __init__(self, nodes=None, ping_timeout=1):
        self.peer_nodes = nodes
        self.ping_timeout = ping_timeout

    def set_ping_timeout(self, timeout):
        self.ping_timeout = timeout

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
            update_config('nodes', self.peer_nodes)
            logger.log_action(f"Added node {node_url}")
            return True
        logger.log_error(f"Failed to add node {node_url}: Node already exists")
        return False

    def remove_node(self, node_url):
        if node_url in self.peer_nodes:
            self.peer_nodes.remove(node_url)
            update_config('nodes', self.peer_nodes)
            logger.log_action(f"Removed node {node_url}")
            return True
        return False

    def is_node_online(self, node_url):
        try:
            # WinSock will stuck there if the node is offline
            # so we need to set a timeout and use threading
            server = Server(node_url)
            socket.setdefaulttimeout(self.ping_timeout)
            pong = server.pong()
            socket.setdefaulttimeout(None)
            return pong == 'pong'
        except Exception as e:
            logger.log_error(f"Error pinging {node_url}: {e}")
            return False