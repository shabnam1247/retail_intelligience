import pandas as pd

from sklearn.ensemble import RandomForestRegressor


def forecast_sales(df, days=30):

    if df.empty:
        return []

    data = df.copy()

    data["order_date"] = pd.to_datetime(
        data["order_date"]
    )

    daily = (
        data.groupby("order_date")["sales_amount"]
        .sum()
        .sort_index()
    )

    if len(daily) < 30:

        return []

    daily = daily.asfreq("D", fill_value=0)

    temp = pd.DataFrame({
        "sales": daily
    })

    temp["day_of_week"] = (
        temp.index.dayofweek
    )

    temp["month"] = (
        temp.index.month
    )

    temp["day"] = (
        temp.index.day
    )

    temp["lag_1"] = (
        temp["sales"].shift(1)
    )

    temp["lag_7"] = (
        temp["sales"].shift(7)
    )

    temp["rolling_7"] = (
        temp["sales"]
        .rolling(7)
        .mean()
    )

    temp.dropna(
        inplace=True
    )

    if len(temp) < 20:
        return []

    features = [
        "day_of_week",
        "month",
        "day",
        "lag_1",
        "lag_7",
        "rolling_7"
    ]

    X = temp[features]
    y = temp["sales"]

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X, y)

    history = daily.copy()

    predictions = []

    last_date = history.index.max()

    for i in range(1, days + 1):

        future_date = (
            last_date
            + pd.Timedelta(days=i)
        )

        lag_1 = (
            history.iloc[-1]
        )

        lag_7 = (
            history.iloc[-7]
            if len(history) >= 7
            else history.mean()
        )

        rolling_7 = (
            history.tail(7).mean()
        )

        X_future = pd.DataFrame([{
            "day_of_week":
                future_date.dayofweek,

            "month":
                future_date.month,

            "day":
                future_date.day,

            "lag_1":
                lag_1,

            "lag_7":
                lag_7,

            "rolling_7":
                rolling_7
        }])

        prediction = float(
            model.predict(X_future)[0]
        )

        prediction = max(
            prediction,
            0
        )

        predictions.append({
            "date":
                future_date.strftime(
                    "%Y-%m-%d"
                ),
            "prediction":
                round(prediction, 2)
        })

        history.loc[
            future_date
        ] = prediction

    return predictions