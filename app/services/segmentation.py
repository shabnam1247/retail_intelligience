import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


def create_customer_segments(df):

    if df.empty:
        return pd.DataFrame()

    data = df.copy()

    data["order_date"] = pd.to_datetime(
        data["order_date"]
    )

    snapshot_date = (
        data["order_date"].max()
        + pd.Timedelta(days=1)
    )

    rfm = (
        data.groupby("customer_id")
        .agg(
            Recency=(
                "order_date",
                lambda x:
                (snapshot_date - x.max()).days
            ),
            Frequency=(
                "order_id",
                "nunique"
            ),
            Monetary=(
                "sales_amount",
                "sum"
            )
        )
        .reset_index()
    )

    if len(rfm) < 4:

        rfm["Segment"] = "Customer"

        return rfm

    features = [
        "Recency",
        "Frequency",
        "Monetary"
    ]

    scaler = StandardScaler()

    scaled = scaler.fit_transform(
        rfm[features]
    )

    model = KMeans(
        n_clusters=4,
        random_state=42,
        n_init=10
    )

    rfm["Cluster"] = model.fit_predict(
        scaled
    )

    # Rank clusters
    summary = (
        rfm.groupby("Cluster")
        .agg(
            Recency=("Recency", "mean"),
            Frequency=("Frequency", "mean"),
            Monetary=("Monetary", "mean")
        )
    )

    summary["Score"] = (
        summary["Monetary"].rank()
        + summary["Frequency"].rank()
        - summary["Recency"].rank()
    )

    ordered = summary.sort_values(
        "Score",
        ascending=False
    ).index.tolist()

    labels = [
        "High Value",
        "Loyal",
        "Potential",
        "At Risk"
    ]

    mapping = {}

    for i, cluster in enumerate(ordered):

        mapping[cluster] = labels[
            min(i, len(labels) - 1)
        ]

    rfm["Segment"] = rfm[
        "Cluster"
    ].map(mapping)

    return rfm