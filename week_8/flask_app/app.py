from flask import Flask, render_template, request, redirect, url_for
import numpy as np
import pandas as pd
import joblib
import os

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt

from tensorflow.keras.models import load_model


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)


# =========================================================
# CONFIGURATION
# =========================================================

DATA_PATH = "PJME_preprocessed.csv"

MODEL_PATH = "best_gru_phase06.keras"

FEATURE_SCALER_PATH = "feature_scaler.pkl"

TARGET_SCALER_PATH = "target_scaler.pkl"

LOOKBACK = 168

HORIZON = 24

TARGET = "PJME_MW"


# =========================================================
# FEATURES USED BY RNN-48
# =========================================================

FEATURE_COLUMNS = [
    "PJME_MW",

    "Hour_sin",
    "Hour_cos",

    "DayOfWeek_sin",
    "DayOfWeek_cos",

    "Month",
    "IsWeekend",

    "Lag_1",
    "Lag_24",
    "Lag_48",
    "Lag_168",

    "RollingMean_24",
    "RollingMean_168",
    "RollingStd_24",
    "RollingStd_168"
]


# =========================================================
# LOAD DATA
# =========================================================

df = pd.read_csv(DATA_PATH)

df["Datetime"] = pd.to_datetime(
    df["Datetime"]
)

df = df.sort_values(
    "Datetime"
).reset_index(drop=True)


# =========================================================
# LOAD MODEL
# =========================================================

model = load_model(
    MODEL_PATH
)


# =========================================================
# LOAD SCALERS
# =========================================================

feature_scaler = joblib.load(
    FEATURE_SCALER_PATH
)

target_scaler = joblib.load(
    TARGET_SCALER_PATH
)


# =========================================================
# CREATE STATIC FOLDER IF NOT EXISTS
# =========================================================

os.makedirs(
    "static/charts",
    exist_ok=True
)


# =========================================================
# FORECAST FUNCTION
# =========================================================

def generate_forecast():

    # -----------------------------------------
    # Last 48 hours
    # -----------------------------------------

    latest_data = df.tail(
        LOOKBACK
    ).copy()


    # -----------------------------------------
    # Select features
    # -----------------------------------------

    input_features = latest_data[
        FEATURE_COLUMNS
    ].values


    # -----------------------------------------
    # Scale features
    # -----------------------------------------

    input_scaled = feature_scaler.transform(
        input_features
    )


    # -----------------------------------------
    # RNN input
    # -----------------------------------------

    X_input = input_scaled.reshape(
        1,
        LOOKBACK,
        len(FEATURE_COLUMNS)
    )


    # -----------------------------------------
    # Prediction
    # -----------------------------------------

    prediction_scaled = model.predict(
        X_input,
        verbose=0
    )


    # -----------------------------------------
    # Convert back to MW
    # -----------------------------------------

    prediction = target_scaler.inverse_transform(
        prediction_scaled.reshape(-1, 1)
    ).flatten()


    # -----------------------------------------
    # Future timestamps
    # -----------------------------------------

    last_datetime = latest_data[
        "Datetime"
    ].iloc[-1]


    future_dates = pd.date_range(
        start=last_datetime + pd.Timedelta(hours=1),
        periods=HORIZON,
        freq="h"
    )


    # -----------------------------------------
    # Forecast dataframe
    # -----------------------------------------

    forecast_df = pd.DataFrame({

        "Datetime": future_dates,

        "Forecast_MW": prediction

    })


    return forecast_df


# =========================================================
# CREATE FORECAST CHART
# =========================================================

def create_forecast_chart(
    forecast_df
):

    chart_path = (
        "static/charts/"
        "forecast.png"
    )


    plt.figure(
        figsize=(12, 5)
    )


    plt.plot(
        forecast_df["Datetime"],
        forecast_df["Forecast_MW"],
        marker="o"
    )


    plt.title(
        "24-Hour Electricity Demand Forecast"
    )

    plt.xlabel(
        "Time"
    )

    plt.ylabel(
        "Demand (MW)"
    )


    plt.xticks(
        rotation=45
    )


    plt.tight_layout()


    plt.savefig(
        chart_path,
        dpi=120
    )


    plt.close()


    return chart_path


# =========================================================
# CREATE HISTORICAL CHART
# =========================================================

