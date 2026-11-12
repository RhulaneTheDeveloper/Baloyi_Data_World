import os
from pathlib import Path
from typing import Dict, List

import pandas as pd
import xlsxwriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from config.settings import EXPORTS_DIR


EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


def export_excel_report(df: pd.DataFrame, summary: Dict[str, object], filename: str = "hosi_data_quality_report.xlsx") -> str:
    output_path = EXPORTS_DIR / filename
    workbook = xlsxwriter.Workbook(str(output_path))
    worksheet = workbook.add_worksheet("Summary")

    rows = [
        ["Metric", "Value"],
        ["Total rows", summary.get("row_count", 0)],
        ["Columns", summary.get("column_count", 0)],
        ["Identifier field", summary.get("identifier_field", "")],
        ["Duplicate count", summary.get("duplicate_count", 0)],
        ["Quality score", summary.get("quality_score", 0)],
    ]

    for row_index, row in enumerate(rows):
        for col_index, value in enumerate(row):
            worksheet.write(row_index, col_index, value)

    data_sheet = workbook.add_worksheet("Data")
    for row_index, row in enumerate(df.head(1000).values.tolist()):
        for col_index, value in enumerate(row):
            data_sheet.write(row_index, col_index, value)

    worksheet.autofilter(0, 0, len(rows) - 1, 1)
    workbook.close()
    return str(output_path)


def export_pdf_report(summary: Dict[str, object], filename: str = "hosi_data_quality_report.pdf") -> str:
    output_path = EXPORTS_DIR / filename
    story = []
    story.append(Paragraph("Baloyi Data World Report"))
    story.append(Spacer(1, 12))

    table_data = [
        ["Metric", "Value"],
        ["Row count", str(summary.get("row_count", 0))],
        ["Column count", str(summary.get("column_count", 0))],
        ["Duplicate count", str(summary.get("duplicate_count", 0))],
        ["Quality score", str(summary.get("quality_score", 0))],
    ]

    table = Table(table_data)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f77b4")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )
    story.append(table)

    doc = SimpleDocTemplate(str(output_path), pagesize=A4)
    doc.build(story)
    return str(output_path)
