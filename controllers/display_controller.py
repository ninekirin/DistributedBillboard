import threading
import time
import tkinter as tk
from PIL import Image, ImageTk
from models.image_model import ImageModel
from models.config_model import load_config
import models.log_model as logger

class DisplayController:
    def __init__(self, root):
        self.root = root
        self.label = tk.Label(root)
        self.label.pack(fill=tk.BOTH, expand=True)
        self.image_model = ImageModel()
        self.image_switch_interval = load_config().get('image_switch_interval', 5)
        # 启动广告轮播线程
        threading.Thread(target=self.show_images, daemon=True).start()
        # self.root.bind('<Configure>', self.on_resize) # 为窗口大小变化绑定事件（性能较差）

    def on_resize(self, event):
        # 重新显示当前图像以适应新的窗口尺寸
        if hasattr(self, 'current_image_path'):
            self.display_image(self.current_image_path)

    def display_image(self, image_path):
        self.current_image_path = image_path
        img = Image.open(image_path)
        # 获取窗口的当前尺寸
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        # 按窗口尺寸调整图像大小
        img = img.resize((window_width, window_height), Image.Resampling.LANCZOS)
        img = ImageTk.PhotoImage(img)
        self.label.config(image=img)
        self.label.image = img

    def show_images(self):
        while True:
            image_path = self.image_model.get_next_image()
            if image_path:
                self.display_image(image_path)
            logger.log_action(f"Displaying image {image_path}")
            time.sleep(self.image_switch_interval)
