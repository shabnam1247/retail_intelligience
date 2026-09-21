from io import BytesIO

import pandas as pd

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)


def create_excel_report(df):

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="Sales Data"
        )

    output.seek(0)

    return output


def create_pdf_report(df):

    output = BytesIO()

    document = SimpleDocTemplate(
        output,
        pagesize=A4
    )

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "Retail Intelligence Report",
            styles["Title"]
        )
    )

    elements.append(
        Spacer(1, 20)
    )

    revenue = df["sales_amount"].sum()
    orders = df["order_id"].nunique()
    customers = df["customer_id"].nunique()
    units = df["quantity"].sum()

    kpi_data = [
        ["Metric", "Value"],
        [
            "Total Revenue",
            f"₹{revenue:,.2f}"
        ],
        [
            "Orders",
            f"{orders:,}"
        ],
        [
            "Customers",
            f"{customers:,}"
        ],
        [
            "Units Sold",
            f"{units:,}"
        ]
    ]

    table = Table(kpi_data)

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#172033")
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                8
            )
        ])
    )

    elements.append(table)

    document.build(elements)

    output.seek(0)

    return output