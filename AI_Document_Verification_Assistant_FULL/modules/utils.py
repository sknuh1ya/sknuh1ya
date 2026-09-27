from pathlib import Path
import json

import fitz  # PyMuPDF
from PIL import Image
import numpy as np


def pdf_to_images(pdf_path: Path):
    """
    Convert each PDF page into an OpenCV-compatible BGR image.
    """
    images = []

    document = fitz.open(str(pdf_path))

    try:
        for page in document:
            # Render page at a reasonable resolution for OCR
            pix = page.get_pixmap(
                matrix=fitz.Matrix(2, 2),
                alpha=False
            )

            # Convert PyMuPDF pixmap to bytes
            image = Image.frombytes(
                "RGB",
                [pix.width, pix.height],
                pix.samples
            )

            # PIL RGB -> NumPy -> OpenCV BGR
            image_array = np.array(image)
            image_bgr = image_array[:, :, ::-1].copy()

            images.append(image_bgr)

    finally:
        document.close()

    return images


def make_json_report(report, output_path):
    """
    Save verification report as JSON.
    """
    output_path = Path(output_path)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False,
            default=str
        )

    return output_path


def make_pdf_report(report, output_path):
    """
    Generate a PDF verification report.

    Supports both the older checklist key:
        Document

    and the newer key:
        Required Document
    """

    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )
    from reportlab.lib import colors

    output_path = Path(output_path)

    styles = getSampleStyleSheet()

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    story = []

    story.append(
        Paragraph(
            "AI Document Verification Report",
            styles["Title"]
        )
    )

    story.append(Spacer(1, 8))

    # ---------------------------------------------------------
    # Application information
    # ---------------------------------------------------------

    application_type = report.get(
        "application_type",
        report.get("application", "N/A")
    )

    overall_status = report.get(
        "overall_status",
        report.get("status", "N/A")
    )

    story.append(
        Paragraph(
            f"<b>Application Type:</b> {application_type}",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Overall Status:</b> {overall_status}",
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 12))

    # ---------------------------------------------------------
    # Checklist
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "Document Checklist",
            styles["Heading2"]
        )
    )

    checklist = report.get("checklist", [])

    table_data = [
        [
            "Required Document",
            "Detected",
            "Status",
            "Details",
        ]
    ]

    for item in checklist:

        required_document = item.get(
            "Required Document",
            item.get("Document", "")
        )

        detected = item.get(
            "Detected",
            ""
        )

        status = item.get(
            "Status",
            ""
        )

        details = item.get(
            "Details",
            ""
        )

        table_data.append(
            [
                str(required_document),
                str(detected),
                str(status),
                str(details),
            ]
        )

    if len(table_data) > 1:

        table = Table(
            table_data,
            colWidths=[
                38 * mm,
                35 * mm,
                28 * mm,
                70 * mm,
            ],
            repeatRows=1,
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey,
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                ]
            )
        )

        story.append(table)

    story.append(Spacer(1, 15))

    # ---------------------------------------------------------
    # Document details
    # ---------------------------------------------------------

    documents = report.get(
        "documents",
        report.get("results", [])
    )

    if documents:

        story.append(
            Paragraph(
                "Document Analysis",
                styles["Heading2"]
            )
        )

        for item in documents:

            file_name = item.get(
                "file_name",
                "Unknown file"
            )

            detected_type = item.get(
                "detected_type",
                "Unknown Document"
            )

            confidence = item.get(
                "confidence",
                0
            )

            quality_score = item.get(
                "quality_score",
                0
            )

            expiry_status = item.get(
                "expiry_status",
                "Not checked"
            )

            expiry_date = item.get(
                "expiry_date"
            )

            story.append(
                Paragraph(
                    f"<b>File:</b> {file_name}",
                    styles["Normal"]
                )
            )

            story.append(
                Paragraph(
                    f"<b>Detected Type:</b> {detected_type}",
                    styles["Normal"]
                )
            )

            story.append(
                Paragraph(
                    f"<b>Classification Confidence:</b> "
                    f"{confidence}%",
                    styles["Normal"]
                )
            )

            story.append(
                Paragraph(
                    f"<b>Image Quality:</b> "
                    f"{quality_score}/100",
                    styles["Normal"]
                )
            )

            story.append(
                Paragraph(
                    f"<b>Expiry Status:</b> "
                    f"{expiry_status}",
                    styles["Normal"]
                )
            )

            if expiry_date:
                story.append(
                    Paragraph(
                        f"<b>Expiry Date:</b> "
                        f"{expiry_date}",
                        styles["Normal"]
                    )
                )

            quality_issues = item.get(
                "quality_issues",
                []
            )

            if quality_issues:
                story.append(
                    Paragraph(
                        "<b>Quality Issues:</b> "
                        + ", ".join(map(str, quality_issues)),
                        styles["Normal"]
                    )
                )

            story.append(Spacer(1, 8))

    # ---------------------------------------------------------
    # Recommended actions
    # ---------------------------------------------------------

    actions = report.get(
        "actions",
        report.get("recommendations", [])
    )

    if actions:

        story.append(
            Paragraph(
                "Recommended Actions",
                styles["Heading2"]
            )
        )

        for action in actions:

            story.append(
                Paragraph(
                    f"• {action}",
                    styles["Normal"]
                )
            )

    story.append(Spacer(1, 15))

    # ---------------------------------------------------------
    # Disclaimer
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "<b>Disclaimer:</b> This system performs preliminary "
            "document screening using OCR, document classification, "
            "quality checks, expiry checks, and duplicate detection. "
            "It does not establish document authenticity or determine "
            "whether a document is genuine or fraudulent. Documents "
            "requiring additional verification should be reviewed "
            "by an authorized human or official authority.",
            styles["Normal"]
        )
    )

    document.build(story)

    return output_path
