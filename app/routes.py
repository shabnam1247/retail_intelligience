from io import BytesIO

import pandas as pd

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file
)

from .db import get_connection

from .services.analytics import (
    get_sales_data,
    calculate_kpis,
    monthly_sales,
    payment_analysis,
    channel_analysis,
    product_analysis
)

from .services.cleaning import (
    clean_sales_data
)

from .services.segmentation import (
    create_customer_segments
)

from .services.forecasting import (
    forecast_sales
)

from .services.reports import (
    create_excel_report,
    create_pdf_report
)


bp = Blueprint(
    "main",
    __name__
)


# =========================================================
# DASHBOARD
# =========================================================

@bp.route("/")
def dashboard():

    df = get_sales_data()

    kpis = calculate_kpis(df)

    monthly = monthly_sales(df)

    products = product_analysis(df)

    return render_template(
        "dashboard.html",
        kpis=kpis,
        monthly=monthly,
        products=products
    )


# =========================================================
# DATA UPLOAD
# =========================================================

@bp.route(
    "/upload",
    methods=["GET", "POST"]
)
def upload():

    if request.method == "POST":

        file = request.files.get(
            "file"
        )

        if not file:

            flash(
                "Please select a CSV file.",
                "danger"
            )

            return redirect(
                url_for("main.upload")
            )

        if file.filename == "":

            flash(
                "Please select a CSV file.",
                "danger"
            )

            return redirect(
                url_for("main.upload")
            )

        try:

            df = pd.read_csv(file)

            cleaned_df, stats = (
                clean_sales_data(df)
            )

            connection = get_connection()

            cursor = connection.cursor()

            # Clear old data
            cursor.execute(
                "DELETE FROM sales"
            )

            insert_query = """
                INSERT INTO sales (
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
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
            """

            values = []

            for _, row in cleaned_df.iterrows():

                values.append((
                    int(row["order_id"]),
                    row["order_date"],
                    int(row["customer_id"]),
                    int(row["product_id"]),
                    int(row["quantity"]),
                    float(row["unit_price"]),
                    float(row["discount_pct"]),
                    float(row["sales_amount"]),
                    str(row["payment_method"]),
                    str(row["channel"])
                ))

            cursor.executemany(
                insert_query,
                values
            )

            connection.commit()

            cursor.close()
            connection.close()

            flash(
                f"Successfully uploaded {len(cleaned_df):,} records.",
                "success"
            )

            flash(
                f"Removed {stats['rows_removed']:,} invalid/duplicate rows during cleaning.",
                "info"
            )

            return redirect(
                url_for("main.dashboard")
            )

        except Exception as e:

            flash(
                f"Upload failed: {str(e)}",
                "danger"
            )

            return redirect(
                url_for("main.upload")
            )

    return render_template(
        "upload.html"
    )


# =========================================================
# EDA
# =========================================================

@bp.route("/eda")
def eda():

    df = get_sales_data()

    monthly = monthly_sales(df)

    payment = payment_analysis(df)

    channel = channel_analysis(df)

    products = product_analysis(df)

    return render_template(
        "eda.html",
        monthly=monthly,
        payment=payment,
        channel=channel,
        products=products
    )


# =========================================================
# CUSTOMER SEGMENTATION
# =========================================================

@bp.route("/segmentation")
def segmentation():

    df = get_sales_data()

    segments = create_customer_segments(
        df
    )

    if segments.empty:

        records = []

    else:

        records = (
            segments
            .head(100)
            .to_dict("records")
        )

    return render_template(
        "segmentation.html",
        segments=records
    )


# =========================================================
# SALES FORECAST
# =========================================================

@bp.route("/forecast")
def forecast():

    df = get_sales_data()

    predictions = forecast_sales(
        df,
        days=30
    )

    return render_template(
        "forecast.html",
        predictions=predictions
    )


# =========================================================
# CSV REPORT
# =========================================================

@bp.route("/reports/csv")
def report_csv():

    df = get_sales_data()

    output = BytesIO()

    df.to_csv(
        output,
        index=False
    )

    output.seek(0)

    return send_file(
        output,
        mimetype="text/csv",
        as_attachment=True,
        download_name="retail_sales_report.csv"
    )


# =========================================================
# EXCEL REPORT
# =========================================================

@bp.route("/reports/excel")
def report_excel():

    df = get_sales_data()

    output = create_excel_report(
        df
    )

    return send_file(
        output,
        mimetype=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        as_attachment=True,
        download_name="retail_sales_report.xlsx"
    )


# =========================================================
# PDF REPORT
# =========================================================

@bp.route("/reports/pdf")
def report_pdf():

    df = get_sales_data()

    output = create_pdf_report(
        df
    )

    return send_file(
        output,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="retail_sales_report.pdf"
    )


# =========================================================
# OPTIONAL REPORT PAGE
# =========================================================

@bp.route("/reports")
def reports():

    return render_template(
        "reports.html"
    )