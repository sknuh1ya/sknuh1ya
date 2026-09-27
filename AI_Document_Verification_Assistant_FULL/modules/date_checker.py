
import re
from datetime import datetime

from dateutil import parser


DATE_PATTERNS = [
    r"\b\d{1,2}/\d{1,2}/\d{4}\b",
    r"\b\d{1,2}-\d{1,2}-\d{4}\b",
    r"\b\d{4}-\d{1,2}-\d{1,2}\b",
    r"\b\d{1,2}\.\d{1,2}\.\d{4}\b",
]

EXPIRY_KEYWORDS = [
    "expiry",
    "expiration",
    "valid until",
    "date of expiry",
]


def parse_date(value: str):
    try:
        if re.match(r"^\d{4}-", value):
            return parser.parse(
                value,
                dayfirst=False,
            ).date()

        return parser.parse(
            value,
            dayfirst=True,
        ).date()

    except (ValueError, OverflowError):
        return None


def check_expiry(text: str, document_type: str) -> dict:
    text_lower = text.lower()

    candidates = []

    for pattern in DATE_PATTERNS:
        candidates.extend(
            re.findall(pattern, text)
        )

    if not candidates:
        return {
            "status": "EXPIRY DATE UNCLEAR",
            "date": None,
        }

    selected = None

    # Prefer dates located near an expiry-related keyword.
    for keyword in EXPIRY_KEYWORDS:
        position = text_lower.find(keyword)

        if position >= 0:
            nearby_text = text[
                max(0, position):
                position + 120
            ]

            for pattern in DATE_PATTERNS:
                matches = re.findall(
                    pattern,
                    nearby_text,
                )

                if matches:
                    selected = matches[0]
                    break

        if selected:
            break

    selected = selected or candidates[-1]

    parsed = parse_date(selected)

    if parsed is None:
        return {
            "status": "EXPIRY DATE UNCLEAR",
            "date": None,
        }

    today = datetime.now().date()

    if parsed < today:
        return {
            "status": "EXPIRED",
            "date": parsed.isoformat(),
        }

    return {
        "status": "VALID",
        "date": parsed.isoformat(),
    }
