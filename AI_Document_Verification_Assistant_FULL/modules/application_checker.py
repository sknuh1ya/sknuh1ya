from collections import defaultdict


# ---------------------------------------------------------
# Normalization
# ---------------------------------------------------------

def normalize_document_type(value: str) -> str:

    if not value:
        return ""

    value = value.lower().strip()

    aliases = {

        # Passport
        "passport": "Passport",

        # Emirates ID
        "emirates id": "Emirates ID",
        "emirates identity card": "Emirates ID",
        "uae identity card": "Emirates ID",
        "identity card": "Emirates ID",

        # Photograph
        "photo": "Photograph",
        "photograph": "Photograph",
        "personal photo": "Photograph",
        "personal photograph": "Photograph",

        # Address
        "proof of address": "Proof of Address",
        "address proof": "Proof of Address",
        "residential address": "Proof of Address",
        "proof of residence": "Proof of Address",

        # Education
        "educational certificate": (
            "Educational Certificate"
        ),
        "education certificate": (
            "Educational Certificate"
        ),
        "degree certificate": (
            "Educational Certificate"
        ),
        "academic certificate": (
            "Educational Certificate"
        ),
        "diploma": (
            "Educational Certificate"
        ),

        # Utility
        "utility bill": "Utility Bill",
        "water bill": "Utility Bill",
        "electricity bill": "Utility Bill",

        # Driving
        "driving licence": "Driving License",
        "driving license": "Driving License",

        # Bank
        "bank statement": "Bank Statement",
    }

    return aliases.get(
        value,
        value.title()
    )


# ---------------------------------------------------------
# Required-document matching
# ---------------------------------------------------------

def check_application(
    required_documents,
    documents,
):
    """
    Compare detected documents with the documents
    required by the selected application type.

    This is preliminary screening only.
    """

    # -----------------------------------------------------
    # Normalize requirements
    # -----------------------------------------------------

    required = [
        normalize_document_type(
            document
        )
        for document in required_documents
    ]

    # -----------------------------------------------------
    # Normalize detected documents
    # -----------------------------------------------------

    detected = []

    for document in documents:

        detected_type = normalize_document_type(
            document.get(
                "detected_type",
                ""
            )
        )

        detected.append(
            {
                "document": document,
                "type": detected_type,
            }
        )

    # -----------------------------------------------------
    # Track duplicate document types
    # -----------------------------------------------------

    type_groups = defaultdict(list)

    for item in detected:

        if item["type"]:
            type_groups[
                item["type"]
            ].append(
                item["document"]
            )

    # -----------------------------------------------------
    # Checklist
    # -----------------------------------------------------

    checklist = []

    for required_type in required:

        matching = type_groups.get(
            required_type,
            []
        )

        if not matching:

            checklist.append(
                {
                    "Required Document": (
                        required_type
                    ),
                    "Detected": "No",
                    "Status": "Missing",
                    "Details": (
                        "No matching document detected."
                    ),
                }
            )

            continue

        # Use the strongest matching document
        best_document = max(
            matching,
            key=lambda item: item.get(
                "confidence",
                0
            )
        )

        confidence = best_document.get(
            "confidence",
            0
        )

        quality = best_document.get(
            "quality_score",
            0
        )

        expiry_status = best_document.get(
            "expiry_status",
            ""
        )

        issues = best_document.get(
            "quality_issues",
            []
        )

        # -------------------------------------------------
        # Unknown / human review
        # -------------------------------------------------

        if (
            best_document.get(
                "detected_type"
            ) == "Unknown Document"
        ):

            status = "Human Review"

            details = (
                "Document could not be "
                "classified reliably."
            )

        # -------------------------------------------------
        # Low classification confidence
        # -------------------------------------------------

        elif confidence < 60:

            status = "Human Review"

            details = (
                "Classification confidence "
                "is below the screening threshold."
            )

        # -------------------------------------------------
        # Poor image quality
        # -------------------------------------------------

        elif quality < 50:

            status = "Reupload Required"

            details = (
                "Image quality is too low "
                "for reliable preliminary screening."
            )

        # -------------------------------------------------
        # Expired document
        # -------------------------------------------------

        elif (
            expiry_status
            in {
                "EXPIRED",
                "EXPIRED DOCUMENT",
            }
        ):

            status = "Expired"

            details = (
                "Document appears to be expired."
            )

        # -------------------------------------------------
        # Quality issues
        # -------------------------------------------------

        elif issues:

            status = "Needs Correction"

            details = "; ".join(
                issues
            )

        # -------------------------------------------------
        # Good preliminary match
        # -------------------------------------------------

        else:

            status = "Present"

            details = (
                "Matching document detected."
            )

        checklist.append(
            {
                "Required Document": (
                    required_type
                ),
                "Detected": "Yes",
                "Status": status,
                "Details": details,
            }
        )

    # -----------------------------------------------------
    # Extra uploaded documents
    # -----------------------------------------------------

    required_set = set(
        required
    )

    extra_documents = []

    for item in detected:

        if item["type"] not in required_set:

            extra_documents.append(
                item["document"]
            )

    # -----------------------------------------------------
    # Overall status
    # -----------------------------------------------------

    statuses = [
        item["Status"]
        for item in checklist
    ]

    if any(
        status == "Missing"
        for status in statuses
    ):

        overall_status = "INCOMPLETE"

    elif any(
        status == "Expired"
        for status in statuses
    ):

        overall_status = (
            "EXPIRED DOCUMENT"
        )

    elif any(
        status == "Reupload Required"
        for status in statuses
    ):

        overall_status = (
            "REUPLOAD REQUIRED"
        )

    elif any(
        status == "Needs Correction"
        for status in statuses
    ):

        overall_status = (
            "NEEDS CORRECTION"
        )

    elif any(
        status == "Human Review"
        for status in statuses
    ):

        overall_status = (
            "HUMAN REVIEW REQUIRED"
        )

    else:

        overall_status = "COMPLETE"

    # -----------------------------------------------------
    # Actions
    # -----------------------------------------------------

    actions = []

    for item in checklist:

        if item["Status"] == "Missing":

            actions.append(
                f"Upload the required "
                f"{item['Required Document']}."
            )

        elif item["Status"] == "Reupload Required":

            actions.append(
                f"Re-upload the "
                f"{item['Required Document']} "
                f"with better image quality."
            )

        elif item["Status"] == "Expired":

            actions.append(
                f"Provide a current "
                f"{item['Required Document']}."
            )

        elif item["Status"] == "Needs Correction":

            actions.append(
                f"Review the "
                f"{item['Required Document']} "
                f"because quality issues were detected."
            )

        elif item["Status"] == "Human Review":

            actions.append(
                f"Manually review the "
                f"{item['Required Document']}."
            )

    if not actions:

        actions.append(
            "All required documents passed "
            "preliminary screening. Official "
            "verification is still required."
        )

    # -----------------------------------------------------
    # Return report
    # -----------------------------------------------------

    return {

        "overall_status": overall_status,

        "checklist": checklist,

        "documents": documents,

        "actions": actions,

        "extra_documents": extra_documents,

        "required_documents": required_documents,
    }
