import os
import json
import tensorflow as tf

from flask import (
    Flask,
    render_template,
    request
)
import pandas as pd

from werkzeug.utils import secure_filename

from tensorflow.keras.models import load_model
from utils.preprocess import preprocess_image

from utils.predict import predict_image

from utils.gradcam import generate_gradcam

from utils.report import generate_report

import numpy as np

# =====================================
# Flask Configuration
# =====================================

app = Flask(__name__)



UPLOAD_FOLDER = "static/uploads"

GRADCAM_FOLDER = "static/gradcam"

REPORT_FOLDER = "static/reports"



os.makedirs(UPLOAD_FOLDER, exist_ok=True)

os.makedirs(GRADCAM_FOLDER, exist_ok=True)

os.makedirs(REPORT_FOLDER, exist_ok=True)



app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER





# =====================================
# Load Model
# =====================================


import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "model",
    "resnet_bestmodel.keras"
)

model = load_model(MODEL_PATH)



model = tf.keras.models.load_model(
    MODEL_PATH
)



# =====================================
# Load Classes
# =====================================


with open(
    "model/class_names.json",
    "r"
) as file:

    class_names = json.load(file)





# =====================================
# Dashboard
# =====================================


@app.route("/")

def dashboard():


    dataset = {

        "images":10015,

        "classes":7,

        "train":7010,

        "validation":1502,

        "test":1503

    }



    return render_template(

        "dashboard.html",

        dataset=dataset

    )





# =====================================
# Diagnosis Page
# =====================================


@app.route("/diagnosis")

def diagnosis():


    return render_template(
        "diagnosis.html"
    )






# =====================================
# Prediction Route
# =====================================

@app.route(
    "/predict",
    methods=["POST"]
)
def predict():


    if "image" not in request.files:

        return render_template(
            "diagnosis.html",
            error="No image selected"
        )


    image_file = request.files["image"]


    if image_file.filename == "":

        return render_template(
            "diagnosis.html",
            error="Please select image"
        )


    filename = secure_filename(
        image_file.filename
    )


    image_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )


    image_file.save(
        image_path
    )


    # ================================
    # Preprocess Image
    # ================================

    img_array = preprocess_image(
        image_path
    )


    # Make sure shape is correct

    print(
        "Input shape:",
        img_array.shape
    )



    # ================================
    # Prediction
    # ================================

    disease, confidence, probabilities = predict_image(
        model,
        img_array
    )



    # ================================
    # GradCAM
    # ================================

    heatmap_path =generate_gradcam(
    model=model,
    img_array=img_array,
    save_path="static/gradcam/result.jpg"
)



    # ================================
    # Report
    # ================================

    report_path = generate_report(

        filename,

        disease,

        confidence,

        probabilities

    )



    return render_template(

        "result.html",

        image=image_path.replace("\\","/"),

        heatmap=heatmap_path.replace("\\","/"),

        disease=disease,

        confidence=round(confidence,2),

        probabilities=probabilities,

        report=report_path

    )





# =====================================
# Analytics
# =====================================

import pandas as pd

@app.route("/analytics")
def analytics():

    df = pd.read_csv("data/model_metrics.csv")

    models = df.to_dict(orient="records")

    return render_template(

        "analytics.html",

        models=models,

        labels=df["Model"].tolist(),

        accuracy=df["Accuracy"].tolist(),

        precision=df["Precision"].tolist(),

        recall=df["Recall"].tolist(),

        f1=df["F1"].tolist(),

        auc=df["ROC_AUC"].tolist(),

        best_model={
            "Model":"Resnet05",
            "Accuracy":80.80,
            "Precision":75.40,
            "Recall":63.00,
            "F1":67.20,
            "ROC_AUC":90.20
        }

    )






# =====================================
# Reports
# =====================================


@app.route("/reports")

def reports():


    return render_template(
        "reports.html"
    )






# =====================================
# About
# =====================================


@app.route("/about")

def about():


    return render_template(
        "about.html"
    )







# =====================================
# Run Application
# =====================================


if __name__=="__main__":


    app.run(

        debug=True

    )