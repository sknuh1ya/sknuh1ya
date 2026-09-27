import cv2
import re


# ============================================================
# BASIC KEYWORDS
# ============================================================

KEYWORDS = {
    "Passport": [
        "passport",
        "passport no",
        "passport number",
        "nationality",
        "place of birth",
    ],

    "Emirates ID": [
        "emirates id",
        "emirates identity card",
        "identity card",
        "federal authority",
        "id number",
        "identity number",
        "united arab emirates",
    ],

    "Driving License": [
        "driving license",
        "driving licence",
        "driver license",
        "driver's licence",
    ],

    "Photograph": [],

    "Utility Bill": [
        "electricity",
        "water bill",
        "utility",
        "billing period",
        "meter",
    ],

    "Proof of Address": [
        "proof of address",
        "proof of residence",
        "residential address",
        "residence address",
        "registered address",
        "mailing address",
        "address",
        "residence",
        "residential",
        "building",
        "street",
        "road",
        "district",
        "area",
        "community",
        "villa",
        "apartment",
        "flat",
        "unit",
        "floor",
        "po box",
        "postal",
        "property",
        "tenant",
        "tenancy",
        "lease",
        "rental",
    ],

    "Educational Certificate": [
        "university",
        "college",
        "degree",
        "diploma",
        "graduation",
        "educational",
        "education",
        "certificate",
        "academic",
        "faculty",
        "institute",
        "school",
        "student",
        "course",
        "semester",
        "bachelor",
        "master",
        "phd",
        "doctor of",
        "transcript",
    ],

    "Bank Statement": [
        "bank statement",
        "account number",
        "transaction",
        "balance",
    ],
}


# ============================================================
# GENERAL KEYWORD SCORING
# ============================================================

def keyword_score(text: str, keywords: list[str]) -> float:
    """
    Calculate a simple keyword-based score.

    Returns a value between 0.0 and 1.0.
    """

    if not text:
        return 0.0

    text_lower = text.lower()

    if not keywords:
        return 0.0

    matches = sum(
        1
        for keyword in keywords
        if keyword.lower() in text_lower
    )

    return matches / len(keywords)


# ============================================================
# PASSPORT MRZ DETECTION
# ============================================================

def passport_mrz_score(text: str) -> float:
    """
    Detect a passport using MRZ-style content.

    Handles:
    - Normal P<...
    - Spaced OCR such as P < JPN
    - PP < JPN
    - PP _ JPN
    - Passport field terminology
    """

    if not text:
        return 0.0

    text_upper = text.upper()

    # --------------------------------------------------------
    # Exact / normal MRZ
    # --------------------------------------------------------

    if re.search(r"P<[A-Z<]{3}", text_upper):
        return 1.0

    # --------------------------------------------------------
    # OCR may insert spaces
    # Examples:
    # P < JPN
    # PP < JPN
    # PP _ JPN
    # --------------------------------------------------------

    if re.search(r"P\s*<\s*[A-Z]{3}", text_upper):
        return 0.99

    if re.search(r"PP\s*[_<]\s*[A-Z]{3}", text_upper):
        return 0.98

    if "P<" in text_upper:
        return 0.90

    # --------------------------------------------------------
    # Strong passport field clues
    # --------------------------------------------------------

    passport_clues = [
        "PASSPORT",
        "SURNAME",
        "GIVEN NAME",
        "GIVEN NAMES",
        "NATIONALITY",
        "DATE OF BIRTH",
        "SIGNATURE OF BEARER",
        "PASSPORT NO",
    ]

    matches = sum(
        1
        for clue in passport_clues
        if clue in text_upper
    )

    if matches >= 5:
        return 0.95

    if matches >= 3:
        return 0.85

    if matches >= 2:
        return 0.75

    return 0.0


# ============================================================
# EMIRATES ID DETECTION
# ============================================================

