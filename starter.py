import threading
import tkinter as tk
from controllers.management_controller import ManagementController
from controllers.display_controller import DisplayController
from utils.config import get_config

fullscreen = get_config('fullscreen', False)
image_switch_interval = get_config('image_switch_interval', 5)
background_color = get_config('background_color', 'black')

def on_key_press(event, management_controller):
    # Listen for 'm' key press to toggle management mode
    if event.char == 'm' or event.char == 'M':
        management_controller.toggle()
    # Listen for 'q' key press to quit
    elif event.char == 'q' or event.char == 'Q':
        root.quit()

if __name__ == "__main__":

    # Create a root window
    root = tk.Tk()
    root.geometry("600x400")
    root.title(f"Distributed Billboard")
    if fullscreen:
        root.attributes('-fullscreen', True)
    root.bind("<F11>", lambda e: root.attributes('-fullscreen', not root.attributes('-fullscreen')))
    root.bind("<Escape>", lambda e: root.attributes('-fullscreen', False))

    # Create display controller
    display_controller = DisplayController(root, background_color, image_switch_interval)

    # Create management controller
    management_controller = ManagementController(root, display_controller)

    # Start JSON-RPC server in a separate thread
    threading.Thread(target=management_controller.start_rpc_server, daemon=True).start()

    root.bind("<Key>", lambda e: on_key_press(e, management_controller))
    
    root.mainloop()
    
    # Stop JSON-RPC server
    management_controller.stop_rpc_server()