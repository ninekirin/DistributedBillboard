import os
import tkinter as tk
from tkinter import filedialog, messagebox
from views.management_view import ManagementView
from models.node_model import NodeModel
from models.image_model import ImageModel

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
            self.image_model.distribute_image(filename)
            return filename
        else:
            file_path = filedialog.askopenfilename()
            if file_path:
                local_url = f"file://{file_path}"
                filename = self.add_image(local_url)
                self.image_model.distribute_image(filename)
                return filename
        return None

    def remove_image(self, url, distribution=True):
        self.image_model.remove_image(url)
        # Remove image from image_listbox in management_view (if exists)
        if self.management_view:
            self.management_view.image_listbox_remove_item(url)
        if distribution:
            self.image_model.distribute_remove_image(url)

    def add_node(self, node_url):
        if self.node_model.add_node(node_url):
            messagebox.showinfo("Node Added", f"Node {node_url} added successfully")

    def remove_node(self, node_url):
        if self.node_model.remove_node(node_url):
            messagebox.showinfo("Node Removed", f"Node {node_url} removed successfully")
