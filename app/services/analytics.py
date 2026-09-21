import pandas as pd
from app.db import get_connection


def get_sales_data():

    connection = get_connection()

    query = """
        SELECT
            id,
            order_id,
            order_date,
            customer_id,
            product_id,
            quantity,
            unit_price,
            discount_pct,
            sales_amount,
            payment_method,
            channel
        FROM sales
        ORDER BY order_date
    """

    try:

        df = pd.read_sql(query, connection)

    finally:

        connection.close()

    if not df.empty:
        df["order_date"] = pd.to_datetime(df["order_date"])

    return df


def calculate_kpis(df):

    if df.empty:

        return {
            "revenue": 0,
            "orders": 0,
            "customers": 0,
            "units": 0,
            "aov": 0
        }

    revenue = float(df["sales_amount"].sum())

    orders = int(df["order_id"].nunique())

    customers = int(df["customer_id"].nunique())

    units = int(df["quantity"].sum())

    aov = revenue / orders if orders > 0 else 0

    return {
        "revenue": revenue,
        "orders": orders,
        "customers": customers,
        "units": units,
        "aov": aov
    }


def monthly_sales(df):

    if df.empty:
        return []

    temp = df.copy()

    temp["order_date"] = pd.to_datetime(
        temp["order_date"]
    )

    result = (
        temp
        .groupby(
            temp["order_date"].dt.to_period("M")
        )["sales_amount"]
        .sum()
        .reset_index()
    )

    result["month"] = (
        result["order_date"]
        .astype(str)
    )

    result["sales"] = result["sales_amount"].round(2)

    return result[
        ["month", "sales"]
    ].to_dict("records")


def payment_analysis(df):

    if df.empty:
        return []

    result = (
        df.groupby("payment_method")["sales_amount"]
        .sum()
        .reset_index()
    )

    result["sales"] = result["sales_amount"].round(2)

    return result[
        ["payment_method", "sales"]
    ].to_dict("records")


def channel_analysis(df):

    if df.empty:
        return []

    result = (
        df.groupby("channel")["sales_amount"]
        .sum()
        .reset_index()
    )

    result["sales"] = result["sales_amount"].round(2)

    return result[
        ["channel", "sales"]
    ].to_dict("records")


def product_analysis(df):

    if df.empty:
        return []

    result = (
        df.groupby("product_id")["sales_amount"]
        .sum()
        .reset_index()
        .sort_values(
            "sales_amount",
            ascending=False
        )
        .head(10)
    )

    result["product"] = (
        "Product "
        + result["product_id"].astype(str)
    )

    result["sales"] = result["sales_amount"].round(2)

    return result[
        ["product", "sales"]
    ].to_dict("records")