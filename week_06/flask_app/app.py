from flask import Flask, render_template, request, send_file
import joblib
import pandas as pd
import os
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import datetime
import reportlab.lib.enums as TA_CENTER
import tempfile


os.makedirs("static/plots", exist_ok=True)

app = Flask(__name__)

model = joblib.load("/Users/aximsoft/Downloads/week_06/final_model.pkl")

baseline_df = pd.read_csv("/Users/aximsoft/Downloads/week_06/baseline_model_results.csv")
optimized_df = pd.read_csv("/Users/aximsoft/Downloads/week_06/optimized_results.csv")

best_model = optimized_df.loc[
    optimized_df["R2"].idxmax()
]

@app.route("/")
def dashboard():

    df = pd.read_csv("/Users/aximsoft/Downloads/week_06/train.csv")

    dashboard_info = {
        "dataset": "House Prices - Advanced Regression Techniques",
        "records": len(df),
        "models": len(optimized_df)
    }

    best = {
        "model": best_model["Model"],
        "mae": best_model["MAE"],
        "mse": best_model["MSE"],
        "rmse": best_model["RMSE"],
        "r2": best_model["R2"]
    }

    return render_template(
        "dashboard.html",
        info=dashboard_info,
        best=best
    )

@app.route("/prediction")
def prediction():
    return render_template("prediction.html")

@app.route('/predict',methods=['POST'])
def predict():

    TotalArea = float(request.form["TotalArea"])
    OverallQual = float(request.form["OverallQual"])
    TotalLivingSF = float(request.form["TotalLivingSF"])
    GrLivArea = float(request.form["GrLivArea"])
    GarageCars = float(request.form["GarageCars"])
    TotalBathrooms = float(request.form["TotalBathrooms"])
    GarageArea = float(request.form["GarageArea"])
    TotalBsmtSF = float(request.form["TotalBsmtSF"])
    YearBuilt = float(request.form["YearBuilt"])

    input_df = pd.DataFrame([{
        "TotalArea": TotalArea,
        "OverallQual": OverallQual,
        "TotalLivingSF": TotalLivingSF,
        "GrLivArea": GrLivArea,
        "GarageCars": GarageCars,
        "TotalBathrooms": TotalBathrooms,
        "GarageArea": GarageArea,
        "TotalBsmtSF": TotalBsmtSF,
        "YearBuilt": YearBuilt
    }])

    prediction = model.predict(input_df)[0]

    return render_template(
        "prediction.html",
        prediction=round(prediction, 2)
    )

@app.route("/analytics")
def analytics():

    plots = {
        "distribution": "plots/distribution.png",
        "heatmap": "plots/heatmap.png",
        "missing": "plots/missing_values.png",
        "feature": "plots/feature_importance.png",
        "actual": "plots/actual_vs_predicted.png",
        "residual": "plots/residual_plot.png"
    }

    return render_template(
        "analytics.html",
        plots=plots
    )

@app.route("/comparison")
def comparison():

    baseline_df = pd.read_csv("/Users/aximsoft/Downloads/week_06/baseline_model_results.csv")
    optimized_df = pd.read_csv("/Users/aximsoft/Downloads/week_06/optimized_results.csv")

    best_model = optimized_df.loc[
        optimized_df["R2"].idxmax()
    ].to_dict()

    return render_template(
        "comparison.html",
        baseline=baseline_df.to_dict(orient="records"),
        optimized=optimized_df.to_dict(orient="records"),
        best=best_model
    )


@app.route("/report")
def report():
    return render_template("report.html")

@app.route("/report/prediction")
def prediction_report():
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    doc = SimpleDocTemplate(temp.name)
    styles = getSampleStyleSheet()

    title = styles["Title"]
    title.alignment = TA_CENTER
    pdf_path = os.path.join("prediction_report.pdf")

    story = []

    story.append(Paragraph("House Price Prediction Report", title))
    story.append(Paragraph("<br/>", styles["Normal"]))

    story.append(Paragraph(f"Generated On : {datetime.now()}", styles["Normal"]))
    story.append(Paragraph(f"Model Used : {best_model['Model']}", styles["Normal"]))
    story.append(Paragraph(f"R² Score : {best_model['R2']:.4f}", styles["Normal"]))
    story.append(Paragraph(f"MAE : {best_model['MAE']:.4f}", styles["Normal"]))
    story.append(Paragraph(f"MSE : {best_model['MSE']:.4f}", styles["Normal"]))
    story.append(Paragraph(f"RMSE : {best_model['RMSE']:.4f}", styles["Normal"]))

    doc.build(story)

    return send_file(pdf_path,temp.name,
                     as_attachment=True,
                     download_name="Prediction_Report.pdf")


@app.route("/report/comparison")
def comparison_report():
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    doc = SimpleDocTemplate(temp.name)

    styles = getSampleStyleSheet()

    story = []
    pdf_path = os.path.join("comparison_report.pdf")

    story.append(Paragraph("Model Comparison Report", styles["Title"]))
    story.append(Paragraph("<br/>", styles["Normal"]))

    data = [["Model", "MAE", "MSE", "RMSE", "R2"]]

    for _, row in optimized_df.iterrows():
        data.append([
            row["Model"],
            round(row["MAE"], 4),
            round(row["MSE"], 4),
            round(row["RMSE"], 4),
            round(row["R2"], 4)
        ])

    table = Table(data)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("ALIGN", (0, 0), (-1, -1), "CENTER")
    ]))

    story.append(table)

    story.append(Paragraph("<br/><br/>", styles["Normal"]))

    story.append(Paragraph(
        f"<b>Best Model :</b> {best_model['Model']}",
        styles["Heading2"]
    ))

    doc.build(story)

    return send_file(pdf_path,temp.name,
                     as_attachment=True,
                     download_name="Model_Comparison_Report.pdf")


@app.route("/report/eda")
def eda_report():
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    doc = SimpleDocTemplate(temp.name)

    styles = getSampleStyleSheet()

    df = pd.read_csv("dataset/train.csv")

    story = []
    pdf_path = os.path.join("comparison_report.pdf")

    story.append(Paragraph("Exploratory Data Analysis Report",
                           styles["Title"]))

    story.append(Paragraph("<br/>", styles["Normal"]))

    story.append(Paragraph(f"Rows : {df.shape[0]}", styles["Normal"]))

    story.append(Paragraph(f"Columns : {df.shape[1]}", styles["Normal"]))

    story.append(Paragraph(
        f"Missing Values : {df.isnull().sum().sum()}",
        styles["Normal"]
    ))

    story.append(Paragraph(
        f"Duplicate Rows : {df.duplicated().sum()}",
        styles["Normal"]
    ))

    story.append(Paragraph(
        f"Numerical Features : {len(df.select_dtypes(include='number').columns)}",
        styles["Normal"]
    ))

    story.append(Paragraph(
        f"Categorical Features : {len(df.select_dtypes(exclude='number').columns)}",
        styles["Normal"]
    ))

    story.append(Paragraph("<br/>Summary", styles["Heading2"]))

    story.append(Paragraph(
        "The dataset was preprocessed by handling missing values, "
        "encoding categorical variables, feature engineering, "
        "outlier treatment, and scaling where required. "
        "Several regression algorithms were trained and evaluated. "
        "CatBoost achieved the best prediction accuracy.",
        styles["Normal"]
    ))

    doc.build(story)

    return send_file(pdf_path,temp.name,
                     as_attachment=True,
                     download_name="EDA_Report.pdf")

if __name__ == "__main__":
    app.run(debug=True)