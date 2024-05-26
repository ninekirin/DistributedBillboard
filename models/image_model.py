import os
import base64
from urllib.request import urlretrieve
from PIL import Image
import pillow_avif
import utils.log as logger

extentions = (".jpg", ".jpeg", ".png", ".avif", ".webp", ".gif", ".bmp", ".tiff")

class ImageModel:
    def __init__(self):
        if os.name == "nt":
            self.image_cache_dir = ".\\images"
        else:
            self.image_cache_dir = "./images"
        self.image_list = []
        self.current_image_index = -1 # start from -1 at startup

        if not os.path.exists(self.image_cache_dir):
            os.makedirs(self.image_cache_dir)

        path_list = os.listdir(self.image_cache_dir)

        # Remove invalid images
        for path in path_list:
            try:
                Image.open(os.path.join(self.image_cache_dir, path)).verify()
            except Exception as e:
                os.remove(os.path.join(self.image_cache_dir, path))
                # Remove from list
                path_list.remove(path)
                logger.log_action(f"Removed invalid image {path}")

        # Sort images by modification time
        # path_list.sort(key=lambda x: os.path.getmtime(os.path.join(self.image_cache_dir, x)))

        # Sort images by name
        # path_list.sort()

        # Load images from cache
        for filename in path_list:
            if filename.lower().endswith(extentions):
                self.image_list.append(os.path.join(self.image_cache_dir, filename))

        # Sort images by name
        self.image_list.sort()

    def download_image(self, url):
        filename = os.path.join(self.image_cache_dir, os.path.basename(url))
        if not os.path.exists(filename):
            logger.log_action(f"Downloading image from \"{url}\" to {filename}")
            urlretrieve(url, filename)
            logger.log_action(f"Downloaded image from \"{url}\"")
        else:
            logger.log_action(f"Image already exists: {url}")
            return None
        # validate image
        try:
            Image.open(filename).verify()
            return filename
        except Exception as e:
            os.remove(filename)
            logger.log_error(f"Invalid image: {url}")
            return None

    def add_image(self, url):
        filename = self.download_image(url)
        if filename:
            self.image_list.append(filename)
            self.image_list.sort()
            logger.log_action(f"Added image {url}")
            return filename
        return None
    
    def add_image_base64(self, filename, base64data):
        data = base64.b64decode(base64data)
        filepath = os.path.join(self.image_cache_dir, filename)
        if not os.path.exists(filepath):
            with open(filepath, "wb") as f:
                f.write(data)
            self.image_list.append(filepath)
            self.image_list.sort()
            logger.log_action(f"Added image {filename}")
            return filepath
        return None
    
    def remove_image(self, url):
        filename = os.path.join(self.image_cache_dir, os.path.basename(url))
        if filename in self.image_list:
            self.image_list.remove(filename)
            os.remove(filename)
            self.current_image_index = 0
            logger.log_action(f"Removed image {url}")
            return True

    def get_image_list(self):
        return self.image_list

    def get_next_image(self):
        if not self.image_list:
            return None
        self.current_image_index = (self.current_image_index + 1) % len(self.image_list)
        image_path = self.image_list[self.current_image_index]
        return image_path

    def get_prev_image(self):
        if not self.image_list:
            return None
        self.current_image_index = (self.current_image_index - 1) % len(self.image_list)
        image_path = self.image_list[self.current_image_index]
        return image_path