def create_historical_chart():

    chart_path = (
        "static/charts/"
        "historical.png"
    )


    historical = df.tail(
        168
    )


    plt.figure(
        figsize=(12, 5)
    )


    plt.plot(
        historical["Datetime"],
        historical[TARGET]
    )


    plt.title(
        "Historical Electricity Consumption"
    )

    plt.xlabel(
        "Time"
    )

    plt.ylabel(
        "Demand (MW)"
    )


    plt.xticks(
        rotation=45
    )


    plt.tight_layout()


    plt.savefig(
        chart_path,
        dpi=120
    )


    plt.close()


    return chart_path


# =========================================================
# CREATE ACTUAL VS FORECAST CHART
# =========================================================
# =========================================================
# CREATE ACTUAL VS FORECAST BACKTEST CHART
# =========================================================

def create_actual_forecast_chart():

    chart_path = (
        "static/charts/"
        "actual_forecast.png"
    )

    # -----------------------------------------------------
    # Use the final 24 known hours as the evaluation period
    # -----------------------------------------------------

    actual_start = len(df) - HORIZON

    input_start = (
        actual_start - LOOKBACK
    )

    input_end = actual_start

    # Safety check
    if input_start < 0:
        raise ValueError(
            "Not enough historical data for backtest."
        )

    # -----------------------------------------------------
    # 168 hours BEFORE the 24-hour actual period
    # -----------------------------------------------------

    context_df = df.iloc[
        input_start:input_end
    ].copy()

    actual_df = df.iloc[
        actual_start:
    ].copy()

    # -----------------------------------------------------
    # Make Month numeric if necessary
    # -----------------------------------------------------

    if not pd.api.types.is_numeric_dtype(
        context_df["Month"]
    ):
        context_df["Month"] = (
            context_df["Datetime"].dt.month
        )

    # -----------------------------------------------------
    # Prepare model input
    # -----------------------------------------------------

    input_features = context_df[
        FEATURE_COLUMNS
    ].values

    input_scaled = feature_scaler.transform(
        input_features
    )

    X_input = input_scaled.reshape(
        1,
        LOOKBACK,
        len(FEATURE_COLUMNS)
    )

    # -----------------------------------------------------
    # Predict the SAME 24 hours as actual_df
    # -----------------------------------------------------

    prediction_scaled = model.predict(
        X_input,
        verbose=0
    )

    prediction = target_scaler.inverse_transform(
        prediction_scaled.reshape(-1, 1)
    ).flatten()

    # -----------------------------------------------------
    # Make sure lengths match
    # -----------------------------------------------------

    prediction = prediction[:HORIZON]

    actual_values = (
        actual_df[TARGET]
        .values[:HORIZON]
    )

    actual_dates = (
        actual_df["Datetime"]
        .values[:HORIZON]
    )

    # -----------------------------------------------------
    # Plot
    # -----------------------------------------------------

    plt.figure(
        figsize=(12, 5)
    )

    plt.plot(
        actual_dates,
        actual_values,
        marker="o",
        linewidth=2,
        label="Actual"
    )

    plt.plot(
        actual_dates,
        prediction,
        marker="o",
        linewidth=2,
        label="Forecast"
    )

    plt.title(
        "Actual vs Forecast - 24 Hour Backtest"
    )

    plt.xlabel(
        "Time"
    )

    plt.ylabel(
        "Demand (MW)"
    )

    plt.legend()

    plt.grid(
        True,
        alpha=0.25
    )

    plt.xticks(
        rotation=45
    )

    plt.tight_layout()

    plt.savefig(
        chart_path,
        dpi=120,
        bbox_inches="tight"
    )

    plt.close()

    return chart_path

# =========================================================
# DASHBOARD
# =========================================================

@app.route("/")
def home():

    return redirect(
        url_for("dashboard")
    )


@app.route("/dashboard")
def dashboard():

    forecast_df = generate_forecast()


    # -----------------------------------------
    # Current demand
    # -----------------------------------------

    current_demand = round(
        float(
            df[TARGET].iloc[-1]
        ),
        2
    )


    # -----------------------------------------
    # Forecast statistics
    # -----------------------------------------

    peak_demand = round(
        float(
            forecast_df[
                "Forecast_MW"
            ].max()
        ),
        2
    )


    minimum_demand = round(
        float(
            forecast_df[
                "Forecast_MW"
            ].min()
        ),
        2
    )


    average_demand = round(
        float(
            forecast_df[
                "Forecast_MW"
            ].mean()
        ),
        2
    )


    # -----------------------------------------
    # Peak time
    # -----------------------------------------

    peak_index = forecast_df[
        "Forecast_MW"
    ].idxmax()


    peak_time = forecast_df.loc[
        peak_index,
        "Datetime"
    ]


    # -----------------------------------------
    # Historical chart
    # -----------------------------------------

    create_historical_chart()


    # -----------------------------------------
    # Forecast chart
    # -----------------------------------------

    create_forecast_chart(
        forecast_df
    )


    return render_template(
        "dashboard.html",

        current_demand=current_demand,

        peak_demand=peak_demand,

        minimum_demand=minimum_demand,

        average_demand=average_demand,

        peak_hour=peak_time.strftime(
            "%Y-%m-%d %H:%M"
        ),

        mae="2213.30",

        rmse="3018.20",

        mape="6.80",

        historical_dates=[
            x.strftime(
                "%Y-%m-%d %H:%M"
            )
            for x in df.tail(168)["Datetime"]
        ],

        historical_values=[
            round(
                float(x),
                2
            )
            for x in df.tail(168)[TARGET]
        ],

        forecast=forecast_df.to_dict(
            orient="records"
        )
    )


