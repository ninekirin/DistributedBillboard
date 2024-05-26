import tkinter as tk
from controllers.management_controller import ManagementController
from controllers.display_controller import DisplayController
from utils.config import get_config

fullscreen = get_config('fullscreen', False)
image_switch_interval = get_config('image_switch_interval', 5)
background_color = get_config('background_color', 'black')

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
    management_controller.start_rpc_server()

    # Listen for 'm' key press to toggle management mode
    root.bind("<Key>", lambda e: management_controller.toggle() if e.char == 'm' or e.char == 'M' else None)

    # Listen for 'q' key press to quit
    root.bind("<Key>", lambda e: root.quit() if e.char == 'q' or e.char == 'Q' else None)
    
    root.mainloop()