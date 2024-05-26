import threading
import time
import tkinter as tk
import os
from PIL import Image, ImageTk
import pillow_avif
from models.image_model import ImageModel
import utils.log as logger

class DisplayController:
    def __init__(self, root, background_color='black', image_switch_interval=5):
        self.root = root
        self.label = tk.Label(root)

        # Pack label to fill the window
        self.label.pack(fill=tk.BOTH, expand=True)

        try:
            # Set label background color
            self.label.configure(background=background_color)
        except:
            logger.log_error(f"Invalid background color: {background_color}")
            self.label.configure(background='black')

        self.image_model = ImageModel()
        self.image_switch_interval = image_switch_interval
        self.resize_delay = 200  # resize delay in ms
        self.resize_after_id = None

        # Start a thread to show images
        threading.Thread(target=self.show_images, daemon=True).start()

        # Bind window resize event to on_resize
        self.root.bind('<Configure>', self.on_resize)

        # Mouse click to show next image
        self.root.bind('<Button-1>', lambda e: self.display_image(self.image_model.get_next_image()))

    def set_background_color(self, color):
        try:
            self.label.configure(background=color)
            return True
        except:
            logger.log_error(f"Invalid background color: {color}")
            tk.messagebox.showerror("Error", f"Invalid background color: {color}")
            return False

    def set_image_switch_interval(self, interval):
        self.image_switch_interval = interval

    def on_resize(self, event):
        if self.resize_after_id:
            self.root.after_cancel(self.resize_after_id)
        self.resize_after_id = self.root.after(self.resize_delay, self.perform_resize)

    def perform_resize(self):
        self.resize_after_id = None
        if hasattr(self, 'current_image_path'):
            self.display_image(self.current_image_path)

    def display_image(self, image_path):
        self.current_image_path = image_path
        img = Image.open(image_path)
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        # DEPRECATED Resize image to fit window (stretch)
        # img = img.resize((window_width, window_height), Image.Resampling.LANCZOS)
        # Resize image to fit window and keep aspect ratio
        width_ratio = window_width / img.width
        height_ratio = window_height / img.height
        ratio = min(width_ratio, height_ratio)
        new_width = int(img.width * ratio)
        new_height = int(img.height * ratio)
        img = img.resize((new_width, new_height), Image.LANCZOS)
        img = ImageTk.PhotoImage(img)
        self.label.config(image=img)
        self.label.image = img

    def show_images(self):
        while True:
            image_path = self.image_model.get_next_image()
            if image_path:
                # Check if image is exist
                if not os.path.exists(image_path):
                    logger.log_action(f"Image {image_path} not found, skipping")
                    # Remove image from list
                    self.image_model.remove_image(image_path, distribution=False)
                    continue
                self.display_image(image_path)
            logger.log_action(f"Displaying image {image_path}")
            time.sleep(self.image_switch_interval)