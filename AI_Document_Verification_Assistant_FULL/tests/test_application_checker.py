
from modules.application_checker import check_application


def make_document(name, document_type):
    return {
        "file_name": name,
        "detected_type": document_type,
        "confidence": 95,
        "quality_score": 90,
        "quality_issues": [],
        "ocr_text": "",
        "fields": {},
        "expiry_status": "NOT APPLICABLE",
        "expiry_date": None,
        "duplicate_key": name,
        "error": None,
    }


def test_missing_document():
    report = check_application(
        ["Passport", "Emirates ID"],
        [make_document("passport.jpg", "Passport")],
    )

    assert report["overall_status"] == "INCOMPLETE"


def test_complete_application():
    report = check_application(
        ["Passport"],
        [make_document("passport.jpg", "Passport")],
    )

    assert report["overall_status"] == "COMPLETE"


def test_wrong_document():
    report = check_application(
        ["Emirates ID"],
        [make_document("license.jpg", "Driving License")],
    )

    assert report["overall_status"] == "NEEDS CORRECTION"
