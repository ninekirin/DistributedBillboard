import socket
from utils.config import load_config, save_config
import utils.log as logger

class AddrPortModel:
    def __init__(self, endpoint_ipaddr, endpoint_port):
        self.config = load_config()
        self.endpoint_ipaddr = endpoint_ipaddr
        self.endpoint_port = endpoint_port

    def update_server(self, ipaddr, port):
        self.endpoint_ipaddr = ipaddr
        self.endpoint_port = port
        self.config['endpoint_ipaddr'] = ipaddr
        self.config['endpoint_port'] = port
        save_config(self.config)
        return True
    
    def get_server(self):
        return self.endpoint_ipaddr, self.endpoint_port
    
    def get_server_ipaddr(self):
        return self.endpoint_ipaddr
    
    def get_server_port(self):
        return self.endpoint_port
    
    def get_server_url(self):
        return f"http://{self.endpoint_ipaddr}:{self.endpoint_port}"
    
    def is_address_valid(self, ipaddr):
        try:
            socket.inet_aton(ipaddr)
            return True
        except socket.error:
            return False
        
    def is_port_valid(self, port):
        return 0 <= port <= 65535
    
    def is_port_in_use(self, ipaddr, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex((ipaddr, port)) == 0