def emirates_id_score(text: str) -> float:
    """
    Detect UAE / Emirates ID.

    Supports:
    - English OCR
    - Arabic OCR
    - UAE identity number format

    UAE identity numbers normally have the 784 prefix and
    consist of 15 digits. OCR may preserve or distort the
    hyphens, so several patterns are supported.
    """

    if not text:
        return 0.0

    normalized = normalize_text(text)

    score = 0.0

    # --------------------------------------------------------
    # UAE ID number
    #
    # Typical:
    # 784-1979-1234567-1
    #
    # Also accept:
    # 784197912345671
    # --------------------------------------------------------

    id_patterns = [
        r"\b784[-\s]?\d{4}[-\s]?\d{7}[-\s]?\d\b",
        r"\b784\d{4}\d{7}\d\b",
    ]

    has_uae_number = False

    for pattern in id_patterns:
        if re.search(pattern, normalized):
            has_uae_number = True
            score = max(score, 0.99)

    # --------------------------------------------------------
    # English terms
    # --------------------------------------------------------

    strong_english = [
        "EMIRATES ID",
        "EMIRATES IDENTITY CARD",
        "UNITED ARAB EMIRATES",
        "IDENTITY CARD",
        "FEDERAL AUTHORITY",
    ]

    medium_english = [
        "ID NUMBER",
        "IDENTITY NUMBER",
        "CARD NUMBER",
        "NATIONALITY",
        "DATE OF BIRTH",
        "EXPIRY DATE",
        "ISSUING DATE",
    ]

    strong_matches = sum(
        1
        for term in strong_english
        if term in normalized
    )

    medium_matches = sum(
        1
        for term in medium_english
        if term in normalized
    )

    if strong_matches >= 3:
        score = max(score, 0.98)

    elif strong_matches >= 2:
        score = max(score, 0.95)

    elif strong_matches == 1:
        score = max(score, 0.85)

    if medium_matches >= 4:
        score = max(score, 0.85)

    elif medium_matches >= 2:
        score = max(score, 0.70)

    # --------------------------------------------------------
    # Arabic Emirates ID terms
    # --------------------------------------------------------

    arabic_terms = [
        "دولة الإمارات العربية المتحدة",
        "دولة الإمارات العربيه المتحدة",
        "الإمارات العربية المتحدة",
        "الإمارات العربيه المتحدة",
        "بطاقة هوية",
        "بطاقة الهوية",
        "رقم الهوية",
        "الهوية",
        "الجنسية",
        "تاريخ الميلاد",
        "تاريخ الانتهاء",
        "تاريخ الإصدار",
    ]

    arabic_matches = sum(
        1
        for term in arabic_terms
        if term in text
    )

    if arabic_matches >= 5:
        score = max(score, 0.98)

    elif arabic_matches >= 3:
        score = max(score, 0.95)

    elif arabic_matches >= 2:
        score = max(score, 0.90)

    elif arabic_matches >= 1:
        score = max(score, 0.75)

    # --------------------------------------------------------
    # Very strong combinations
    # --------------------------------------------------------

    has_identity_word = (
        "بطاقة هوية" in text
        or "بطاقة الهوية" in text
        or "رقم الهوية" in text
        or "IDENTITY CARD" in normalized
        or "EMIRATES ID" in normalized
        or "ID NUMBER" in normalized
        or "IDENTITY NUMBER" in normalized
    )

    has_uae_word = (
        "دولة الإمارات" in text
        or "الإمارات العربية المتحدة" in text
        or "الإمارات العربيه المتحدة" in text
        or "UNITED ARAB EMIRATES" in normalized
    )

    # UAE ID number + identity terminology
    if has_uae_number and has_identity_word:
        score = max(score, 0.99)

    # UAE ID number + UAE terminology
    if has_uae_number and has_uae_word:
        score = max(score, 0.99)

    # Arabic identity + UAE
    if has_identity_word and has_uae_word:
        score = max(score, 0.97)

    return min(score, 0.99)


# ============================================================
# PROOF OF ADDRESS
# ============================================================

def proof_of_address_score(text: str) -> float:
    """
    Detect Proof of Address using address-related terminology.

    Designed to work with OCR from utility bills, tenancy
    documents, residence certificates and similar documents.
    """

    if not text:
        return 0.0

    normalized = normalize_text(text)

    score = 0.0

    # --------------------------------------------------------
    # Very strong explicit phrases
    # --------------------------------------------------------

    explicit_phrases = [
        "PROOF OF ADDRESS",
        "ADDRESS PROOF",
        "PROOF OF RESIDENCE",
        "RESIDENCE PROOF",
        "PROOF OF RESIDENCY",
        "RESIDENCY CERTIFICATE",
        "RESIDENCE CERTIFICATE",
        "ADDRESS CERTIFICATE",
    ]

    for phrase in explicit_phrases:
        if phrase in normalized:
            score = max(score, 0.95)

    # --------------------------------------------------------
    # Address words
    # --------------------------------------------------------

    address_terms = [
        "ADDRESS",
        "RESIDENTIAL",
        "RESIDENCE",
        "REGISTERED ADDRESS",
        "MAILING ADDRESS",
        "HOME ADDRESS",
        "CURRENT ADDRESS",
        "PERMANENT ADDRESS",
        "BUILDING",
        "STREET",
        "ROAD",
        "DISTRICT",
        "AREA",
        "COMMUNITY",
        "VILLA",
        "APARTMENT",
        "FLAT",
        "UNIT",
        "FLOOR",
        "PO BOX",
        "POSTAL",
    ]

    address_matches = sum(
        1
        for term in address_terms
        if term in normalized
    )

    if address_matches >= 6:
        score = max(score, 0.90)

    elif address_matches >= 4:
        score = max(score, 0.80)

    elif address_matches >= 2:
        score = max(score, 0.65)

    # --------------------------------------------------------
    # Property / tenancy clues
    # --------------------------------------------------------

    property_terms = [
        "PROPERTY",
        "TENANT",
        "TENANCY",
        "LEASE",
        "RENTAL",
        "LANDLORD",
        "RESIDENT",
        "RESIDENCY",
    ]

    property_matches = sum(
        1
        for term in property_terms
        if term in normalized
    )

    if property_matches >= 2 and address_matches >= 1:
        score = max(score, 0.85)

    elif property_matches >= 1 and address_matches >= 2:
        score = max(score, 0.75)

    # --------------------------------------------------------
    # Account / customer + address
    # --------------------------------------------------------

    account_terms = [
        "ACCOUNT NUMBER",
        "CUSTOMER NUMBER",
        "CUSTOMER ID",
        "SERVICE ADDRESS",
        "BILLING ADDRESS",
    ]

    account_matches = sum(
        1
        for term in account_terms
        if term in normalized
    )

    if account_matches >= 1 and address_matches >= 2:
        score = max(score, 0.85)

    return min(score, 0.99)


