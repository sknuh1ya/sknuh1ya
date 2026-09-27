
from modules.date_checker import check_expiry


def test_expired_date():
    result = check_expiry(
        "Date of Expiry: 01/01/2020",
        "Passport",
    )

    assert result["status"] == "EXPIRED"


def test_future_date():
    result = check_expiry(
        "Date of Expiry: 01/01/2099",
        "Passport",
    )

    assert result["status"] == "VALID"


def test_unclear_date():
    result = check_expiry(
        "Passport document with no readable expiry",
        "Passport",
    )

    assert result["status"] == "EXPIRY DATE UNCLEAR"
