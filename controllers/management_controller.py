import base64
import os
import socket
import psutil
import threading
from threading import Lock
from tkinter import filedialog, messagebox
from jsonrpclib import Server
from utils.config import get_config, update_config
from views.management_view import ManagementView
from models.node_model import NodeModel
from models.addrport_model import AddrPortModel
import utils.log as logger
import utils.rpcserver as rpcserver
from models.image_model import extentions

class ManagementController:
    def __init__(self, root, display_controller):
        self.root = root
        self.display_controller = display_controller
        
        self.node_model = NodeModel(get_config('nodes', []), get_config('ping_timeout', 1))
        self.image_model = self.display_controller.image_model
        self.addrport_model = AddrPortModel(get_config('endpoint_ipaddr', '0.0.0.0'), get_config('endpoint_port', 8000))

        self.rpc_server = None
        self.rpc_server_thread = None
        self.rpc_server_lock = Lock()
        self.ping_interval = get_config('ping_interval', 15)

        self.management_view = ManagementView(self.root, self)

        # hide management_view by default
        self.management_view.management_win.withdraw()

    def toggle(self):
        if self.management_view.management_win.state() == "normal":
            self.management_view.management_win.withdraw()
        elif self.management_view.management_win.state() == "withdrawn":
            self.management_view.management_win.deiconify()

    def add_image(self, url):
        filepath = self.image_model.add_image(url)
        if self.management_view.management_win.winfo_exists():
            self.management_view.update_image_listbox()
        if filepath:
            return filepath
        return None
    
    def add_image_base64(self, filename, base64data, distribution=True):
        filepath = self.image_model.add_image_base64(filename, base64data)
        # self.management_view.image_listbox_add_item(filepath)
        if self.management_view.management_win.winfo_exists():
            self.management_view.update_image_listbox()
        if filepath:
            return filepath
        return None

    def upload_image(self, url):
        if url.startswith(("http://", "https://")):
            filename = self.add_image(url)
            if filename:
                # self.distribute_image(filename)
                threading.Thread(target=self.distribute_image, args=(filename,), daemon=True).start()
                return filename
        else:
            file_path = filedialog.askopenfilename(filetypes=[("Image files", extentions)], title="Select Image File")
            url_prefix = "file://" # Default to Unix-like systems
            if file_path:
                if os.name == "nt": # Windows
                    url_prefix = "file:///"
                local_url = f"{url_prefix}{file_path}"
                filename = self.add_image(local_url)
                if filename:
                    # self.distribute_image(filename)
                    threading.Thread(target=self.distribute_image, args=(filename,), daemon=True).start()
                    return filename
        return None
    
    def remove_image(self, url, distribution=True):
        self.image_model.remove_image(url)
        # Remove image from image_listbox in management_view (if exists)
        if self.management_view.management_win.winfo_exists():
            self.management_view.update_image_listbox()
        if distribution:
            # self.distribute_remove_image(url)
            threading.Thread(target=self.distribute_remove_image, args=(url,), daemon=True).start()

    def add_node(self, node_url):
        return self.node_model.add_node(node_url)
    
    def edit_node(self, node_url, new_node_url):
        return self.node_model.edit_node(node_url, new_node_url)

    def remove_node(self, node_url):
        return self.node_model.remove_node(node_url)
    
    def get_nodes(self):
        return self.node_model.get_nodes()
    
    def get_nodes_dict(self):
        return self.node_model.get_nodes_dict()
    
    def debug_get_nodes_dict(self):
        logger.log_action(self.node_model.get_nodes_dict())
    
    def get_image_list(self):
        return self.image_model.get_image_list()

    def distribute_image(self, filename):
        nodes = self.node_model.get_nodes_dict()
        for peer in [node for node in nodes if node['uuid'] != self.node_model.uuid]:
            try:
                if peer['pong']:
                    node = Server(peer['node'])
                    with open(filename, "rb") as f:
                        base64data = base64.b64encode(f.read()).decode('utf-8')
                    node.add_image_base64(os.path.basename(filename), base64data, True)
                    logger.log_action(f"Distributed image {filename} to {peer['node']}")
            except Exception as e:
                logger.log_error(f"Error distributing to {peer}: {e}")
    
    def distribute_remove_image(self, url):
        nodes = self.node_model.get_nodes_dict()
        for peer in [node for node in nodes if node['uuid'] != self.node_model.uuid]:
            try:
                if peer['pong']:
                    node = Server(peer['node'])
                    node.remove_image(url, True)
                    logger.log_action(f"Distributed remove image {url} to {peer['node']}")
            except Exception as e:
                logger.log_error(f"Error distributing remove to {peer}: {e}")

    def get_interfaces(self):
        interfaces = ['0.0.0.0'] # Default interfaces
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    interfaces.append(addr.address)
        return interfaces

    def check_server(self, ipaddr, port):
        if not self.addrport_model.is_address_valid(ipaddr):
            logger.log_error(f"Invalid IP address: {ipaddr}")
            return
        if not self.addrport_model.is_port_valid(port):
            logger.log_error(f"Invalid port: {port}")
            return
        return True

    def update_server(self, ipaddr, port):
        if not self.check_server(ipaddr, port):
            return False
        self.addrport_model.update_server(ipaddr, port)
        logger.log_action(f"Server updated to {ipaddr}:{port}")
        self.stop_rpc_server()
        self.start_rpc_server()

    def start_rpc_server(self):
        with self.rpc_server_lock:
            if self.rpc_server and self.rpc_server.is_alive():
                logger.log_error("RPC server is already running.")
                return  # Server is already running
            # Check if IP address and port are valid
            if not self.check_server(self.addrport_model.endpoint_ipaddr, self.addrport_model.endpoint_port):
                return
            if self.addrport_model.is_port_in_use(self.addrport_model.endpoint_ipaddr, self.addrport_model.endpoint_port):
                logger.log_error(f"Port {self.addrport_model.endpoint_port} is already in use on {self.addrport_model.endpoint_ipaddr}")
                return
            self.rpc_server = rpcserver.RPCServer(self, self.addrport_model.endpoint_ipaddr, self.addrport_model.endpoint_port)
            self.rpc_server_thread = threading.Thread(target=self.rpc_server.start, daemon=True)
            self.rpc_server_thread.start()

    def stop_rpc_server(self):
        with self.rpc_server_lock:
            if self.rpc_server and self.rpc_server.is_alive():
                self.rpc_server.stop()
                self.rpc_server_thread.join()  # Wait up to 5 seconds for the thread to terminate
                if self.rpc_server_thread.is_alive():
                    logger.log_error("Failed to stop RPC server properly.")
                else:
                    self.rpc_server = None
                    logger.log_action(f"Stopped RPC server on {self.addrport_model.endpoint_ipaddr}:{self.addrport_model.endpoint_port}")

    def load_settings(self):
        return {
            'fullscreen': get_config('fullscreen', False),
            'background_color': get_config('background_color', 'skyblue'),
            'image_switch_interval': get_config('image_switch_interval', 15),
            'ping_interval': get_config('ping_interval', 15),
            'ping_timeout': get_config('ping_timeout', 1)
        }

    def save_settings(self, settings):
        """
        fullscreen: false
        background_color: skyblue
        image_switch_interval: 15
        ping_interval: 15
        ping_timeout: 1
        """
        update_config('fullscreen', settings['fullscreen'])
        update_config('background_color', settings['background_color'])
        update_config('image_switch_interval', settings['image_switch_interval'])
        update_config('ping_interval', settings['ping_interval'])
        update_config('ping_timeout', settings['ping_timeout'])
        # Set fullscreen
        self.root.attributes('-fullscreen', settings['fullscreen'])
        # Set display_controller settings
        self.display_controller.set_background_color(settings['background_color'])
        self.display_controller.set_image_switch_interval(settings['image_switch_interval'])
        # Set ping_interval
        self.ping_interval = settings['ping_interval']
        # Set ping_timeout
        self.node_model.set_ping_timeout(settings['ping_timeout'])
        logger.log_action("Settings saved")