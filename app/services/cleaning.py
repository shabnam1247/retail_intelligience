import pandas as pd


REQUIRED_COLUMNS = [
    "order_id",
    "order_date",
    "customer_id",
    "product_id",
    "quantity",
    "unit_price",
    "discount_pct",
    "sales_amount"
]


def clean_sales_data(df):

    df = df.copy()

    rows_before = len(df)

    # Clean column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

    # Column aliases
    aliases = {

        "date": "order_date",
        "orderid": "order_id",
        "customerid": "customer_id",
        "productid": "product_id",
        "qty": "quantity",
        "price": "unit_price",
        "discount": "discount_pct",
        "sales": "sales_amount",
        "total_amount": "sales_amount",
        "total_ammount": "sales_amount"
    }

    df.rename(
        columns=aliases,
        inplace=True
    )

    # Create missing columns
    if "discount_pct" not in df.columns:
        df["discount_pct"] = 0

    if "sales_amount" not in df.columns:
        df["sales_amount"] = None

    # Required column validation
    missing = [
        col
        for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            "Missing columns: "
            + ", ".join(missing)
        )

    # Date
    df["order_date"] = pd.to_datetime(
        df["order_date"],
        errors="coerce"
    )

    # Numeric
    numeric_columns = [
        "order_id",
        "customer_id",
        "product_id",
        "quantity",
        "unit_price",
        "discount_pct",
        "sales_amount"
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Fill values
    df["discount_pct"] = (
        df["discount_pct"]
        .fillna(0)
        .clip(0, 100)
    )

    df["quantity"] = (
        df["quantity"]
        .fillna(1)
        .clip(lower=1)
    )

    df["unit_price"] = (
        df["unit_price"]
        .fillna(0)
    )

    # Calculate missing sales
    calculated_sales = (
        df["quantity"]
        * df["unit_price"]
        * (
            1 -
            df["discount_pct"] / 100
        )
    )

    df["sales_amount"] = (
        df["sales_amount"]
        .fillna(calculated_sales)
    )

    # Text fields
    if "payment_method" not in df.columns:
        df["payment_method"] = "Unknown"

    if "channel" not in df.columns:
        df["channel"] = "Unknown"

    df["payment_method"] = (
        df["payment_method"]
        .fillna("Unknown")
        .astype(str)
    )

    df["channel"] = (
        df["channel"]
        .fillna("Unknown")
        .astype(str)
    )

    # Remove invalid rows
    df.dropna(
        subset=[
            "order_id",
            "order_date",
            "customer_id",
            "product_id"
        ],
        inplace=True
    )

    # Remove duplicate orders
    df.drop_duplicates(
        subset=["order_id"],
        keep="first",
        inplace=True
    )

    # Remove invalid sales
    df = df[
        df["sales_amount"] >= 0
    ]

    # Convert types
    df["order_id"] = df["order_id"].astype(int)
    df["customer_id"] = df["customer_id"].astype(int)
    df["product_id"] = df["product_id"].astype(int)
    df["quantity"] = df["quantity"].astype(int)

    df["order_date"] = (
        df["order_date"].dt.date
    )

    rows_after = len(df)

    stats = {
        "rows_before": rows_before,
        "rows_after": rows_after,
        "rows_removed": rows_before - rows_after
    }

    return df, stats