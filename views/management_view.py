import re
import threading
import tkinter as tk
import os
from tkinter import ttk, messagebox

class ManagementView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.management_win = tk.Toplevel(self.root)
        self.management_win.title("Manage Billboard")

        # Bind 'Escape' key to deiconify management view
        self.management_win.bind("<Escape>", lambda e: self.management_win.deiconify())
        # Main frame
        self.main_frame = tk.Frame(self.management_win)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Notebook
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Image management part
        self.upload_frame = tk.Frame(self.notebook)
        self.notebook.add(self.upload_frame, text="Images")

        self.image_listbox = tk.Listbox(self.upload_frame)
        self.image_listbox.grid(row=0, column=0, columnspan=2, sticky="nsew")

        for image in self.controller.image_model.get_image_list():
            self.image_listbox.insert(tk.END, image)

        self.image_entry_label = tk.Label(self.upload_frame, text="Image URL")
        self.image_entry_label.grid(row=1, column=0, sticky="ew")

        self.image_var = tk.StringVar()
        self.image_entry = tk.Entry(self.upload_frame, textvariable=self.image_var)
        self.image_entry.grid(row=1, column=1, sticky="ew")
        self.image_var.trace_add("write", lambda name, index, mode: self.update_upload_button_text())

        self.upload_img_button = tk.Button(self.upload_frame, text="Select Image From Filesystem", command=self.upload_image)
        self.upload_img_button.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.update_upload_button_text()

        self.remove_img_button = tk.Button(self.upload_frame, text="Remove Selected Image", command=self.remove_image)
        self.remove_img_button.grid(row=3, column=0, columnspan=2, sticky="ew")

        # Node management part
        self.node_frame = tk.Frame(self.notebook)
        self.notebook.add(self.node_frame, text="Nodes")

        self.node_listbox = tk.Listbox(self.node_frame)
        self.node_listbox.grid(row=0, column=0, columnspan=2, sticky="nsew")

        self.node_entry_label = tk.Label(self.node_frame, text="Node URL")
        self.node_entry_label.grid(row=1, column=0, sticky="ew")

        self.node_entry = tk.Entry(self.node_frame)
        self.node_entry.grid(row=1, column=1, sticky="ew")

        self.add_button = tk.Button(self.node_frame, text="Add Node", command=self.add_node)
        self.add_button.grid(row=2, column=0, columnspan=2, sticky="ew")

        self.edit_button = tk.Button(self.node_frame, text="Edit Selected Node", command=self.edit_node)
        self.edit_button.grid(row=3, column=0, columnspan=2, sticky="ew")

        self.remove_button = tk.Button(self.node_frame, text="Remove Selected Node", command=self.remove_node)
        self.remove_button.grid(row=4, column=0, columnspan=2, sticky="ew")

        # Interface and server management part
        self.interface_server_frame = tk.Frame(self.notebook)
        self.notebook.add(self.interface_server_frame, text="Interface")

        self.interface_listbox = tk.Listbox(self.interface_server_frame)
        self.interface_listbox.grid(row=0, column=0, columnspan=2, sticky="nsew")

        interfaces = self.controller.get_interfaces()
        for interface in interfaces:
            self.interface_listbox.insert(tk.END, interface)

        self.server_ip_label = tk.Label(self.interface_server_frame, text="Interface IP Address")
        self.server_ip_label.grid(row=1, column=0, sticky="ew")

        self.server_ip_entry = tk.Entry(self.interface_server_frame)
        self.server_ip_entry.grid(row=1, column=1, sticky="ew")
        self.server_ip_entry.insert(0, self.controller.addrport_model.endpoint_ipaddr)

        self.server_port_label = tk.Label(self.interface_server_frame, text="Server Port")
        self.server_port_label.grid(row=2, column=0, sticky="ew")

        self.server_port_entry = tk.Entry(self.interface_server_frame)
        self.server_port_entry.grid(row=2, column=1, sticky="ew")
        self.server_port_entry.insert(0, self.controller.addrport_model.endpoint_port)

        self.update_server_button = tk.Button(self.interface_server_frame, text="Update Server", command=self.update_server)
        self.update_server_button.grid(row=3, column=0, columnspan=2, sticky="ew")

        # Other settings part
        self.other_frame = tk.Frame(self.notebook)
        self.notebook.add(self.other_frame, text="Other")
        """
        fullscreen: false
        background_color: skyblue
        image_switch_interval: 15
        ping_interval: 15
        ping_timeout: 1
        """
        self.fullscreen_var = tk.BooleanVar()
        self.fullscreen_check = tk.Checkbutton(self.other_frame, text="Fullscreen", variable=self.fullscreen_var)
        self.fullscreen_check.grid(row=0, column=0, sticky="ew")

        self.bg_color_label = tk.Label(self.other_frame, text="Background Color")
        self.bg_color_label.grid(row=1, column=0, sticky="ew")

        self.bg_color_entry = tk.Entry(self.other_frame)
        self.bg_color_entry.grid(row=1, column=1, sticky="ew")

        self.img_switch_interval_label = tk.Label(self.other_frame, text="Image Switch Interval (s)")
        self.img_switch_interval_label.grid(row=2, column=0, sticky="ew")

        self.img_switch_interval_entry = tk.Entry(self.other_frame)
        self.img_switch_interval_entry.grid(row=2, column=1, sticky="ew")

        self.ping_interval_label = tk.Label(self.other_frame, text="Ping Interval (s)")
        self.ping_interval_label.grid(row=3, column=0, sticky="ew")

        self.ping_interval_entry = tk.Entry(self.other_frame)
        self.ping_interval_entry.grid(row=3, column=1, sticky="ew")

        self.ping_timeout_label = tk.Label(self.other_frame, text="Ping Timeout (s)")
        self.ping_timeout_label.grid(row=4, column=0, sticky="ew")

        self.ping_timeout_entry = tk.Entry(self.other_frame)
        self.ping_timeout_entry.grid(row=4, column=1, sticky="ew")

        self.save_button = tk.Button(self.other_frame, text="Save Settings", command=self.save_settings)
        self.save_button.grid(row=5, column=0, columnspan=2, sticky="ew")

        # debug button: get nodes
        self.get_nodes_button = tk.Button(self.other_frame, text="Debug: Get Nodes", command=self.controller.debug_get_nodes_dict)
        self.get_nodes_button.grid(row=6, column=0, columnspan=2, sticky="ew")

        # Grid configuration
        self.node_frame.grid_rowconfigure(0, weight=1)
        self.node_frame.grid_rowconfigure(1, weight=0)
        self.node_frame.grid_rowconfigure(2, weight=0)
        self.node_frame.grid_rowconfigure(3, weight=0)
        self.node_frame.grid_rowconfigure(4, weight=0)
        self.node_frame.grid_columnconfigure(0, weight=1)
        self.node_frame.grid_columnconfigure(1, weight=1)

        self.upload_frame.grid_rowconfigure(0, weight=1)
        self.upload_frame.grid_rowconfigure(1, weight=0)
        self.upload_frame.grid_rowconfigure(2, weight=0)
        self.upload_frame.grid_rowconfigure(3, weight=0)
        self.upload_frame.grid_columnconfigure(0, weight=1)
        self.upload_frame.grid_columnconfigure(1, weight=1)

        self.interface_server_frame.grid_rowconfigure(0, weight=1)
        self.interface_server_frame.grid_rowconfigure(1, weight=0)
        self.interface_server_frame.grid_rowconfigure(2, weight=0)
        self.interface_server_frame.grid_rowconfigure(3, weight=0)
        self.interface_server_frame.grid_columnconfigure(0, weight=1)
        self.interface_server_frame.grid_columnconfigure(1, weight=1)

        self.other_frame.grid_rowconfigure(0, weight=0)
        self.other_frame.grid_rowconfigure(1, weight=0)
        self.other_frame.grid_rowconfigure(2, weight=0)
        self.other_frame.grid_rowconfigure(3, weight=0)
        self.other_frame.grid_rowconfigure(4, weight=0)
        self.other_frame.grid_rowconfigure(5, weight=0)
        self.other_frame.grid_rowconfigure(6, weight=0)
        self.other_frame.grid_columnconfigure(0, weight=1)
        self.other_frame.grid_columnconfigure(1, weight=1)

        # Bind double-click events
        self.node_listbox.bind("<Double-1>", self.on_node_double_click)
        self.image_listbox.bind("<Double-1>", self.on_image_double_click)
        # Bind click event for interface listbox
        self.interface_listbox.bind("<<ListboxSelect>>", self.on_interface_click)

        # Bind 'Escape' key to deiconify management view
        self.management_win.bind("<Escape>", lambda e: self.management_win.withdraw())

        # Schedule regular updates for node statuses
        self.schedule_status_updates()

        # Load settings
        self.load_settings()

        # On close event: hide instead of closing
        self.management_win.protocol("WM_DELETE_WINDOW", self.management_win.withdraw)

    def on_closing(self):
        self.management_win.withdraw()

    def add_node(self):
        node_url = self.node_entry.get()
        regex = r"^(http|https)://[a-zA-Z0-9.-]+(:[0-9]+)?/?$"
        if re.match(regex, node_url):
            if not self.controller.add_node(node_url):
                messagebox.showerror("Error", "Failed to add node, please check the logs")
                # focus on the entry
                self.node_entry.focus_set()
                return
            self.update_node_listbox()
            self.node_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Invalid URL", "Invalid URL format.\nPlease enter a valid URL.\nExample: http://127.0.0.1:6000")
            # focus on the entry
            self.node_entry.focus_set()

    def edit_node(self):
        regex = r"^(http|https)://[a-zA-Z0-9.-]+(:[0-9]+)?/?$"
        # get node_url and new_node_url
        selected = self.node_listbox.curselection()
        if selected:
            node_info = self.node_listbox.get(selected)
            node_url = node_info.split(' - ')[0]
            new_node_url = self.node_entry.get()
            if node_url == new_node_url:
                messagebox.showerror("Error", "New node URL is the same as the current node URL.")
                # focus on the entry
                self.node_listbox.focus_set()
                return
            if re.match(regex, new_node_url):
                if not self.controller.edit_node(node_url, new_node_url):
                    messagebox.showerror("Error", "Failed to edit node, please check the logs")
                    # focus on the entry
                    self.node_listbox.focus_set()
                    return
                self.update_node_listbox()
                self.node_entry.delete(0, tk.END)
                # focus on the item
                self.node_listbox.selection_set(selected)
            else:
                messagebox.showerror("Invalid URL", "Invalid URL format.\nPlease enter a valid URL.\nExample: http://127.0.0.1:6000")
                # focus on the entry
                self.node_listbox.focus_set()
        else:
            messagebox.showerror("Error", "Please select a node to edit.")
            # focus on the entry
            self.node_listbox.focus_set()

    def remove_node(self):
        selected = self.node_listbox.curselection()
        if selected:
            node_info = self.node_listbox.get(selected)
            node_url = node_info.split(' - ')[0]
            if self.controller.remove_node(node_url):
                self.update_node_listbox()

    def upload_image(self):
        url = self.image_entry.get()
        self.controller.upload_image(url)

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

    def update_upload_button_text(self):
        if self.image_entry.get().startswith(('http://', 'https://')):
            self.upload_img_button.config(text="Download Image From Remote")
        else:
            self.upload_img_button.config(text="Select Image From Filesystem")

    def update_image_listbox(self):
        selected = self.image_listbox.curselection()
        images = self.controller.image_model.get_image_list()
        self.image_listbox.delete(0, tk.END)
        for image in images:
            self.image_listbox.insert(tk.END, image)
        if selected:
            self.image_listbox.selection_set(selected)

    def update_node_listbox(self):
        # get selected index
        selected = self.node_listbox.curselection()
        def update():
            try:
                nodes_with_status = self.controller.get_nodes_dict()
                self.node_listbox.delete(0, tk.END)
                for node in nodes_with_status:
                    node_url = node['node']
                    status = "Online" if node['pong'] else "Offline"
                    self.node_listbox.insert(tk.END, f"{node_url} - {status}")
                if selected:
                    self.node_listbox.selection_set(selected)
            except Exception as e:
                pass
        threading.Thread(target=update).start()

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

    def on_interface_click(self, event):
        selected = self.interface_listbox.curselection()
        if selected:
            interface_info = self.interface_listbox.get(selected)
            ip = interface_info
            self.root.clipboard_clear()
            self.root.clipboard_append(ip)
            self.root.update()  # now it stays on the clipboard
            self.server_ip_entry.delete(0, tk.END)
            self.server_ip_entry.insert(0, ip)

    def update_server(self):
        ip = self.server_ip_entry.get()
        port = self.server_port_entry.get()
        if ip and port:
            try:
                port = int(port)
                if not self.controller.update_server(ip, port):
                    messagebox.showerror("Error", "Invalid IP address or port, or port is already in use.")
            except ValueError:
                messagebox.showerror("Invalid Port", "Port must be a number.")
                self.server_port_entry.focus_set()
        else:
            messagebox.showerror("Invalid Input", "IP and Port cannot be empty.")
            self.server_ip_entry.focus_set()

    def schedule_status_updates(self):
        threading.Thread(target=self.update_node_listbox).start()
        ping_interval = self.controller.ping_interval
        self.management_win.after(ping_interval * 1000, self.schedule_status_updates)

    def load_settings(self):
        settings = self.controller.load_settings()
        self.fullscreen_var.set(settings['fullscreen'])
        self.bg_color_entry.insert(0, settings['background_color'])
        self.img_switch_interval_entry.insert(0, settings['image_switch_interval'])
        self.ping_interval_entry.insert(0, settings['ping_interval'])
        self.ping_timeout_entry.insert(0, settings['ping_timeout'])

    def save_settings(self):
        # Validate input (ping_interval and ping_timeout must be greater than 0)
        if not self.ping_interval_entry.get().isdigit() or int(self.ping_interval_entry.get()) <= 0:
            messagebox.showerror("Invalid Input", "Ping Interval must be a positive integer.")
            self.ping_interval_entry.focus_set()
            return
        if not self.ping_timeout_entry.get().isdigit() or int(self.ping_timeout_entry.get()) <= 0:
            messagebox.showerror("Invalid Input", "Ping Timeout must be a positive integer.")
            self.ping_timeout_entry.focus_set()
            return
        if not self.img_switch_interval_entry.get().isdigit() or int(self.img_switch_interval_entry.get()) <= 0:
            messagebox.showerror("Invalid Input", "Image Switch Interval must be a positive integer.")
            self.img_switch_interval_entry.focus_set()
            return
        settings = {
            'fullscreen': self.fullscreen_var.get(),
            'background_color': self.bg_color_entry.get(),
            'image_switch_interval': int(self.img_switch_interval_entry.get()),
            'ping_interval': int(self.ping_interval_entry.get()),
            'ping_timeout': int(self.ping_timeout_entry.get())
        }
        self.controller.save_settings(settings)