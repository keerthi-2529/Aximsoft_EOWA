import numpy as np
from PIL import Image

# Image size used during model training
IMG_HEIGHT = 224
IMG_WIDTH = 224

import numpy as np
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input



def preprocess_image(path):

    img = image.load_img(
        path,
        target_size=(224,224)
    )


    img_array = image.img_to_array(
        img
    )


    img_array = preprocess_input(img_array)


    img_array = np.expand_dims(
        img_array,
        axis=0
    )


    return img_array