# ============================================================
# UTILITY BILL
# ============================================================

def utility_bill_score(text: str) -> float:
    """
    Detect utility bills separately from general proof of address.
    """

    if not text:
        return 0.0

    normalized = normalize_text(text)

    score = 0.0

    strong_terms = [
        "ELECTRICITY BILL",
        "ELECTRICITY",
        "WATER BILL",
        "UTILITY BILL",
        "UTILITY",
    ]

    medium_terms = [
        "BILLING PERIOD",
        "METER",
        "CONSUMPTION",
        "ACCOUNT NUMBER",
        "DUE DATE",
        "AMOUNT DUE",
        "TOTAL AMOUNT",
    ]

    strong_matches = sum(
        1
        for term in strong_terms
        if term in normalized
    )

    medium_matches = sum(
        1
        for term in medium_terms
        if term in normalized
    )

    if strong_matches >= 2:
        score = max(score, 0.95)

    elif strong_matches == 1:
        score = max(score, 0.80)

    if medium_matches >= 3:
        score = max(score, 0.85)

    elif medium_matches >= 2:
        score = max(score, 0.70)

    return min(score, 0.99)


# ============================================================
# EDUCATIONAL CERTIFICATE
# ============================================================

def educational_certificate_score(text: str) -> float:
    """
    Detect educational certificates, degrees, diplomas,
    transcripts and related academic documents.
    """

    if not text:
        return 0.0

    normalized = normalize_text(text)

    score = 0.0

    strong_terms = [
        "UNIVERSITY",
        "COLLEGE",
        "DEGREE",
        "DIPLOMA",
        "BACHELOR",
        "MASTER",
        "PHD",
        "DOCTOR OF",
        "GRADUATION",
        "TRANSCRIPT",
    ]

    medium_terms = [
        "EDUCATIONAL",
        "EDUCATION",
        "ACADEMIC",
        "FACULTY",
        "INSTITUTE",
        "SCHOOL",
        "STUDENT",
        "COURSE",
        "SEMESTER",
        "CERTIFICATE",
    ]

    strong_matches = sum(
        1
        for term in strong_terms
        if term in normalized
    )

    medium_matches = sum(
        1
        for term in medium_terms
        if term in normalized
    )

    if strong_matches >= 4:
        score = max(score, 0.95)

    elif strong_matches >= 2:
        score = max(score, 0.85)

    elif strong_matches == 1:
        score = max(score, 0.70)

    if medium_matches >= 4:
        score = max(score, 0.80)

    elif medium_matches >= 2:
        score = max(score, 0.65)

    return min(score, 0.99)


# ============================================================
# PHOTOGRAPH DETECTION
# ============================================================

