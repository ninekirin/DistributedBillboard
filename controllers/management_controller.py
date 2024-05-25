import base64
import os
import socket
import psutil
import threading
import re
import asyncio
from threading import Lock
from tkinter import filedialog, messagebox
from jsonrpclib import Server
from views.management_view import ManagementView
from models.node_model import NodeModel
from models.addrport_model import AddrPortModel
import utils.log as logger
import utils.rpcserver as rpcserver
from utils.config import save_config

class ManagementController:
    def __init__(self, root, display_controller, endpoint_ipaddr, endpoint_port):
        self.root = root
        self.display_controller = display_controller
        
        self.node_model = NodeModel()
        self.image_model = self.display_controller.image_model
        self.addrport_model = AddrPortModel(endpoint_ipaddr, endpoint_port)
        self.management_view = None
        self.rpc_server = None
        self.rpc_server_thread = None
        self.rpc_server_lock = Lock()

    def toggle(self):
        if self.management_view:
            self.destroy()
        else:
            self.show()
            # Bind 'm' key to toggle management view
            self.management_view.management_win.bind("<Key>", lambda e: self.toggle() if e.char == 'm' else None)

    def show(self):
        self.management_view = ManagementView(self.root, self)

    def destroy(self):
        if self.management_view:
            self.management_view.management_win.destroy()
            self.management_view = None

    def add_image(self, url):
        filepath = self.image_model.add_image(url)
        return filepath
    
    def add_image_base64(self, filename, base64data):
        filepath = self.image_model.add_image_base64(filename, base64data)
        self.management_view.image_listbox_add_item(filepath)
        return filepath

    def upload_image(self, url):
        if url.startswith("http://") or url.startswith("https://"):
            filename = self.add_image(url)
            if filename:
                self.distribute_image(filename)
                return filename
        else:
            file_path = filedialog.askopenfilename()
            if file_path:
                local_url = f"file:///{file_path}"
                filename = self.add_image(local_url)
                self.distribute_image(filename)
                return filename
        return None

    def remove_image(self, url, distribution=True):
        self.image_model.remove_image(url)
        # Remove image from image_listbox in management_view (if exists)
        if self.management_view:
            self.management_view.image_listbox_remove_item(url)
        if distribution:
            self.distribute_remove_image(url)

    def add_node(self, node_url):
        self.node_model.add_node(node_url)

    def remove_node(self, node_url):
        self.node_model.remove_node(node_url)

    def get_nodes_with_status(self):
        nodes = self.node_model.get_nodes()
        nodes_status = []
        for node in nodes:
            online_status = self.node_model.is_node_online(node)
            nodes_status.append((node, online_status))
        return nodes_status

    def ping(self, node_url):
        try:
            server = Server(node_url)
            return server.pong()
        except Exception as e:
            logger.log_error(f"Error pinging {node_url}: {e}")
            return False

    def pong(self):
        return 'pong'

    def distribute_image(self, filename):
        nodes = self.node_model.get_nodes()
        for peer in nodes:
            try:
                node = Server(peer)
                with open(filename, "rb") as f:
                    base64data = base64.b64encode(f.read()).decode('utf-8')
                node.add_image_base64(os.path.basename(filename), base64data)
                logger.log_action(f"Distributed image {filename} to {peer}")
            except Exception as e:
                logger.log_error(f"Error distributing to {peer}: {e}")
    
    def distribute_remove_image(self, url):
        nodes = self.node_model.get_nodes()
        for peer in nodes:
            try:
                node = Server(peer)
                node.remove_image(url, False)
                logger.log_action(f"Distributed remove image {url} to {peer}")
            except Exception as e:
                logger.log_error(f"Error distributing remove to {peer}: {e}")

    def get_interfaces(self):
        interfaces = ['0.0.0.0'] #, '::'] # Default interfaces
        regex_public_ipv6 = r"^(?:[0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$"
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    interfaces.append(addr.address)
                # elif addr.family == socket.AF_INET6:
                #     if re.match(regex_public_ipv6, addr.address):
                #         interfaces.append(addr.address)
        return interfaces
    
    def update_server(self, ipaddr, port):
        regex_ipv4 = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
        regex_ipv6 = r"^(?:[0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$"
        if not re.match(regex_ipv4, ipaddr) and not re.match(regex_ipv6, ipaddr):
            logger.log_error(f"Invalid IP address: {ipaddr}")
            messagebox.showerror("Error", "Invalid IP address")
            return
        port = int(port)
        if port < 0 or port > 65535:
            logger.log_error(f"Invalid port: {port}")
            messagebox.showerror("Error", "Invalid port")
            return
        self.addrport_model.update_server(ipaddr, port)
        self.stop_rpc_server()
        self.start_rpc_server()
        logger.log_action(f"Server updated to {ipaddr}:{port}")

    def start_rpc_server(self):
        with self.rpc_server_lock:
            if self.rpc_server and self.rpc_server.is_alive():
                logger.log_error("RPC server is already running.")
                return  # Server is already running
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