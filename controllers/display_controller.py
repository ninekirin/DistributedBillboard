import threading
import time
import tkinter as tk
from PIL import Image, ImageTk
from models.image_model import ImageModel

class DisplayController:
    def __init__(self, root):
        self.root = root
        self.label = tk.Label(root)
        self.label.pack()
        self.image_model = ImageModel()
        # 启动广告轮播线程
        threading.Thread(target=self.show_images, daemon=True).start()

    def show_images(self):
        while True:
            image_path = self.image_model.get_next_image()
            if image_path:
                img = ImageTk.PhotoImage(Image.open(image_path))
                self.label.config(image=img)
                self.label.image = img
            time.sleep(1)