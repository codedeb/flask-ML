import json
import logging
import sys
import os
from PIL import Image

logging.basicConfig(format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def resize_images(input_images):
    input_arr = json.loads(input_images)
    for image_path in input_arr:
        image_path_modified = os.path.join(os.environ['NAS_PATH'],image_path)
        logger.info('image : %s' % image_path_modified)
        with Image.open(image_path_modified) as image:
            w = image.size[0]
            h = image.size[1]

            w_scale = 1.0
            h_scale = 1.0

            if w >= h:
                w_scale = w/h
            else:
                h_scale = h/w

            sizes = [100, 200, 1024]
            for size in sizes:
                img_resized = image.resize((int(w_scale*size), int(h_scale*size)))
                # extract the file name and extension
                filename_extension = os.path.splitext(image_path)
                filename = filename_extension[0]
                extension = filename_extension[1]
                output_image = os.path.join(os.environ['NAS_PATH'], filename + "_" + str(size) + extension)
                # img_resized.save(os.path.join(os.environ['NAS_PATH'], image_path[:-4] + "_" + str(size) + ".jpg"))
                img_resized.save(output_image)
    return True

