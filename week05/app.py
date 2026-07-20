from flask import Flask, render_template, request, send_file
import pandas as pd
import numpy as np
import plotly.express as px
import plotly
from math import ceil

app = Flask(__name__)

# Load Dataset
df = pd.read_csv("feature_engineered_dataset.csv")

# Convert Date Columns
date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

for col in date_columns:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")


# -------------------------------------------------------
# Plotly Helper
# -------------------------------------------------------

def create_plot(fig):
    return plotly.offline.plot(
        fig,
        include_plotlyjs=False,
        output_type="div"
    )


# -------------------------------------------------------
# Dashboard
# -------------------------------------------------------

@app.route("/")
@app.route("/dashboard")
def dashboard():
    total_revenue = round(df["payment_value"].sum(), 2)

    total_orders = df["order_id"].nunique()

    total_customers = df["customer_unique_id"].nunique()

    total_sellers = df["seller_id"].nunique()

    avg_review = round(df["review_score"].mean(), 2)

    avg_delivery = round(df["delivery_time"].mean(), 1)

    # -------------------------------------------------------
    # Monthly Revenue
    # -------------------------------------------------------

    monthly = (
        df.groupby("purchase_month")["payment_value"]
        .sum()
        .reset_index()
    )

    fig1 = px.line(
        monthly,
        x="purchase_month",
        y="payment_value",
        markers=True,
        title="Monthly Revenue"
    )

    # -------------------------------------------------------
    # Revenue by State
    # -------------------------------------------------------

    state = (
        df.groupby("customer_state")["payment_value"]
        .sum()
        .reset_index()
        .sort_values("payment_value", ascending=False)
    )

    fig2 = px.bar(
        state,
        x="customer_state",
        y="payment_value",
        color="payment_value",
        title="Revenue by State"
    )

    # -------------------------------------------------------
    # Payment Types
    # -------------------------------------------------------

    payment = (
        df.groupby("payment_type")["payment_value"]
        .sum()
        .reset_index()
    )

    fig3 = px.pie(
        payment,
        names="payment_type",
        values="payment_value",
        hole=0.45,
        title="Payment Distribution"
    )

    # -------------------------------------------------------
    # Revenue by Category
    # -------------------------------------------------------

    category = (
        df.groupby("product_category_name_english")["payment_value"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig4 = px.bar(
        category,
        x="payment_value",
        y="product_category_name_english",
        orientation="h",
        color="payment_value",
        title="Top Categories by Revenue"
    )

    return render_template(

        "dashboard.html",

        revenue=total_revenue,

        orders=total_orders,

        customers=total_customers,

        sellers=total_sellers,

        review=avg_review,

        delivery=avg_delivery,

        chart1=create_plot(fig1),

        chart2=create_plot(fig2),

        chart3=create_plot(fig3),

        chart4=create_plot(fig4)

    )


# -------------------------------------------------------
# SALES ANALYTICS
# -------------------------------------------------------


@app.route("/sales")
def sales():
    # 1. Monthly Revenue Trend
    monthly_revenue = (
        df.groupby("purchase_month")["payment_value"]
        .sum()
        .reset_index()
    )

    fig1 = px.line(
        monthly_revenue,
        x="purchase_month",
        y="payment_value",
        markers=True,
        title="Monthly Revenue Trend"
    )

    # 2. Monthly Orders
    monthly_orders = (
        df.groupby("purchase_month")["order_id"]
        .nunique()
        .reset_index(name="Orders")
    )

    fig2 = px.bar(
        monthly_orders,
        x="purchase_month",
        y="Orders",
        color="Orders",
        title="Monthly Orders"
    )

    # 3. Revenue by Product Category
    revenue_category = (
        df.groupby("product_category_name_english")["payment_value"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig3 = px.bar(
        revenue_category,
        x="payment_value",
        y="product_category_name_english",
        orientation="h",
        color="payment_value",
        title="Top 10 Categories by Revenue"
    )

    # 4. Revenue by State
    revenue_state = (
        df.groupby("customer_state")["payment_value"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    fig4 = px.bar(
        revenue_state,
        x="customer_state",
        y="payment_value",
        color="payment_value",
        title="Revenue by State"
    )

    # 5. Top Selling Products
    top_products = (
        df.groupby("product_category_name_english")["order_item_id"]
        .count()
        .sort_values(ascending=False)
        .head(10)
        .reset_index(name="Orders")
    )

    fig5 = px.bar(
        top_products,
        x="Orders",
        y="product_category_name_english",
        orientation="h",
        color="Orders",
        title="Top Selling Product Categories"
    )

    # 6. Average Order Value
    avg_order = (
        df.groupby("purchase_month")["total_order_value"]
        .mean()
        .reset_index()
    )

    fig6 = px.line(
        avg_order,
        x="purchase_month",
        y="total_order_value",
        markers=True,
        title="Average Order Value"
    )

    # 7. Revenue by Payment Type
    payment = (
        df.groupby("payment_type")["payment_value"]
        .sum()
        .reset_index()
    )

    fig7 = px.pie(
        payment,
        names="payment_type",
        values="payment_value",
        hole=0.45,
        title="Revenue by Payment Method"
    )

    # 8. Top 10 Sellers by Revenue
    sellers = (
        df.groupby("seller_id")["payment_value"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    sellers["Seller"] = [
        f"Seller {i + 1}" for i in range(len(sellers))
    ]

    fig8 = px.bar(
        sellers,
        x="payment_value",
        y="Seller",
        orientation="h",
        color="payment_value",
        title="Top 10 Sellers by Revenue"
    )

    return render_template(

        "sales.html",

        chart1=create_plot(fig1),
        chart2=create_plot(fig2),
        chart3=create_plot(fig3),
        chart4=create_plot(fig4),
        chart5=create_plot(fig5),
        chart6=create_plot(fig6),
        chart7=create_plot(fig7),
        chart8=create_plot(fig8)

    )


# -------------------------------------------------------
# CUSTOMER ANALYTICS
# -------------------------------------------------------

@app.route("/customers")
def customers():
    # 1. Customers by State
    customer_state = (
        df.groupby("customer_state")["customer_unique_id"]
        .nunique()
        .reset_index(name="Customers")
        .sort_values("Customers", ascending=False)
    )

    fig1 = px.bar(
        customer_state,
        x="customer_state",
        y="Customers",
        color="Customers",
        title="Customers by State"
    )

    # 2. Top Purchasing Cities
    top_cities = (
        df.groupby("customer_city")["payment_value"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig2 = px.bar(
        top_cities,
        x="payment_value",
        y="customer_city",
        orientation="h",
        color="payment_value",
        title="Top 10 Purchasing Cities"
    )

    # 3. Customer Lifetime Value
    clv = df.dropna(subset=["customer_lifetime_value"])

    clv["log_clv"] = np.log1p(clv["customer_lifetime_value"])

    clv = clv.replace([np.inf, -np.inf], np.nan)
    clv = clv.dropna(subset=["log_clv"])

    clv["CLV Range"] = pd.cut(
        clv["log_clv"],
        bins=8
    ).astype(str)

    clv_dist = (
        clv.groupby("CLV Range")
        .size()
        .reset_index(name="Customers")
    )

    fig3 = px.bar(
        clv_dist,
        x="CLV Range",
        y="Customers",
        text="Customers",
        color="Customers",
        title="Customer Lifetime Value Distribution"
    )

    # 4. Repeat vs One-Time Customers
    repeat = (
        df.groupby("repeat_customer")["customer_unique_id"]
        .nunique()
        .reset_index(name="Customers")
    )

    repeat["Customer Type"] = repeat["repeat_customer"].map({
        "No": "One-Time",
        "Yes": "Repeat"
    })

    fig4 = px.pie(
        repeat,
        names="Customer Type",
        values="Customers",
        hole=0.45,
        title="Repeat Customer Analysis"
    )

    # 5 Monthly New Customers
    monthly_customers = (
        df.groupby("purchase_month")["customer_unique_id"]
        .nunique()
        .reset_index(name="Customers")
    )

    fig5 = px.line(
        monthly_customers,
        x="purchase_month",
        y="Customers",
        markers=True,
        title="Monthly Customers"
    )

    # 6. Top 10 High Value Customers
    top_customers = (
        df.groupby("customer_unique_id")["customer_lifetime_value"]
        .max()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    top_customers["Customer"] = [
        f"Customer {i + 1}"
        for i in range(len(top_customers))
    ]

    fig6 = px.bar(
        top_customers,
        x="customer_lifetime_value",
        y="Customer",
        orientation="h",
        color="customer_lifetime_value",
        title="Top 10 High Value Customers"
    )

    return render_template(

        "customers.html",

        chart1=create_plot(fig1),
        chart2=create_plot(fig2),
        chart3=create_plot(fig3),
        chart4=create_plot(fig4),
        chart5=create_plot(fig5),
        chart6=create_plot(fig6)

    )


# -------------------------------------------------------
# PRODUCT ANALYTICS
# -------------------------------------------------------

@app.route("/products")
def products():

    # -----------------------------
    # 1. Top Selling Categories (Bar Chart)
    # -----------------------------
    top_categories = (
        df.groupby("product_category_name_english")["order_item_id"]
        .count()
        .sort_values(ascending=False)
        .head(10)
        .reset_index(name="Orders")
    )

    fig1 = px.bar(
        top_categories,
        x="product_category_name_english",
        y="Orders",
        color="Orders",
        text="Orders",
        title="Top 10 Selling Categories"
    )

    fig1.update_layout(
        template="plotly_white",
        xaxis_tickangle=-45
    )

    # -----------------------------
    # 2. Revenue by Category (Donut Chart)
    # -----------------------------
    category_revenue = (
        df.groupby("product_category_name_english")["payment_value"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig2 = px.pie(
        category_revenue,
        names="product_category_name_english",
        values="payment_value",
        hole=0.45,
        title="Revenue Share by Category"
    )

    fig2.update_layout(template="plotly_white")

    # -----------------------------
    # 3. Product Price Distribution (Histogram)
    # -----------------------------
    fig3 = px.histogram(
        df,
        x="price",
        nbins=40,
        title="Product Price Distribution"
    )

    fig3.update_layout(template="plotly_white")

    # -----------------------------
    # 4. Product Weight Distribution (Box Plot)
    # -----------------------------
    fig4 = px.box(
        df,
        y="product_weight_g",
        points="outliers",
        title="Product Weight Distribution"
    )

    fig4.update_layout(template="plotly_white")

    # -----------------------------
    # 5. Average Price by Category (Line Chart)
    # -----------------------------
    avg_price = (
        df.groupby("product_category_name_english")["price"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig5 = px.line(
        avg_price,
        x="product_category_name_english",
        y="price",
        markers=True,
        title="Average Product Price by Category"
    )

    fig5.update_layout(
        template="plotly_white",
        xaxis_tickangle=-45,
        xaxis_title="Category",
        yaxis_title="Average Price"
    )

    # -----------------------------
    # 6. Product Popularity (Scatter Plot)
    # -----------------------------
    popularity = (
        df.groupby("product_category_name_english")["customer_unique_id"]
        .nunique()
        .sort_values(ascending=False)
        .head(10)
        .reset_index(name="Customers")
    )

    fig6 = px.scatter(
        popularity,
        x="Customers",
        y="product_category_name_english",
        size="Customers",
        color="Customers",
        title="Most Popular Categories"
    )

    fig6.update_layout(template="plotly_white")

    # -----------------------------
    # 7. Product Photos (Bar Chart)
    # -----------------------------
    photos = (
        df["product_photos_qty"]
        .value_counts()
        .sort_index()
        .reset_index()
    )

    photos.columns = ["Photos", "Products"]

    fig7 = px.bar(
        photos,
        x="Photos",
        y="Products",
        color="Products",
        text="Products",
        title="Product Photos Distribution"
    )

    fig7.update_layout(template="plotly_white")

    # -----------------------------
    # 8. Average Product Dimensions (Bar Chart)
    # -----------------------------
    dimensions = (
        df[
            [
                "product_length_cm",
                "product_height_cm",
                "product_width_cm"
            ]
        ]
        .mean()
        .reset_index()
    )

    dimensions.columns = ["Dimension", "Average"]

    fig8 = px.bar(
        dimensions,
        x="Dimension",
        y="Average",
        color="Average",
        text="Average",
        title="Average Product Dimensions"
    )

    fig8.update_layout(template="plotly_white")

    # -----------------------------
    # Render Template
    # -----------------------------
    return render_template(
        "products.html",
        chart1=create_plot(fig1),
        chart2=create_plot(fig2),
        chart3=create_plot(fig3),
        chart4=create_plot(fig4),
        chart5=create_plot(fig5),
        chart6=create_plot(fig6),
        chart7=create_plot(fig7),
        chart8=create_plot(fig8)
    )
# -------------------------------------------------------
# SELLER ANALYTICS
# -------------------------------------------------------

@app.route("/sellers")
def sellers():

    # -------------------------------------------------
    # 1. Top Sellers by Revenue (Bar Chart)
    # -------------------------------------------------
    seller_revenue = (
        df.groupby("seller_id")["payment_value"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    seller_revenue["Seller"] = [
        f"Seller {i+1}" for i in range(len(seller_revenue))
    ]

    fig1 = px.bar(
        seller_revenue,
        x="Seller",
        y="payment_value",
        color="payment_value",
        text="payment_value",
        title="Top 10 Sellers by Revenue"
    )

    # -------------------------------------------------
    # 2. Top Sellers by Orders (Line Chart)
    # -------------------------------------------------
    seller_orders = (
        df.groupby("seller_id")["order_id"]
        .nunique()
        .sort_values(ascending=False)
        .head(10)
        .reset_index(name="Orders")
    )

    seller_orders["Seller"] = [
        f"Seller {i+1}" for i in range(len(seller_orders))
    ]

    fig2 = px.line(
        seller_orders,
        x="Seller",
        y="Orders",
        markers=True,
        title="Top Sellers by Orders"
    )

    # -------------------------------------------------
    # 3. Seller Distribution by State (Donut Chart)
    # -------------------------------------------------
    seller_state = (
        df.groupby("seller_state")["seller_id"]
        .nunique()
        .reset_index(name="Sellers")
    )

    fig3 = px.histogram(
        df,
        x="seller_state",
        color="seller_state",
        title="Seller Distribution by State"
    )


    # -------------------------------------------------
    # 4. Seller Revenue Distribution (Box Plot)
    # -------------------------------------------------
    revenue_distribution = (
        df.groupby("seller_id")["payment_value"]
        .sum()
        .reset_index()
    )

    fig4 = px.box(
        revenue_distribution,
        y="payment_value",
        points="outliers",
        title="Seller Revenue Distribution"
    )

    # -------------------------------------------------
    # 5. Seller Performance (Scatter Plot)
    # -------------------------------------------------
    seller_score = (
        df.groupby("seller_id")
        .agg({
            "review_score": "mean",
            "order_id": "nunique"
        })
        .reset_index()
    )

    seller_score.columns = [
        "seller_id",
        "Average Review Score",
        "Orders"
    ]

    fig5 = px.scatter(
        seller_score,
        x="Orders",
        y="Average Review Score",
        size="Orders",
        color="Average Review Score",
        title="Seller Performance Score"
    )

    # -------------------------------------------------
    # 6. Average Delivery Time (Bar Chart)
    # -------------------------------------------------
    seller_delivery = (
        df.groupby("seller_id")["delivery_time"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    seller_delivery["Seller"] = [
        f"Seller {i+1}" for i in range(len(seller_delivery))
    ]

    fig6 = px.bar(
        seller_delivery,
        x="Seller",
        y="delivery_time",
        color="delivery_time",
        text="delivery_time",
        title="Average Delivery Time by Seller"
    )

    # -------------------------------------------------
    # 7. Review Score Distribution (Histogram)
    # -------------------------------------------------
    fig7 = px.histogram(
        df,
        x="review_score",
        nbins=5,
        color="review_score",
        title="Seller Review Score Distribution"
    )

    # -------------------------------------------------
    # 8. Revenue vs Orders (Scatter Plot)
    # -------------------------------------------------
    seller_analysis = (
        df.groupby("seller_id")
        .agg({
            "payment_value": "sum",
            "order_id": "nunique"
        })
        .reset_index()
    )

    seller_analysis.columns = [
        "Seller",
        "Revenue",
        "Orders"
    ]

    fig8 = px.scatter(
        seller_analysis,
        x="Orders",
        y="Revenue",
        size="Revenue",
        color="Revenue",
        hover_name="Seller",
        title="Seller Revenue vs Orders"
    )

    # -------------------------------------------------
    # Apply Common Layout
    # -------------------------------------------------
    figures = [fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8]

    for fig in figures:
        fig.update_layout(
            template="plotly_white",
            height=450,
            margin=dict(l=20, r=20, t=60, b=20)
        )

    return render_template(
        "sellers.html",
        chart1=create_plot(fig1),
        chart2=create_plot(fig2),
        chart3=create_plot(fig3),
        chart4=create_plot(fig4),
        chart5=create_plot(fig5),
        chart6=create_plot(fig6),
        chart7=create_plot(fig7),
        chart8=create_plot(fig8)
    )

# -------------------------------------------------------
# DELIVERY ANALYTICS
# -------------------------------------------------------

@app.route("/delivery")
def delivery():

    # ---------------------------------------
    # 1. Delivery Time Distribution (Box Plot)
    # ---------------------------------------
    delivery_dist = df[df["delivery_time"].notna()]

    fig1 = px.box(
        delivery_dist,
        y="delivery_time",
        points="outliers",
        title="Delivery Time Distribution"
    )

    # ---------------------------------------
    # 2. Shipping Duration Distribution (Histogram)
    # ---------------------------------------
    shipping = df[df["shipping_duration"].notna()]
    shipping_bar = (
        shipping["shipping_duration"]
        .round()
        .value_counts()
        .sort_index()
        .reset_index()
    )

    shipping_bar.columns = ["Days", "Orders"]

    fig2 = px.bar(
        shipping_bar,
        x="Days",
        y="Orders",
        color="Orders",
        text="Orders",
        title="Shipping Duration Distribution"
    )

    # ---------------------------------------
    # 3. Delayed vs On-Time Delivery (Donut Chart)
    # ---------------------------------------
    if "delivery_status" in df.columns:

        delay = (
            df["delivery_status"]
            .value_counts()
            .reset_index()
        )

        delay.columns = ["Status", "Count"]

    else:

        delay = pd.DataFrame({
            "Status": ["Available", "Missing"],
            "Count": [len(df), 0]
        })

    fig3 = px.pie(
        delay,
        names="Status",
        values="Count",
        hole=0.45,
        title="Delayed vs On-Time Deliveries"
    )

    fig3.update_traces(textinfo="percent+label")

    # ---------------------------------------
    # 4. Monthly Delivery Trend (Line Chart)
    # ---------------------------------------
    monthly_delivery = (
        df.groupby("purchase_month")["delivery_time"]
        .mean()
        .reset_index()
    )

    fig4 = px.line(
        monthly_delivery,
        x="purchase_month",
        y="delivery_time",
        markers=True,
        title="Monthly Average Delivery Time"
    )

    # ---------------------------------------
    # 5. Average Delivery Time by State
    # (Horizontal Bar Chart)
    # ---------------------------------------

    state_delivery = (
        df.groupby("customer_state")["delivery_time"]
        .mean()
        .sort_values(ascending=False)
        .head(15)
        .reset_index()
    )

    fig5 = px.bar(
        state_delivery,
        x="delivery_time",
        y="customer_state",
        orientation="h",
        color="delivery_time",
        text=state_delivery["delivery_time"].round(1),
        title="Average Delivery Time by State"
    )

    # ---------------------------------------
    # 6. Estimated vs Actual Delivery
    # (Scatter Plot)
    # ---------------------------------------

    estimated_actual = df[
        [
            "estimated_delivery_days",
            "delivery_time"
        ]
    ].dropna()

    fig6 = px.scatter(
        estimated_actual,
        x="estimated_delivery_days",
        y="delivery_time",
        color="delivery_time",
        opacity=0.7,
        title="Estimated vs Actual Delivery Time"
    )

    # ---------------------------------------
    # 7. Delivery Time by Order Status
    # (Box Plot)
    # ---------------------------------------

    fig7 = px.box(
        df,
        x="order_status",
        y="delivery_time",
        color="order_status",
        points="outliers",
        title="Delivery Time by Order Status"
    )

    # ---------------------------------------
    # 8. Shipping Performance
    # (Bar Chart)
    # ---------------------------------------

    shipping_perf = (
        df.groupby("order_status")["delivery_time"]
        .mean()
        .reset_index()
    )

    fig8 = px.bar(
        shipping_perf,
        x="order_status",
        y="delivery_time",
        color="delivery_time",
        text=shipping_perf["delivery_time"].round(1),
        title="Average Delivery Time by Order Status"
    )

    # ---------------------------------------
    # Common Professional Layout
    # ---------------------------------------

    figures = [fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8]

    for fig in figures:

        fig.update_layout(
            template="plotly_white",
            height=450,
            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20
            ),
            title_x=0.5
        )

    # ---------------------------------------
    # Render Template
    # ---------------------------------------

    return render_template(

        "delivery.html",

        chart1=create_plot(fig1),
        chart2=create_plot(fig2),
        chart3=create_plot(fig3),
        chart4=create_plot(fig4),
        chart5=create_plot(fig5),
        chart6=create_plot(fig6),
        chart7=create_plot(fig7),
        chart8=create_plot(fig8)

    )

# -------------------------------------------------------
# PAYMENT & REVIEW ANALYTICS
# -------------------------------------------------------
@app.route("/payments")
def payments():

    # ----------------------------------------
    # 1. Payment Method Distribution (Donut)
    # ----------------------------------------

    payment_method = (
        df.groupby("payment_type")["payment_value"]
        .sum()
        .reset_index()
    )

    fig1 = px.pie(
        payment_method,
        names="payment_type",
        values="payment_value",
        hole=0.45,
        title="Payment Method Distribution"
    )

    # ----------------------------------------
    # 2. Installment Usage (Line Chart)
    # ----------------------------------------

    installments = (
        df.groupby("payment_installments")["order_id"]
        .nunique()
        .reset_index(name="Orders")
    )

    fig2 = px.line(
        installments,
        x="payment_installments",
        y="Orders",
        markers=True,
        title="Installment Usage"
    )

    # ----------------------------------------
    # 3. Payment Value Distribution (Box Plot)
    # ----------------------------------------

    fig3 = px.box(
        df,
        y="payment_value",
        points="outliers",
        title="Payment Value Distribution"
    )

    # ----------------------------------------
    # 4. Review Score Distribution (Histogram)
    # ----------------------------------------

    fig4 = px.histogram(
        df,
        x="review_score",
        nbins=5,
        color="review_score",
        title="Review Score Distribution"
    )

    # ----------------------------------------
    # 5. Positive vs Negative Reviews (Donut)
    # ----------------------------------------

    review_sentiment = df.copy()

    review_sentiment["Review Type"] = np.where(
        review_sentiment["review_score"] >= 4,
        "Positive",
        "Negative"
    )

    sentiment = (
        review_sentiment["Review Type"]
        .value_counts()
        .reset_index()
    )

    sentiment.columns = ["Review Type", "Count"]

    fig5 = px.pie(
        sentiment,
        names="Review Type",
        values="Count",
        hole=0.45,
        title="Positive vs Negative Reviews"
    )

    fig5.update_traces(textinfo="percent+label")

    # ----------------------------------------
    # 6. Monthly Review Score Trend (Line)
    # ----------------------------------------

    review_trend = (
        df.groupby("purchase_month")["review_score"]
        .mean()
        .reset_index()
    )

    fig6 = px.line(
        review_trend,
        x="purchase_month",
        y="review_score",
        markers=True,
        title="Monthly Review Score Trend"
    )

    # ----------------------------------------
    # 7. Customer Satisfaction (Bar Chart)
    # ----------------------------------------

    satisfaction = (
        df.groupby("review_score")["customer_unique_id"]
        .nunique()
        .reset_index(name="Customers")
    )

    fig7 = px.bar(
        satisfaction,
        x="review_score",
        y="Customers",
        color="Customers",
        text="Customers",
        title="Customer Satisfaction Metrics"
    )

    # ----------------------------------------
    # 8. Payment Value vs Review Score
    # (Scatter Plot)
    # ----------------------------------------

    payment_review = (
        df.groupby("review_score")["payment_value"]
        .mean()
        .reset_index()
    )

    fig8 = px.scatter(
        payment_review,
        x="review_score",
        y="payment_value",
        size="payment_value",
        color="payment_value",
        title="Payment Value vs Review Score"
    )

    # ----------------------------------------
    # Common Professional Layout
    # ----------------------------------------

    figures = [fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8]

    for fig in figures:

        fig.update_layout(
            template="plotly_white",
            height=450,
            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20
            ),
            title_x=0.5
        )

    # ----------------------------------------
    # Render Template
    # ----------------------------------------

    return render_template(

        "payments.html",

        chart1=create_plot(fig1),
        chart2=create_plot(fig2),
        chart3=create_plot(fig3),
        chart4=create_plot(fig4),
        chart5=create_plot(fig5),
        chart6=create_plot(fig6),
        chart7=create_plot(fig7),
        chart8=create_plot(fig8)

    )


# -------------------------------------------------------
# DATASET EXPLORER
# -------------------------------------------------------

@app.route("/explorer")
def explorer():

    # ---------------------------------------------------
    # Search & Filters
    # ---------------------------------------------------

    search = request.args.get("search", "")

    state = request.args.get("state", "")

    category = request.args.get("category", "")

    payment = request.args.get("payment", "")

    status = request.args.get("status", "")

    month = request.args.get("month", "")

    review = request.args.get("review", "")

    sort_column = request.args.get("sort", "")

    page = request.args.get("page", 1, type=int)

    rows_per_page = 20

    explorer_df = df.copy()

    # ---------------------------------------------------
    # Global Search
    # ---------------------------------------------------

    if search:

        explorer_df = explorer_df[

            explorer_df.astype(str)

            .apply(

                lambda row:

                row.str.contains(

                    search,

                    case=False,

                    na=False

                ).any(),

                axis=1

            )

        ]

    # ---------------------------------------------------
    # Customer State Filter
    # ---------------------------------------------------

    if state:

        explorer_df = explorer_df[

            explorer_df["customer_state"] == state

        ]

    # ---------------------------------------------------
    # Product Category Filter
    # ---------------------------------------------------

    if category:

        explorer_df = explorer_df[

            explorer_df["product_category_name_english"] == category

        ]

    # ---------------------------------------------------
    # Payment Type Filter
    # ---------------------------------------------------

    if payment:

        explorer_df = explorer_df[

            explorer_df["payment_type"] == payment

        ]

    # ---------------------------------------------------
    # Order Status Filter
    # ---------------------------------------------------

    if status:

        explorer_df = explorer_df[

            explorer_df["order_status"] == status

        ]

    # ---------------------------------------------------
    # Purchase Month Filter
    # ---------------------------------------------------

    if month:

        explorer_df = explorer_df[

            explorer_df["purchase_month"] == month

        ]

    # ---------------------------------------------------
    # Review Score Filter
    # ---------------------------------------------------

    if review:

        explorer_df = explorer_df[

            explorer_df["review_score"] == int(review)

        ]

    # ---------------------------------------------------
    # Sorting
    # ---------------------------------------------------

    if sort_column in explorer_df.columns:

        explorer_df = explorer_df.sort_values(

            by=sort_column

        )

    # ---------------------------------------------------
    # Pagination
    # ---------------------------------------------------

    total_rows = len(explorer_df)

    total_pages = max(

        1,

        ceil(total_rows / rows_per_page)

    )

    start = (page - 1) * rows_per_page

    end = start + rows_per_page

    table_data = explorer_df.iloc[start:end]

    # ---------------------------------------------------
    # Dataset Statistics
    # ---------------------------------------------------

    total_columns = len(df.columns)

    missing_values = int(df.isna().sum().sum())

    duplicate_rows = int(df.duplicated().sum())

    numeric_columns = len(
        df.select_dtypes(include="number").columns
    )

    categorical_columns = len(
        df.select_dtypes(include=["object"]).columns
    )

    datetime_columns = len(
        df.select_dtypes(include=["datetime64[ns]"]).columns
    )

    total_orders = df["order_id"].nunique()

    total_customers = df["customer_unique_id"].nunique()

    total_sellers = df["seller_id"].nunique()

    total_products = df["product_id"].nunique()

    total_revenue = round(
        df["payment_value"].sum(),
        2
    )

    average_order_value = round(
        df["payment_value"].mean(),
        2
    )

    # ---------------------------------------------------
    # Dropdown Values
    # ---------------------------------------------------

    states = sorted(
        df["customer_state"]
        .dropna()
        .unique()
    )

    categories = sorted(
        df["product_category_name_english"]
        .dropna()
        .unique()
    )

    payment_types = sorted(
        df["payment_type"]
        .dropna()
        .unique()
    )

    order_status = sorted(
        df["order_status"]
        .dropna()
        .unique()
    )

    purchase_months = sorted(
        df["purchase_month"]
        .dropna()
        .unique()
    )

    review_scores = sorted(
        df["review_score"]
        .dropna()
        .unique()
    )

    # ---------------------------------------------------
    # Table
    # ---------------------------------------------------

    table_html = table_data.to_html(

        classes="""
        table
        table-hover
        table-striped
        table-bordered
        align-middle
        text-nowrap
        """,

        index=False,

        border=0

    )

    columns = table_data.columns.tolist()

    # ---------------------------------------------------
    # Render Template
    # ---------------------------------------------------

    return render_template(

        "explorer.html",

        # Table
        tables=[table_html],
        columns=columns,

        # Pagination
        page=page,
        total_pages=total_pages,

        # Search
        search=search,
        state=state,
        category=category,
        payment=payment,
        status=status,
        month=month,
        review=review,
        sort=sort_column,

        # Dataset Statistics
        total_rows=total_rows,
        total_columns=total_columns,
        missing_values=missing_values,
        duplicate_rows=duplicate_rows,
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
        datetime_columns=datetime_columns,

        total_orders=total_orders,
        total_customers=total_customers,
        total_products=total_products,
        total_sellers=total_sellers,
        total_revenue=total_revenue,
        average_order_value=average_order_value,

        # Dropdown Lists
        states=states,
        categories=categories,
        payment_types=payment_types,
        order_status=order_status,
        purchase_months=purchase_months,
        review_scores=review_scores

    )
# -------------------------------------------------------
# DOWNLOAD CSV
# -------------------------------------------------------

@app.route("/download")
def download():
    file_path = (
        "feature_engineered_dataset.csv"
    )

    return send_file(
        file_path,
        as_attachment=True
    )


# -------------------------------------------------------
# ERROR HANDLING
# -------------------------------------------------------

@app.errorhandler(404)
def page_not_found(error):
    return render_template(
        "404.html"
    ), 404


# -------------------------------------------------------
# RUN APPLICATION
# -------------------------------------------------------

if __name__ == "__main__":
    app.run(
        debug=True
    )