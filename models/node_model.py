from utils.config import update_config
import utils.log as logger
import concurrent.futures
from jsonrpclib import Server
import socket
import uuid

class NodeModel:

    def __init__(self, nodes=None, ping_timeout=1):
        self.uuid = uuid.uuid4().hex
        self.peer_nodes = nodes if nodes else []
        self.ping_timeout = ping_timeout

        self.peer_nodes_dict = []
        self.check_nodes_status()

    def set_ping_timeout(self, timeout):
        self.ping_timeout = timeout

    def get_nodes(self):
        return self.peer_nodes
    
    def get_nodes_dict(self):
        return self.peer_nodes_dict
    
    def check_nodes_status(self):
        nodes = []

        def check_node_status(node):
            resp = self.ping(node)
            if not resp:
                return {"node": node, "pong": False, "uuid": None}
            pong = resp.get('pong', False)
            uuid = resp.get('uuid', None)
            return {"node": node, "pong": pong, "uuid": uuid}

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(check_node_status, node) for node in self.peer_nodes]
            for future in concurrent.futures.as_completed(futures):
                nodes.append(future.result())
        self.peer_nodes_dict = nodes

    def add_node(self, node_url):
        if node_url and node_url not in self.peer_nodes:
            # check if node is online
            resp = self.ping(node_url)
            if not resp:
                logger.log_error(f"Failed to add node {node_url}: Node is offline")
                return False
            if resp.get('uuid') == self.uuid:
                logger.log_error(f"Failed to add node {node_url}: Node is the same as current node")
                return False
            if resp.get('pong') == False:
                logger.log_error(f"Failed to add node {node_url}: Node is not a valid node")
                return False
            if resp.get('uuid') in [node.get('uuid') for node in self.peer_nodes_dict]:
                logger.log_error(f"Failed to add node {node_url}: Node already exists")
                return False
            self.peer_nodes.append(node_url)
            self.peer_nodes_dict.append(resp)
            update_config('nodes', self.peer_nodes)
            logger.log_action(f"Added node {node_url}")
            return True
        logger.log_error(f"Failed to add node {node_url}: Node already exists")
        return False
    
    def edit_node(self, node_url, new_node_url):
        if node_url in self.peer_nodes:
            self.peer_nodes.remove(node_url)
            self.peer_nodes_dict = [node for node in self.peer_nodes_dict if node['node'] != node_url]
            update_config('nodes', self.peer_nodes)
            logger.log_action(f"Removed node {node_url}")
            if self.add_node(new_node_url):
                logger.log_action(f"Edited node {node_url} to {new_node_url}")
                return True
            else:
                self.add_node(node_url)
                return False
        logger.log_error(f"Failed to edit node {node_url}: Node not found")
        return False

    def remove_node(self, node_url):
        if node_url in self.peer_nodes:
            self.peer_nodes.remove(node_url)
            self.peer_nodes_dict = [node for node in self.peer_nodes_dict if node['node'] != node_url]
            update_config('nodes', self.peer_nodes)
            logger.log_action(f"Removed node {node_url}")
            return True
        logger.log_error(f"Failed to remove node {node_url}: Node not found")
        return False

    def ping(self, node_url):
        try:
            # WinSock will stuck there if the node is offline
            # so we need to set a timeout and use threading
            server = Server(node_url)
            socket.setdefaulttimeout(self.ping_timeout)
            resp = server.pong()
            resp['node'] = node_url
            socket.setdefaulttimeout(None)
            return resp
        except Exception as e:
            logger.log_error(f"Error pinging {node_url}: {e}")
            return None
        
    def pong(self):
        return {"pong": True, "uuid": self.uuid}