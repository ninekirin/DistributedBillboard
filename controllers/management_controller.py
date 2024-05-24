import base64
import os
from tkinter import filedialog, messagebox
from jsonrpclib import Server
from views.management_view import ManagementView
from models.node_model import NodeModel
import models.log_model as logger

class ManagementController:
    def __init__(self, root, display_controller):
        self.root = root
        self.display_controller = display_controller
        self.node_model = NodeModel()
        self.image_model = self.display_controller.image_model
        self.management_view = None

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
            self.distribute_image(filename)
            return filename
        else:
            file_path = filedialog.askopenfilename()
            if file_path:
                local_url = f"file://{file_path}"
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