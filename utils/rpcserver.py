from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
import utils.log as logger

def start_rpc_server(controller, ip, port):
    server = SimpleJSONRPCServer((ip, port), logRequests=False)
    server.register_function(controller.add_image_base64, 'add_image_base64')
    server.register_function(controller.remove_image, 'remove_image')
    server.register_function(controller.pong, 'pong')
    logger.log_action(f"Starting RPC server on {ip}:{port}")
    server.serve_forever()