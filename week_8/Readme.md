-Project Overview
This project predicts future electricity demand using historical electricity consumption data.
The project uses Deep Learning models to learn electricity demand patterns and forecast future demand.

-Dataset
Hourly Energy Consumption – PJM
The dataset contains hourly electricity consumption data for different regions.

-Technologies Used
Python
Pandas
NumPy
Scikit-learn
TensorFlow / Keras
Matplotlib
Seaborn
Flask
Bootstrap
Git & GitHub
Project Phases

-Phase 1 – Data Understanding
Analyze timestamps
Check missing values
Check duplicate records
Study electricity demand trends
Identify seasonal patterns
Detect abnormal demand periods

-Phase 2 – Data Preprocessing
Sort data by time
Handle missing timestamps
Handle missing values
Create time-based features
Create lag features
Create rolling features
Scale the data

-Phase 3 – Exploratory Data Analysis
The project analyzes:
Hourly demand
Daily demand
Weekly demand
Monthly demand
Peak and off-peak demand
Rolling mean and standard deviation
Autocorrelation
Seasonal patterns

-Phase 4 – Baseline Models
Simple forecasting methods are created first:
Naive Forecast
Moving Average
Previous-Day Forecast
Previous-Week Forecast
These models are used as a baseline for comparison.

-Phase 5 – Deep Learning Models
The following models are developed:
RNN
LSTM
GRU
Bidirectional LSTM
Different lookback periods are tested:
24 hours
48 hours
168 hours
The models use historical electricity demand to predict future demand.

-Phase 6 – Model Improvement
The models are improved using:
Additional lag features
Rolling features
Dropout
RMSprop optimizer
Learning-rate scheduling
Early stopping
Batch-size tuning
Layers and neurons
Hyperparameter tuning
Batch Normalization was tested but not used in the final improvement pipeline because it did not provide good performance.

-Model Evaluation
The models are evaluated using:
MAE
RMSE
MAPE
R²
Bias
The best model is selected based mainly on higher R² and lower error values.

-Forecasting Dashboard
A Flask + Bootstrap dashboard is created to display:
Current electricity demand
Historical demand
Future demand forecast
Model performance
Actual vs predicted demand
Daily and weekly trends
Forecast errors
Peak demand analysis
