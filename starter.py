import threading
import tkinter as tk
from controllers.management_controller import ManagementController
from controllers.display_controller import DisplayController
from utils.config import load_config
from utils.rpcserver import start_rpc_server

config = load_config()
endpoint_ipv4 = config.get('endpoint_ipv4', '0.0.0.0')
endpoint_port = config.get('endpoint_port', 8000)
fullscreen = config.get('fullscreen', False)
background_color = config.get('background_color', 'black')

if __name__ == "__main__":

    # Create a root window
    root = tk.Tk()
    root.geometry("600x600")
    root.title(f"Distributed Billboard")
    if fullscreen:
        root.attributes('-fullscreen', True)
    root.bind("<F11>", lambda e: root.attributes('-fullscreen', not root.attributes('-fullscreen')))
    root.bind("<Escape>", lambda e: root.attributes('-fullscreen', False))

    # Create display controller
    display_controller = DisplayController(root)

    # Create management controller
    management_controller = ManagementController(root, display_controller, endpoint_ipv4, endpoint_port)

    # Start JSON-RPC server in a separate thread
    # threading.Thread(target=start_rpc_server, args=(management_controller, endpoint_ipv4, endpoint_port), daemon=True).start()
    management_controller.start_rpc_server()

    # Listen for 'm' key press to toggle management mode
    root.bind("<Key>", lambda e: management_controller.toggle() if e.char == 'm' else None)
    
    root.mainloop()