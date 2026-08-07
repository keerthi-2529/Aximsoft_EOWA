Multi-Class Skin Disease Classification & Diagnosis Platform

Project Overview

This project is a deep learning-based web application that classifies skin diseases from medical images using Convolutional Neural Networks (CNN) and Transfer Learning models. The application allows users to upload a skin image, predicts the disease, displays the confidence score, and provides visual explanations using Grad-CAM.



Dataset

- Dataset: HAM10000 (Skin Cancer MNIST)
- Total Images: 10,015
- Number of Classes: 7

Disease Classes
- Actinic Keratosis
- Basal Cell Carcinoma
- Benign Keratosis
- Dermatofibroma
- Melanocytic Nevus
- Melanoma
- Vascular Lesion

Features

- Image preprocessing
- Data augmentation
- Custom CNN models
- Transfer Learning
  - MobileNetV2
  - EfficientNetB0
  - ResNet50
  - DenseNet121
- Hyperparameter tuning
- Model evaluation
- Grad-CAM visualization
- Flask web application
- Bootstrap 5 user interface

Technologies Used

- Python
- TensorFlow / Keras
- OpenCV
- NumPy
- Pandas
- Matplotlib
- Flask
- Bootstrap 5
- Git & GitHub

Model Evaluation

The models were evaluated using:

- Accuracy
- Precision
- Recall
- F1 Score
- ROC-AUC
- Confusion Matrix


Flask Application

The web application includes:

- Dashboard
- Skin Disease Prediction
- Model Analytics
- Explainable AI (Grad-CAM)
- Reports
- About Page


Output

- Upload a skin image
- Predict disease class
- Display confidence score
- Show Grad-CAM heatmap
- Download diagnosis report