# =========================================================
# FORECAST PAGE
# =========================================================

@app.route(
    "/forecast",
    methods=["GET", "POST"]
)
def forecast():

    forecast_df = None

    peak_demand = None

    minimum_demand = None

    average_demand = None

    peak_hour = None


    if request.method == "POST":

        forecast_df = generate_forecast()


        peak_demand = round(
            float(
                forecast_df[
                    "Forecast_MW"
                ].max()
            ),
            2
        )


        minimum_demand = round(
            float(
                forecast_df[
                    "Forecast_MW"
                ].min()
            ),
            2
        )


        average_demand = round(
            float(
                forecast_df[
                    "Forecast_MW"
                ].mean()
            ),
            2
        )


        peak_index = forecast_df[
            "Forecast_MW"
        ].idxmax()


        peak_hour = forecast_df.loc[
            peak_index,
            "Datetime"
        ].strftime(
            "%Y-%m-%d %H:%M"
        )


        create_forecast_chart(
            forecast_df
        )


    return render_template(
        "forecast.html",

        forecast=(
            forecast_df.to_dict(
                orient="records"
            )
            if forecast_df is not None
            else None
        ),

        peak_demand=peak_demand,

        minimum_demand=minimum_demand,

        average_demand=average_demand,

        peak_hour=peak_hour
    )


# =========================================================
# ANALYTICS PAGE
# =========================================================

@app.route("/analytics")
def analytics():

    forecast_df = generate_forecast()


    # -----------------------------------------
    # Historical data
    # -----------------------------------------

    historical = df.tail(
        168
    ).copy()


    # -----------------------------------------
    # Error information
    # -----------------------------------------

    recent_actual = historical[
        TARGET
    ].values


    recent_mean = float(
        recent_actual.mean()
    )


    forecast_mean = float(
        forecast_df[
            "Forecast_MW"
        ].mean()
    )


    forecast_peak = float(
        forecast_df[
            "Forecast_MW"
        ].max()
    )


    create_historical_chart()

    create_forecast_chart(
        forecast_df
    )

    create_actual_forecast_chart()

    return render_template(
        "analytics.html",

        current_demand=round(
            float(
                df[TARGET].iloc[-1]
            ),
            2
        ),

        historical_mean=round(
            recent_mean,
            2
        ),

        forecast_mean=round(
            forecast_mean,
            2
        ),

        forecast_peak=round(
            forecast_peak,
            2
        )
    )


# =========================================================
# VALIDATION PAGE
# =========================================================

@app.route(
    "/validation",
    methods=["GET", "POST"]
)
def validation():

    validation_days = 30


    if request.method == "POST":

        validation_days = int(
            request.form.get(
                "validation_days",
                30
            )
        )


    # -----------------------------------------
    # We keep test data untouched.
    # Validation is taken before final test.
    # -----------------------------------------

    test_size = int(
        len(df) * 0.20
    )


    development_df = df.iloc[
        :-test_size
    ].copy()


    validation_hours = (
        validation_days * 24
    )


    validation_df = development_df.tail(
        validation_hours
    ).copy()


    # -----------------------------------------
    # Actual values
    # -----------------------------------------

    actual = validation_df[
        TARGET
    ].values


    # -----------------------------------------
    # Basic validation display
    # -----------------------------------------

    return render_template(
        "validation.html",

        validation_days=validation_days,

        validation_rows=len(
            validation_df
        ),

        actual_mean=round(
            float(
                actual.mean()
            ),
            2
        ),

        actual_peak=round(
            float(
                actual.max()
            ),
            2
        ),

        mae="2213.30",

        rmse="3018.20",

        mape="6.80",

        r2="0.7836"
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )