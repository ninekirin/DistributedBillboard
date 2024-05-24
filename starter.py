import threading
import tkinter as tk
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
from controllers.management_controller import ManagementController
from controllers.display_controller import DisplayController
from utils.config import load_config

config = load_config()
endpoint_ipv4 = config.get('endpoint_ipv4', '0.0.0.0')
endpoint_port = config.get('endpoint_port', 8000)
fullscreen = config.get('fullscreen', False)
background_color = config.get('background_color', 'black')

if __name__ == "__main__":

    # Create a root window
    root = tk.Tk()
    root.geometry("600x600")
    root.title(f"Billboard - http://{endpoint_ipv4}:{endpoint_port}")
    if fullscreen:
        root.attributes('-fullscreen', True)
    root.bind("<F11>", lambda e: root.attributes('-fullscreen', not root.attributes('-fullscreen')))
    root.bind("<Escape>", lambda e: root.attributes('-fullscreen', False))

    # Create display controller
    display_controller = DisplayController(root)

    # Create management controller
    management_controller = ManagementController(root, display_controller)

    # Create JSON-RPC server
    server = SimpleJSONRPCServer((endpoint_ipv4, endpoint_port),logRequests=False)
    server.register_function(management_controller.add_image_base64, 'add_image_base64')
    server.register_function(management_controller.remove_image, 'remove_image')
    server.register_function(management_controller.pong, 'pong')
    threading.Thread(target=server.serve_forever, daemon=True).start()

    # Listen for 'm' key press to toggle management mode
    root.bind("<Key>", lambda e: management_controller.toggle() if e.char == 'm' else None)
    
    root.mainloop()
