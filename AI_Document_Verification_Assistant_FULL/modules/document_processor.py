from pathlib import Path
import hashlib

import cv2
import numpy as np

from modules.ocr_engine import extract_text
from modules.document_classifier import classify_document
from modules.image_quality import analyze_quality
from modules.date_checker import check_expiry
from modules.utils import pdf_to_images


ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".pdf",
}


# ---------------------------------------------------------
# SHA-256
# ---------------------------------------------------------

def calculate_sha256(path: Path) -> str:

    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


# ---------------------------------------------------------
# Process uploaded document
# ---------------------------------------------------------

def process_uploaded_file(path: Path) -> dict:

    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(
            "Unsupported file type."
        )

    if path.stat().st_size == 0:
        raise ValueError(
            "The uploaded document is empty."
        )

    # -----------------------------------------------------
    # Convert PDF or load image
    # -----------------------------------------------------

    if path.suffix.lower() == ".pdf":

        images = pdf_to_images(
            path
        )

    else:

        image = cv2.imread(
            str(path)
        )

        images = (
            [image]
            if image is not None
            else []
        )

    if not images:
        raise ValueError(
            "Unable to read the document."
        )

    # -----------------------------------------------------
    # OCR and quality
    # -----------------------------------------------------

    all_text = []
    quality_results = []

    for image in images[:5]:

        if image is None:
            continue

        # Image quality
        quality_results.append(
            analyze_quality(image)
        )

        # Multilingual OCR
        text = extract_text(
            image
        )

        if text:
            all_text.append(
                text
            )

    # -----------------------------------------------------
    # Combine OCR
    # -----------------------------------------------------

    ocr_text = "\n".join(
        all_text
    ).strip()

    # -----------------------------------------------------
    # Classification
    #
    # Uses actual image + OCR.
    # Filename is never passed to classifier.
    # -----------------------------------------------------

    classification = classify_document(
        ocr_text,
        images[0],
    )

    # -----------------------------------------------------
    # Expiry
    # -----------------------------------------------------

    try:

        expiry = check_expiry(
            ocr_text,
            classification[
                "document_type"
            ],
        )

    except Exception:

        expiry = {
            "status": "EXPIRY DATE UNCLEAR",
            "date": None,
        }

    # -----------------------------------------------------
    # Quality score
    # -----------------------------------------------------

    if quality_results:

        quality_score = int(
            round(
                np.mean(
                    [
                        item["score"]
                        for item in quality_results
                    ]
                )
            )
        )

    else:

        quality_score = 0

    # -----------------------------------------------------
    # Quality issues
    # -----------------------------------------------------

    quality_issues = []

    for result in quality_results:

        quality_issues.extend(
            result.get(
                "issues",
                []
            )
        )

    quality_issues = list(
        dict.fromkeys(
            quality_issues
        )
    )

    # -----------------------------------------------------
    # Return complete result
    # -----------------------------------------------------

    return {

        "file_name": path.name,

        "detected_type": (
            classification[
                "document_type"
            ]
        ),

        "confidence": (
            classification[
                "confidence"
            ]
        ),

        "classification_scores": (
            classification.get(
                "scores",
                {}
            )
        ),

        "quality_score": quality_score,

        "quality_issues": quality_issues,

        "ocr_text": ocr_text,

        "fields": classification.get(
            "fields",
            {}
        ),

        "expiry_status": expiry.get(
            "status",
            "EXPIRY DATE UNCLEAR"
        ),

        "expiry_date": expiry.get(
            "date"
        ),

        "duplicate_key": (
            calculate_sha256(path)
        ),

        "error": None,
    }
