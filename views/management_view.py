import re
import tkinter as tk
import os

class ManagementView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.management_win = tk.Toplevel(self.root)
        self.management_win.title("Manage Billboard")

        # Bind 'Escape' key to destroy management view
        self.management_win.bind("<Escape>", lambda e: self.management_win.destroy())

        # 主框架
        self.main_frame = tk.Frame(self.management_win)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 管理节点部分
        self.node_frame = tk.LabelFrame(self.main_frame, text="Manage Nodes", padx=10, pady=10)
        self.node_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.node_listbox = tk.Listbox(self.node_frame)
        self.node_listbox.grid(row=0, column=0, columnspan=2, sticky="nsew")

        self.node_entry_label = tk.Label(self.node_frame, text="Node URL")
        self.node_entry_label.grid(row=1, column=0, sticky="ew")

        self.node_entry = tk.Entry(self.node_frame)
        self.node_entry.grid(row=1, column=1, sticky="ew")

        self.add_button = tk.Button(self.node_frame, text="Add Node", command=self.add_node)
        self.add_button.grid(row=2, column=0, columnspan=2, sticky="ew")

        self.remove_button = tk.Button(self.node_frame, text="Remove Selected Node", command=self.remove_node)
        self.remove_button.grid(row=3, column=0, columnspan=2, sticky="ew")

        # 上传图片部分
        self.upload_frame = tk.LabelFrame(self.main_frame, text="Uploaded Image", padx=10, pady=10)
        self.upload_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.image_listbox = tk.Listbox(self.upload_frame)
        self.image_listbox.grid(row=0, column=0, columnspan=2, sticky="nsew")

        for image in self.controller.image_model.get_images():
            self.image_listbox.insert(tk.END, image)

        self.image_entry_label = tk.Label(self.upload_frame, text="Image URL")
        self.image_entry_label.grid(row=1, column=0, sticky="ew")

        self.image_entry = tk.Entry(self.upload_frame)
        self.image_entry.grid(row=1, column=1, sticky="ew")

        self.upload_img_button = tk.Button(self.upload_frame, text="Upload Image", command=self.upload_image)
        self.upload_img_button.grid(row=2, column=0, columnspan=2, sticky="ew")

        self.remove_img_button = tk.Button(self.upload_frame, text="Remove Selected Image", command=self.remove_image)
        self.remove_img_button.grid(row=3, column=0, columnspan=2, sticky="ew")

        # 接口信息部分
        self.interface_frame = tk.LabelFrame(self.main_frame, text="Interface Info (Double Click to Copy)", padx=10, pady=10)
        self.interface_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.interface_listbox = tk.Listbox(self.interface_frame)
        self.interface_listbox.grid(row=0, column=0, columnspan=2, sticky="nsew")

        # Populate interface listbox with dummy data for demonstration
        interfaces = self.controller.get_interfaces()
        for interface in interfaces:
            self.interface_listbox.insert(tk.END, interface)

        # 配置网格布局
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        
        self.node_frame.grid_rowconfigure(0, weight=1)
        self.node_frame.grid_rowconfigure(1, weight=0)
        self.node_frame.grid_rowconfigure(2, weight=0)
        self.node_frame.grid_rowconfigure(3, weight=0)
        self.node_frame.grid_columnconfigure(0, weight=1)
        self.node_frame.grid_columnconfigure(1, weight=1)

        self.upload_frame.grid_rowconfigure(0, weight=1)
        self.upload_frame.grid_rowconfigure(1, weight=0)
        self.upload_frame.grid_rowconfigure(2, weight=0)
        self.upload_frame.grid_rowconfigure(3, weight=0)
        self.upload_frame.grid_columnconfigure(0, weight=1)
        self.upload_frame.grid_columnconfigure(1, weight=1)

        self.interface_frame.grid_rowconfigure(0, weight=1)
        self.interface_frame.grid_columnconfigure(0, weight=1)
        self.interface_frame.grid_columnconfigure(1, weight=1)

        # Bind double-click events
        self.node_listbox.bind("<Double-1>", self.on_node_double_click)
        self.image_listbox.bind("<Double-1>", self.on_image_double_click)
        self.interface_listbox.bind("<Double-1>", self.on_interface_double_click)

        # Schedule regular updates for node statuses
        self.schedule_status_updates()

    def add_node(self):
        node_url = self.node_entry.get()
        regex = r"^(http|https)://[a-zA-Z0-9.-]+(:[0-9]+)?/?$"
        if re.match(regex, node_url):
            self.controller.add_node(node_url)
            self.update_node_listbox()
            self.node_entry.delete(0, tk.END)

    def remove_node(self):
        selected = self.node_listbox.curselection()
        if selected:
            node_info = self.node_listbox.get(selected)
            node_url = node_info.split(' - ')[0]
            self.controller.remove_node(node_url)
            self.update_node_listbox()

    def upload_image(self):
        url = self.image_entry.get()
        filename = self.controller.upload_image(url)
        if filename:
            self.image_listbox.insert(tk.END, filename)
            self.image_entry.delete(0, tk.END)

    def remove_image(self):
        selected = self.image_listbox.curselection()
        if selected:
            url = self.image_listbox.get(selected)
            self.controller.remove_image(url)

    def image_listbox_add_item(self, item):
        self.image_listbox.insert(tk.END, item)

    def image_listbox_remove_item(self, item):
        index = self.image_listbox.get(0, tk.END).index(item)
        self.image_listbox.delete(index)

    def node_listbox_add_item(self, item):
        self.node_listbox.insert(tk.END, item)

    def node_listbox_remove_item(self, item):
        index = self.node_listbox.get(0, tk.END).index(item)
        self.node_listbox.delete(index)

    def update_node_listbox(self):
        # get selected index
        selected = self.node_listbox.curselection()
        self.node_listbox.delete(0, tk.END)
        for node, status in self.controller.get_nodes_with_status():
            status_text = "Online" if status else "Offline"
            self.node_listbox.insert(tk.END, f"{node} - {status_text}")
        if selected:
            self.node_listbox.selection_set(selected)

    def on_node_double_click(self, event):
        selected = self.node_listbox.curselection()
        if selected:
            node_info = self.node_listbox.get(selected)
            node_url = node_info.split(' - ')[0]
            self.node_entry.delete(0, tk.END)
            self.node_entry.insert(0, node_url)

    def on_image_double_click(self, event):
        selected = self.image_listbox.curselection()
        if selected:
            filename = self.image_listbox.get(selected)
            if os.name == 'posix':  # for macOS or Linux
                os.system(f'open "{filename}"')
            elif os.name == 'nt':  # for Windows
                os.startfile(filename)

    def on_interface_double_click(self, event):
        selected = self.interface_listbox.curselection()
        if selected:
            interface_info = self.interface_listbox.get(selected)
            ip = interface_info.split(':')[0]
            self.root.clipboard_clear()
            self.root.clipboard_append(ip)
            self.root.update()  # now it stays on the clipboard

    def schedule_status_updates(self):
        self.update_node_listbox()
        self.management_win.after(5000, self.schedule_status_updates)  # Update every 5 seconds