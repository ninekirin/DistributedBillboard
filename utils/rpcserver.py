import socket
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
import utils.log as logger

class RPCServer:
    def __init__(self, controller, ipaddr, port):
        self.controller = controller
        self.ipaddr = ipaddr
        self.port = port
        self.server = None

    def start(self):
        self.server = SimpleJSONRPCServer((self.ipaddr, self.port), logRequests=False)
        self.server.register_function(self.controller.add_image_base64, 'add_image_base64')
        self.server.register_function(self.controller.remove_image, 'remove_image')
        self.server.register_function(self.controller.node_model.pong, 'pong')
        logger.log_action(f"Starting RPC server on {self.ipaddr}:{self.port}")
        self.server.serve_forever()

    def stop(self):
        if self.server:
            self.server.shutdown()
            logger.log_action(f"Stopping RPC server on {self.ipaddr}:{self.port}")

    def is_alive(self):
        if self.server:
            return True
        else:
            return False