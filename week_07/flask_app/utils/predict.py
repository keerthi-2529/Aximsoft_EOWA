import os
import json
import numpy as np

from tensorflow.keras.preprocessing import image


# ===============================
# Load class names
# ===============================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


CLASS_PATH = os.path.join(
    BASE_DIR,
    "model",
    "class_names.json"
)


with open(CLASS_PATH, "r") as f:
    class_names = json.load(f)



# Handle JSON dictionary

if isinstance(class_names, dict):

    class_names = {
        int(k): v
        for k, v in class_names.items()
    }


# Handle JSON list

elif isinstance(class_names, list):

    class_names = {
        i: name
        for i, name in enumerate(class_names)
    }



# ===============================
# Prediction Function
# ===============================

def predict_image(model, img):

    # -------------------------------
    # Load image
    # -------------------------------

    if isinstance(img, str):

        img = image.load_img(
            img,
            target_size=(224,224)
        )

        img_array = image.img_to_array(img)


    else:

        img_array = np.array(img)



    # -------------------------------
    # Remove extra batch dimensions
    # -------------------------------

    while len(img_array.shape) > 3:

        img_array = np.squeeze(img_array, axis=0)



    # -------------------------------
    # Ensure correct size
    # -------------------------------

    if img_array.shape != (224,224,3):

        img = image.array_to_img(img_array)

        img = img.resize((224,224))

        img_array = image.img_to_array(img)



    # -------------------------------
    # Normalize
    # -------------------------------

    img_array = img_array.astype("float32") / 255.0



    # Add batch dimension

    img_array = np.expand_dims(
        img_array,
        axis=0
    )


    print("Final input shape:", img_array.shape)

    # -------------------------------
    # Prediction
    # -------------------------------

    prediction = model.predict(img_array)


    predicted_index = int(
        np.argmax(prediction[0])
    )


    confidence = float(
        np.max(prediction[0])*100
    )


    disease = class_names.get(
        predicted_index,
        "Unknown"
    )


    probabilities=[]


    for i, prob in enumerate(prediction[0]):

        probabilities.append({

            "class": class_names.get(
                i,
                f"Class {i}"
            ),

            "probability": round(
                float(prob)*100,
                2
            )

        })


    return disease, confidence, probabilities