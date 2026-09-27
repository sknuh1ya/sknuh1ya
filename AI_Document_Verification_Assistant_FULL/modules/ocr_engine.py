import cv2
import pytesseract


# ============================================================
# OCR SETTINGS
# ============================================================

# All languages installed on your system can still be used.
# Tesseract processes them together instead of running
# completely separate OCR jobs for every language.

PREFERRED_LANGUAGES = [
    "eng",
    "ara",
    "chi_sim",
    "chi_tra",
    "deu",
    "fra",
    "hin",
    "jpn",
    "kor_vert",
    "spa",
]


# ============================================================
# GET AVAILABLE LANGUAGES
# ============================================================

def get_available_languages():

    try:

        languages = pytesseract.get_languages(
            config=""
        )

        # Remove special/non-OCR languages
        languages = [
            lang
            for lang in languages
            if lang not in [
                "osd",
                "equ",
            ]
        ]

        return languages

    except Exception:

        return ["eng"]


# ============================================================
# BUILD MULTILINGUAL LANGUAGE STRING
# ============================================================

def get_ocr_language_string():

    available = get_available_languages()

    selected = [
        lang
        for lang in PREFERRED_LANGUAGES
        if lang in available
    ]

    # Include any additional installed language
    # so the OCR remains multilingual.
    for lang in available:

        if lang not in selected:

            selected.append(lang)

    if not selected:

        return "eng"

    return "+".join(selected)


# ============================================================
# PREPROCESS IMAGE
# ============================================================

def preprocess_image(image):

    if image is None:
        return None

    try:

        height, width = image.shape[:2]

        # Don't upscale very large images.
        # This keeps OCR considerably faster.
        max_width = 1800

        if width > max_width:

            scale = max_width / width

            image = cv2.resize(
                image,
                None,
                fx=scale,
                fy=scale,
                interpolation=cv2.INTER_AREA,
            )

        elif width < 1000:

            scale = 1000 / width

            image = cv2.resize(
                image,
                None,
                fx=scale,
                fy=scale,
                interpolation=cv2.INTER_CUBIC,
            )

        return image

    except Exception:

        return image


# ============================================================
# CLEAN OCR TEXT
# ============================================================

def clean_text(text):

    if not text:
        return ""

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if line:
            lines.append(line)

    return "\n".join(lines)


# ============================================================
# MAIN OCR
# ============================================================

def run_ocr(image):

    if image is None:
        return ""

    try:

        # --------------------------------------------
        # Prepare image ONCE
        # --------------------------------------------

        processed = preprocess_image(
            image
        )

        if processed is None:
            return ""

        languages = get_ocr_language_string()

        results = []

        # --------------------------------------------
        # PASS 1
        #
        # One multilingual OCR call.
        #
        # PSM 6 works well for ID/passport/certificate
        # style documents.
        # --------------------------------------------

        try:

            text = pytesseract.image_to_string(
                processed,
                lang=languages,
                config="--oem 1 --psm 6",
            )

            text = clean_text(text)

            if text:
                results.append(text)

        except Exception:
            pass


        # --------------------------------------------
        # PASS 2
        #
        # Only perform a second OCR pass if the first
        # result is very short.
        #
        # This helps photographs and unusual layouts
        # without making every document slow.
        # --------------------------------------------

        combined_text = "\n".join(
            results
        )

        if len(combined_text.strip()) < 80:

            try:

                text = pytesseract.image_to_string(
                    processed,
                    lang=languages,
                    config="--oem 1 --psm 11",
                )

                text = clean_text(text)

                if text:
                    results.append(text)

            except Exception:
                pass


        # --------------------------------------------
        # FALLBACK
        #
        # If multilingual OCR failed completely,
        # try English once.
        # --------------------------------------------

        if not results:

            try:

                text = pytesseract.image_to_string(
                    processed,
                    lang="eng",
                    config="--oem 1 --psm 6",
                )

                text = clean_text(text)

                if text:
                    results.append(text)

            except Exception:
                pass


        # --------------------------------------------
        # REMOVE DUPLICATE OCR RESULTS
        # --------------------------------------------

        unique_results = []

        for text in results:

            if text and text not in unique_results:

                unique_results.append(text)


        return "\n".join(
            unique_results
        ).strip()


    except Exception:

        return ""


# ============================================================
# COMPATIBILITY FUNCTION
# ============================================================

def extract_text(image):

    return run_ocr(image)
