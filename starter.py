import threading
import tkinter as tk
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
from controllers.management_controller import ManagementController
from controllers.display_controller import DisplayController
from models.config_model import load_config

config = load_config()
endpoint_port = config.get('endpoint_port', 8000)

if __name__ == "__main__":

    # 创建Tkinter主界面
    root = tk.Tk()
    root.geometry("600x400")
    # root.attributes('-fullscreen', True)
    root.bind("<F11>", lambda e: root.attributes('-fullscreen', not root.attributes('-fullscreen')))
    root.bind("<Escape>", lambda e: root.attributes('-fullscreen', False))

    # 创建显示控制器
    display_controller = DisplayController(root)
    
    # 创建管理控制器
    management_controller = ManagementController(root, display_controller)
        
    # 启动服务器线程
    server = SimpleJSONRPCServer(('0.0.0.0', endpoint_port))
    server.register_function(management_controller.add_image_base64, 'add_image_base64')
    server.register_function(management_controller.remove_image, 'remove_image')
    threading.Thread(target=server.serve_forever, daemon=True).start()

    # 监听键盘输入切换管理UI
    root.bind("<Key>", lambda e: management_controller.toggle() if e.char == 'm' else None)

    root.mainloop()