def photograph_score(text: str, image) -> float:
    """
    Detect a photograph using image characteristics.

    OCR is often empty or mostly garbage for photographs,
    so Photograph detection must NOT depend on OCR.

    Uses:
    - portrait-like aspect ratio
    - very little meaningful OCR
    - brightness
    - contrast
    - optional face detection
    """

    if image is None:
        return 0.0

    try:
        height, width = image.shape[:2]

        if height <= 0 or width <= 0:
            return 0.0

        score = 0.0

        # ----------------------------------------------------
        # Portrait aspect ratio
        # ----------------------------------------------------

        ratio = height / width

        if 1.15 <= ratio <= 1.80:
            score += 0.25

        elif 1.05 <= ratio <= 2.00:
            score += 0.10

        # ----------------------------------------------------
        # Very little OCR
        # ----------------------------------------------------

        clean_text = (text or "").strip()

        # Remove our OCR language labels
        clean_text = re.sub(
            r"\[OCR_LANGUAGE=.*?\]",
            "",
            clean_text,
            flags=re.IGNORECASE,
        )

        # Keep only letters/numbers
        meaningful_text = re.sub(
            r"[^A-Za-z0-9]+",
            "",
            clean_text,
        )

        text_length = len(meaningful_text)

        if text_length <= 20:
            score += 0.25

        elif text_length <= 80:
            score += 0.15

        # ----------------------------------------------------
        # Image brightness / contrast
        # ----------------------------------------------------

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        brightness = float(gray.mean())
        contrast = float(gray.std())

        if brightness >= 150:
            score += 0.15

        if contrast >= 20:
            score += 0.15

        # ----------------------------------------------------
        # Optional face detection
        # ----------------------------------------------------

        try:
            if hasattr(cv2, "CascadeClassifier"):

                cascade_path = (
                    cv2.data.haarcascades
                    + "haarcascade_frontalface_default.xml"
                )

                cascade = cv2.CascadeClassifier(
                    cascade_path
                )

                if not cascade.empty():

                    faces = cascade.detectMultiScale(
                        gray,
                        scaleFactor=1.1,
                        minNeighbors=4,
                        minSize=(40, 40),
                    )

                    if len(faces) > 0:
                        score += 0.35

        except Exception:
            # Face detection is optional.
            # Never allow it to break classification.
            pass

        return min(score, 0.99)

    except Exception:
        return 0.0


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text: str) -> str:
    """
    Normalize OCR text for reliable matching.

    Keeps Arabic characters while normalizing English
    matching and whitespace.
    """

    if not text:
        return ""

    text = text.upper()

    # Normalize common whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# MAIN CLASSIFIER
# ============================================================

def classify_document(text: str, image) -> dict:
    """
    Main document classifier.

    The classifier:
    1. Uses general keyword scores.
    2. Applies specialized detectors.
    3. Selects the highest-scoring document type.
    4. Uses a lower threshold for photographs.
    5. Returns classification scores for debugging.
    """

    text = text or ""

    # --------------------------------------------------------
    # General keyword scores
    # --------------------------------------------------------

    scores = {
        name: keyword_score(text, words)
        for name, words in KEYWORDS.items()
    }

    # --------------------------------------------------------
    # Passport
    # --------------------------------------------------------

    mrz_score = passport_mrz_score(text)

    if mrz_score > 0:
        scores["Passport"] = max(
            scores["Passport"],
            mrz_score
        )

    # --------------------------------------------------------
    # Emirates ID
    # --------------------------------------------------------

    scores["Emirates ID"] = max(
        scores["Emirates ID"],
        emirates_id_score(text)
    )

    # --------------------------------------------------------
    # Proof of Address
    # --------------------------------------------------------

    scores["Proof of Address"] = max(
        scores["Proof of Address"],
        proof_of_address_score(text)
    )

    # --------------------------------------------------------
    # Utility Bill
    # --------------------------------------------------------

    scores["Utility Bill"] = max(
        scores["Utility Bill"],
        utility_bill_score(text)
    )

    # --------------------------------------------------------
    # Educational Certificate
    # --------------------------------------------------------

    scores["Educational Certificate"] = max(
        scores["Educational Certificate"],
        educational_certificate_score(text)
    )

    # --------------------------------------------------------
    # Photograph
    # --------------------------------------------------------

    scores["Photograph"] = max(
        scores["Photograph"],
        photograph_score(text, image)
    )

    # --------------------------------------------------------
    # Find highest score
    # --------------------------------------------------------

    best_type = max(
        scores,
        key=scores.get
    )

    best_score = scores[best_type]

    confidence = round(
        min(99, best_score * 100)
    )

    # --------------------------------------------------------
    # Confidence threshold
    #
    # Photograph can be accepted from 50%.
    # Text-based documents require 60%.
    # --------------------------------------------------------

    if best_type == "Photograph":

        if confidence < 50:
            best_type = "Unknown Document"

    else:

        if confidence < 60:
            best_type = "Unknown Document"

    # --------------------------------------------------------
    # Fields
    # --------------------------------------------------------

    fields = {}

    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return {
        "document_type": best_type,
        "confidence": confidence,
        "fields": fields,
        "scores": {
            key: round(value * 100)
            for key, value in scores.items()
        },
    }
