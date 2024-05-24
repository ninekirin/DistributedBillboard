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