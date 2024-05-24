import os
import base64
from urllib.request import urlretrieve
from PIL import Image
import models.log_model as logger

class ImageModel:
    def __init__(self):
        if os.name == "nt":
            self.image_cache_dir = ".\\images"
        else:
            self.image_cache_dir = "./images"
        self.image_list = []
        self.current_image_index = 0

        if not os.path.exists(self.image_cache_dir):
            os.makedirs(self.image_cache_dir)

        # Load images from image_cache_dir
        for filename in os.listdir(self.image_cache_dir):
            if filename.lower().endswith((".jpg", ".jpeg", ".png")):
                self.image_list.append(os.path.join(self.image_cache_dir, filename))

    def download_image(self, url):
        filename = os.path.join(self.image_cache_dir, os.path.basename(url))
        if not os.path.exists(filename):
            urlretrieve(url, filename)
            logger.log_action(f"Downloaded image from {url}")
        # validate image
        try:
            Image.open(filename).verify()
        except Exception as e:
            os.remove(filename)
            raise Exception(f"Invalid image: {url}")
        return filename

    def add_image(self, url):
        filename = self.download_image(url)
        self.image_list.append(filename)
        logger.log_action(f"Added image {url}")
        return filename

    def remove_image(self, url):
        filename = os.path.join(self.image_cache_dir, os.path.basename(url))
        if filename in self.image_list:
            self.image_list.remove(filename)
            os.remove(filename)
            self.current_image_index = 0
            logger.log_action(f"Removed image {url}")
            return True

    def get_images(self):
        return self.image_list

    def get_next_image(self):
        if not self.image_list:
            return None
        image_path = self.image_list[self.current_image_index]
        self.current_image_index = (self.current_image_index + 1) % len(self.image_list)
        return image_path

    def add_image_base64(self, filename, base64data):
        data = base64.b64decode(base64data)
        filepath = os.path.join(self.image_cache_dir, filename)
        with open(filepath, "wb") as f:
            f.write(data)
        self.image_list.append(filepath)
        logger.log_action(f"Added base64 image {filename}")
        return filepath
