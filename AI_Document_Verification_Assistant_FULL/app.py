from pathlib import Path
import json
import html

import streamlit as st

from modules.document_processor import process_uploaded_file
from modules.application_checker import check_application
from modules.database import init_db, save_application
from modules.utils import make_json_report, make_pdf_report


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Document Verification Assistant",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
REPORT_DIR = DATA_DIR / "reports"
DB_PATH = DATA_DIR / "verification.db"

APPLICATION_TYPES_PATH = DATA_DIR / "application_types.json"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# DATABASE
# ============================================================

try:
    init_db(DB_PATH)
except TypeError:
    try:
        init_db()
    except Exception:
        pass
except Exception:
    pass


# ============================================================
# LOAD APPLICATION TYPES
# ============================================================

def load_application_types():

    default_types = {
        "Visa Application": [
            "Passport",
            "Emirates ID",
            "Photograph",
        ],

        "Residency Application": [
            "Passport",
            "Emirates ID",
            "Photograph",
        ],

        "Government Service": [
            "Emirates ID",
            "Photograph",
        ],

        "Employment Application": [
            "Passport",
            "Educational Certificate",
            "Photograph",
        ],

        "Custom Application": [],
    }

    if not APPLICATION_TYPES_PATH.exists():
        return default_types

    try:

        with open(
            APPLICATION_TYPES_PATH,
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        if isinstance(data, dict):

            if "applications" in data:
                data = data["applications"]

            if isinstance(data, dict):
                return data

    except Exception:
        pass

    return default_types


APPLICATION_TYPES = load_application_types()


# ============================================================
# HTML ESCAPE
# ============================================================

def safe_html(value):

    return html.escape(
        str(value)
    )


# ============================================================
# CUSTOM CSS
#
# IMPORTANT:
# We use st.html() for HTML blocks.
# This prevents the <div> tags from appearing as code.
# ============================================================

st.html(
    """
    <style>

    /* ------------------------------
       MAIN PAGE
    ------------------------------ */

    .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    /* ------------------------------
       HIDE STREAMLIT DEFAULT ELEMENTS
    ------------------------------ */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    /* ------------------------------
       PAGE BACKGROUND
    ------------------------------ */

    .app-background {
        background: #f5f7fb;
        padding: 0;
        margin: 0;
    }

    /* ------------------------------
       HERO
    ------------------------------ */

    .hero {
        background:
            linear-gradient(
                135deg,
                #173b8f 0%,
                #2563c7 55%,
                #4f83dc 100%
            );

        border-radius: 24px;

        padding: 34px 38px;

        margin-bottom: 28px;

        color: white;

        box-shadow:
            0 12px 35px rgba(24, 60, 130, 0.18);
    }

    .hero-icon {
        font-size: 2.2rem;
        margin-bottom: 8px;
    }

    .hero-title {
        font-size: 2.25rem;
        font-weight: 800;
        letter-spacing: -0.7px;
        margin-bottom: 8px;
        color: white;
    }

    .hero-subtitle {
        font-size: 1rem;
        line-height: 1.65;
        max-width: 820px;
        color: #e8f0ff;
        margin-bottom: 20px;
    }

    .hero-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }

    .hero-badge {
        display: inline-block;
        padding: 7px 12px;
        border-radius: 999px;
        background: rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.24);
        color: white;
        font-size: 0.78rem;
        font-weight: 650;
    }

    /* ------------------------------
       SECTION
    ------------------------------ */

    .section-title {
        font-size: 1.35rem;
        font-weight: 750;
        color: #ccebff;
        margin-top: 26px;
        margin-bottom: 4px;
    }

    .section-subtitle {
        font-size: 0.9rem;
        color: #d1d1e0;
        margin-bottom: 14px;
    }

    /* ------------------------------
       CARDS
    ------------------------------ */

    .card {
        background: white;
        border: 1px solid #e1e7ef;
        border-radius: 18px;
        padding: 20px;
        box-shadow:
            0 5px 20px rgba(25, 40, 65, 0.045);
        margin-bottom: 16px;
    }

    .card-title {
        font-size: 1rem;
        font-weight: 750;
        color: #172033;
        margin-bottom: 12px;
    }

    /* ------------------------------
       REQUIRED DOCUMENT
    ------------------------------ */

    .required-document {
        display: flex;
        align-items: center;
        gap: 12px;

        padding: 12px 4px;

        border-bottom: 1px solid #edf0f5;
    }

    .required-document:last-child {
        border-bottom: none;
    }

    .document-icon {
        width: 40px;
        height: 40px;

        border-radius: 11px;

        background: #eef4ff;

        display: flex;
        align-items: center;
        justify-content: center;

        font-size: 1.1rem;
    }

    .document-name {
        font-size: 0.9rem;
        font-weight: 700;
        color: #253149;
    }

    .document-description {
        font-size: 0.73rem;
        color: #8792a3;
        margin-top: 2px;
    }

    /* ------------------------------
       SCREENING CHECKS
    ------------------------------ */

    .check-row {
        display: flex;
        align-items: center;
        gap: 9px;
        padding: 6px 0;

        font-size: 0.84rem;
        color: #526075;
    }

    .check-icon {
        color: #198754;
        font-weight: 800;
    }

    /* ------------------------------
       UPLOAD INFO
    ------------------------------ */

    .upload-info {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;

        margin-top: 10px;
    }

    .file-type-badge {
        background: #f1f4f9;
        color: #5f6d80;

        padding: 6px 10px;

        border-radius: 8px;

        font-size: 0.74rem;
        font-weight: 650;
    }

    /* ------------------------------
       FILE CARD
    ------------------------------ */

    .file-card {
        display: flex;
        align-items: center;
        gap: 12px;

        padding: 12px 14px;

        background: white;

        border: 1px solid #e4e8ef;

        border-radius: 12px;

        margin-top: 8px;
    }

    .file-card-icon {
        width: 38px;
        height: 38px;

        border-radius: 10px;

        background: #f0f4fa;

        display: flex;
        align-items: center;
        justify-content: center;
    }

    .file-card-name {
        font-weight: 650;
        font-size: 0.85rem;
        color: #29354a;
    }

    .file-card-size {
        font-size: 0.72rem;
        color: #8993a3;
        margin-top: 2px;
    }

    /* ------------------------------
       METRICS
    ------------------------------ */

    .metric-card {
        background: white;

        border: 1px solid #e2e7ee;

        border-radius: 16px;

        padding: 18px;

        min-height: 110px;

        box-shadow:
            0 4px 16px rgba(25, 40, 65, 0.04);
    }

    .metric-label {
        color: #7b8798;
        font-size: 0.75rem;
        font-weight: 650;
        margin-bottom: 6px;
    }

    .metric-value {
        color: #182338;
        font-size: 1.65rem;
        font-weight: 800;
    }

    .metric-description {
        color: #8b95a5;
        font-size: 0.7rem;
        margin-top: 3px;
    }

    /* ------------------------------
       DOCUMENT RESULT
    ------------------------------ */

    .result-card {
        background: white;

        border: 1px solid #e1e7ef;

        border-radius: 17px;

        padding: 18px;

        margin-top: 12px;

        box-shadow:
            0 4px 16px rgba(25, 40, 65, 0.035);
    }

    .result-name {
        color: #182338;
        font-size: 0.95rem;
        font-weight: 750;
    }

    .result-type {
        color: #6d798c;
        font-size: 0.78rem;
        margin-top: 4px;
    }

    /* ------------------------------
       BADGES
    ------------------------------ */

    .badge {
        display: inline-block;

        padding: 6px 10px;

        border-radius: 999px;

        font-size: 0.72rem;

        font-weight: 750;
    }

    .badge-success {
        background: #e8f7ef;
        color: #187744;
    }

    .badge-warning {
        background: #fff4d9;
        color: #926500;
    }

    .badge-danger {
        background: #fdeaea;
        color: #a32929;
    }

    .badge-neutral {
        background: #edf1f6;
        color: #5e6b7d;
    }

    /* ------------------------------
       DISCLAIMER
    ------------------------------ */

    .disclaimer {
        background: #f1f4f8;

        border: 1px solid #dfe4eb;

        border-radius: 14px;

        padding: 16px 18px;

        margin-top: 30px;

        color: #667286;

        font-size: 0.76rem;

        line-height: 1.6;
    }

    </style>
    """
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_required_documents(application_type):

    value = APPLICATION_TYPES.get(
        application_type,
        []
    )

    if isinstance(value, dict):

        for key in [
            "required_documents",
            "required",
            "documents",
            "Required Documents",
        ]:

            if key in value:
                value = value[key]
                break

    if isinstance(value, list):
        return value

    if isinstance(value, str):
        return [value]

    return []


def save_uploaded_file(uploaded_file):

    filename = Path(
        uploaded_file.name
    ).name

    destination = UPLOAD_DIR / filename

    counter = 1

    while destination.exists():

        destination = (
            UPLOAD_DIR
            / (
                f"{Path(filename).stem}_"
                f"{counter}"
                f"{Path(filename).suffix}"
            )
        )

        counter += 1

    with open(
        destination,
        "wb"
    ) as output:

        output.write(
            uploaded_file.getbuffer()
        )

    return destination


def get_detected_type(result):

    return (
        result.get("detected_type")
        or result.get("document_type")
        or "Unknown Document"
    )


def get_confidence(result):

    try:
        return int(
            result.get(
                "confidence",
                0
            )
        )
    except Exception:
        return 0


def get_quality(result):

    try:
        return int(
            result.get(
                "quality_score",
                0
            )
        )
    except Exception:
        return 0


def get_ocr_text(result):

    return (
        result.get("ocr_text")
        or result.get("ocr")
        or ""
    )


def badge_html(status):

    status_text = str(
        status or "Unknown"
    )

    normalized = status_text.lower()

    if any(
        x in normalized
        for x in [
            "present",
            "complete",
            "detected",
            "valid",
            "pass",
            "yes",
            "found",
        ]
    ):

        css = "badge-success"

    elif any(
        x in normalized
        for x in [
            "missing",
            "expired",
            "error",
            "failed",
            "wrong",
        ]
    ):

        css = "badge-danger"

    elif any(
        x in normalized
        for x in [
            "review",
            "attention",
            "warning",
            "low",
        ]
    ):

        css = "badge-warning"

    else:

        css = "badge-neutral"

    return (
        f'<span class="badge {css}">'
        f'{safe_html(status_text)}'
        f'</span>'
    )


def metric_card(
    label,
    value,
    description
):

    st.html(
        f"""
        <div class="metric-card">

            <div class="metric-label">
                {safe_html(label)}
            </div>

            <div class="metric-value">
                {safe_html(value)}
            </div>

            <div class="metric-description">
                {safe_html(description)}
            </div>

        </div>
        """
    )


def get_checklist(report):

    if not isinstance(
        report,
        dict
    ):
        return []

    return (
        report.get("checklist")
        or report.get("Checklist")
        or []
    )


def get_actions(report):

    if not isinstance(
        report,
        dict
    ):
        return []

    actions = (
        report.get("actions")
        or report.get(
            "recommended_actions"
        )
        or report.get("Actions")
        or []
    )

    if isinstance(
        actions,
        str
    ):
        return [actions]

    return actions


def get_overall_status(report):

    if isinstance(
        report,
        dict
    ):

        for key in [
            "overall_status",
            "status",
            "Overall Status",
        ]:

            if key in report:
                return report[key]

    checklist = get_checklist(
        report
    )

    statuses = []

    for item in checklist:

        if isinstance(
            item,
            dict
        ):

            status = (
                item.get("Status")
                or item.get("status")
                or ""
            )

            statuses.append(
                str(status).lower()
            )

    if any(
        "missing" in x
        for x in statuses
    ):
        return "Needs Attention"

    if any(
        "review" in x
        for x in statuses
    ):
        return "Needs Human Review"

    if any(
        "expired" in x
        for x in statuses
    ):
        return "Needs Attention"

    return "Screening Complete"


# ============================================================
# HERO
# ============================================================

st.html(
    """
    <div class="hero">

        <div class="hero-icon">
            📄
        </div>

        <div class="hero-title">
            AI Document Verification Assistant
        </div>

        <div class="hero-subtitle">
            Smart preliminary document screening for
            application workflows. Upload your documents
            and review document type, quality, expiry and
            application requirements.
        </div>

        <div class="hero-badges">

            <span class="hero-badge">
                🔒 Local screening
            </span>

            <span class="hero-badge">
                🌐 Multilingual OCR
            </span>

            <span class="hero-badge">
                📋 Application checklist
            </span>

        </div>

        <div style="
            margin-top:20px;
            padding:13px 16px;
            border-radius:12px;
            background:rgba(0,0,0,0.14);
            border:1px solid rgba(255,255,255,0.16);
            color:#eef4ff;
            font-size:0.76rem;
            line-height:1.55;
        ">

            <strong style="color:white;">
                ⚠️ Preliminary screening only
            </strong>
            <br>

            This tool can help identify document type,
            OCR text, image quality, expiry information
            and application requirements. It cannot prove
            that a document is authentic or fake and should
            not replace official verification or human review.
            It is strictly advised to not upload real documents,
            please upload sample documents.

        </div>

    </div>
    """
)


# ============================================================
# APPLICATION
# ============================================================

st.html(
    """
    <div class="section-title">
        Application
    </div>

    <div class="section-subtitle">
        Select the type of application you want to screen.
    </div>
    """
)


application_type = st.selectbox(
    "Application type",
    options=list(
        APPLICATION_TYPES.keys()
    ),
    label_visibility="collapsed",
)


required_documents = get_required_documents(
    application_type
)


# ============================================================
# APPLICATION INFORMATION
# ============================================================

left_column, right_column = st.columns(
    [1.5, 1],
    gap="large",
)


# ------------------------------------------------------------
# REQUIRED DOCUMENTS
# ------------------------------------------------------------

with left_column:

    required_html = ""

    if required_documents:

        for document in required_documents:

            required_html += f"""
            <div class="required-document">

                <div class="document-icon">
                    📄
                </div>

                <div>

                    <div class="document-name">
                        {safe_html(document)}
                    </div>

                    <div class="document-description">
                        Required for this application
                    </div>

                </div>

            </div>
            """

    else:

        required_html = """
        <div style="
            color:#788497;
            font-size:0.84rem;
            padding:10px 0;
        ">
            No predefined documents.
            Upload documents to screen them.
        </div>
        """

    st.html(
        f"""
        <div class="card">

            <div class="card-title">
                📋 Required documents
            </div>

            {required_html}

        </div>
        """
    )


# ------------------------------------------------------------
# SCREENING CHECKS
# ------------------------------------------------------------

with right_column:

    st.html(
        """
        <div class="card">

            <div class="card-title">
                🔍 Screening checks
            </div>

            <div class="check-row">
                <span class="check-icon">✓</span>
                Document type detection
            </div>

            <div class="check-row">
                <span class="check-icon">✓</span>
                Multilingual OCR
            </div>

            <div class="check-row">
                <span class="check-icon">✓</span>
                Image quality screening
            </div>

            <div class="check-row">
                <span class="check-icon">✓</span>
                Expiry-date screening
            </div>

            <div class="check-row">
                <span class="check-icon">✓</span>
                Duplicate detection
            </div>

            <div class="check-row">
                <span class="check-icon">✓</span>
                Missing-document detection
            </div>

        </div>
        """
    )


# ============================================================
# UPLOAD
# ============================================================

st.html(
    """
    <div class="section-title">
        Upload documents
    </div>

    <div class="section-subtitle">
        Upload JPG, JPEG, PNG or PDF files.
        Multiple documents can be selected at once.
    </div>
    """
)


uploaded_files = st.file_uploader(
    "Choose documents",
    type=[
        "jpg",
        "jpeg",
        "png",
        "pdf",
    ],
    accept_multiple_files=True,
    label_visibility="collapsed",
)


# ============================================================
# SELECTED FILES
# ============================================================

if uploaded_files:

    file_html = ""

    for uploaded_file in uploaded_files:

        extension = (
            Path(
                uploaded_file.name
            ).suffix
            .lower()
        )

        size_kb = (
            len(
                uploaded_file.getbuffer()
            ) / 1024
        )

        if extension == ".pdf":
            icon = "📕"
        else:
            icon = "🖼️"

        file_html += f"""
        <div class="file-card">

            <div class="file-card-icon">
                {icon}
            </div>

            <div>

                <div class="file-card-name">
                    {safe_html(uploaded_file.name)}
                </div>

                <div class="file-card-size">
                    {extension.upper().replace(".", "")}
                    · {size_kb:.1f} KB
                </div>

            </div>

        </div>
        """

    st.html(
        f"""
        <div style="margin-top:12px;">

            <div style="
                font-size:1.15rem;
                font-weight:750;
                color:#ccebff;
                margin-bottom:12px;
            ">
                📎 {len(uploaded_files)}
                document(s) selected
            </div>

            {file_html}

        </div>
        """
    )


# ============================================================
# ANALYZE BUTTON
# ============================================================

st.write("")

analyze_clicked = st.button(
    "🔎  Analyze Documents",
    type="primary",
    width="stretch",
    disabled=not bool(
        uploaded_files
    ),
)


# ============================================================
# ANALYSIS
# ============================================================

if (
    analyze_clicked
    and uploaded_files
):

    results = []

    total_files = len(uploaded_files)

    # --------------------------------------------------------
    # LOADING / ANALYSIS STATUS
    # --------------------------------------------------------

    with st.status(
        "🔄 Starting document analysis...",
        expanded=True,
    ) as analysis_status:

        st.write(
            "Preparing the uploaded documents..."
        )

        progress = st.progress(
            0,
            text="Preparing analysis..."
        )

        # ----------------------------------------------------
        # ANALYZE EACH DOCUMENT
        # ----------------------------------------------------

        for index, uploaded_file in enumerate(
            uploaded_files,
            start=1,
        ):

            current_percent = int(
                ((index - 1) / total_files) * 100
            )

            progress.progress(
                current_percent,
                text=(
                    f"📄 Preparing document "
                    f"{index} of {total_files}: "
                    f"{uploaded_file.name}"
                ),
            )

            st.write(
                f"🔎 **Analyzing:** "
                f"`{uploaded_file.name}`"
            )

            try:

                # --------------------------------------------
                # SAVE FILE
                # --------------------------------------------

                file_path = save_uploaded_file(
                    uploaded_file
                )

                # --------------------------------------------
                # OCR + CLASSIFICATION + QUALITY + EXPIRY
                # --------------------------------------------

                result = process_uploaded_file(
                    file_path
                )

                results.append(
                    result
                )

                detected_type = (
                    result.get(
                        "detected_type",
                        "Unknown Document",
                    )
                )

                confidence = (
                    result.get(
                        "confidence",
                        0,
                    )
                )

                st.write(
                    f"✓ Detected: "
                    f"**{detected_type}** "
                    f"({confidence}%)"
                )

            except Exception as exc:

                results.append(
                    {
                        "file_name":
                            uploaded_file.name,

                        "detected_type":
                            "Unknown Document",

                        "confidence": 0,

                        "quality_score": 0,

                        "quality_issues": [],

                        "ocr_text": "",

                        "fields": {},

                        "expiry_status":
                            "Unknown",

                        "expiry_date":
                            None,

                        "duplicate_key":
                            None,

                        "classification_scores":
                            {},

                        "error":
                            str(exc),
                    }
                )

                st.warning(
                    f"⚠️ Could not fully process "
                    f"`{uploaded_file.name}`"
                )

            # --------------------------------------------
            # UPDATE PROGRESS
            # --------------------------------------------

            completed_percent = int(
                (index / total_files) * 100
            )

            progress.progress(
                completed_percent,
                text=(
                    f"Analyzed "
                    f"{index} of {total_files} document(s)"
                ),
            )

        # ----------------------------------------------------
        # APPLICATION CHECK
        # ----------------------------------------------------

        st.write(
            "📋 Checking application requirements..."
        )

        try:

            report = check_application(
                required_documents,
                results,
            )

        except Exception as exc:

            report = {
                "checklist": [],
                "overall_status":
                    "Needs Review",

                "actions": [
                    f"Application checking error: {exc}"
                ],

                "error":
                    str(exc),
            }

        # ----------------------------------------------------
        # DATABASE
        # ----------------------------------------------------

        try:

            try:

                save_application(
                    application_type,
                    results,
                    report,
                    DB_PATH,
                )

            except TypeError:

                save_application(
                    application_type,
                    results,
                    report,
                )

        except Exception:
            pass

        # ----------------------------------------------------
        # FINISH
        # ----------------------------------------------------

        progress.progress(
            100,
            text="Analysis complete ✓",
        )

        analysis_status.update(
            label="✅ Document analysis complete",
            state="complete",
            expanded=False,
        )

    # --------------------------------------------------------
    # SAVE RESULTS
    # --------------------------------------------------------

    st.session_state[
        "results"
    ] = results

    st.session_state[
        "report"
    ] = report

    st.session_state[
        "application_type"
    ] = application_type

    st.rerun()

    # --------------------------------------------------------
    # APPLICATION CHECK
    # --------------------------------------------------------

    try:

        report = check_application(
            required_documents,
            results,
        )

    except Exception as exc:

        report = {
            "checklist": [],
            "overall_status":
                "Needs Review",
            "actions": [
                f"Application checking error: {exc}"
            ],
            "error": str(exc),
        }

    # --------------------------------------------------------
    # DATABASE
    # --------------------------------------------------------

    try:

        try:

            save_application(
                application_type,
                results,
                report,
                DB_PATH,
            )

        except TypeError:

            save_application(
                application_type,
                results,
                report,
            )

    except Exception:
        pass

    # --------------------------------------------------------
    # SAVE IN SESSION
    # --------------------------------------------------------

    st.session_state[
        "results"
    ] = results

    st.session_state[
        "report"
    ] = report

    st.session_state[
        "application_type"
    ] = application_type

    st.rerun()


# ============================================================
# RESULTS
# ============================================================

if (
    "results" in st.session_state
    and "report" in st.session_state
):

    results = st.session_state[
        "results"
    ]

    report = st.session_state[
        "report"
    ]

    current_application_type = (
        st.session_state.get(
            "application_type",
            application_type,
        )
    )

    st.divider()

    st.html(
        """
        <div class="section-title">
            Verification results
        </div>

        <div class="section-subtitle">
            Preliminary screening results for the uploaded
            application documents.
        </div>
        """
    )


    # ========================================================
    # SUMMARY
    # ========================================================

    total_documents = len(
        results
    )

    detected_documents = sum(
        1
        for result in results
        if get_detected_type(result)
        != "Unknown Document"
    )

    unknown_documents = (
        total_documents
        - detected_documents
    )

    good_quality = sum(
        1
        for result in results
        if get_quality(result) >= 60
    )

    processing_errors = sum(
        1
        for result in results
        if result.get("error")
    )


    metric_columns = st.columns(
        4,
        gap="medium",
    )

    with metric_columns[0]:

        metric_card(
            "Documents",
            total_documents,
            "Files analyzed",
        )

    with metric_columns[1]:

        metric_card(
            "Detected",
            detected_documents,
            "Document types identified",
        )

    with metric_columns[2]:

        metric_card(
            "Good quality",
            good_quality,
            "Quality score ≥ 60",
        )

    with metric_columns[3]:

        metric_card(
            "Needs review",
            unknown_documents
            + processing_errors,
            "Unknown or processing issues",
        )


    # ========================================================
    # OVERALL STATUS
    # ========================================================

    overall_status = get_overall_status(
        report
    )

    st.html(
        f"""
        <div class="card" style="
            margin-top:18px;
            display:flex;
            align-items:center;
            justify-content:space-between;
            gap:20px;
            flex-wrap:wrap;
        ">

            <div>

                <div style="
                    color:#8994a5;
                    font-size:0.72rem;
                    font-weight:700;
                    text-transform:uppercase;
                    letter-spacing:0.5px;
                ">
                    Application
                </div>

                <div style="
                    color:#172033;
                    font-size:1.25rem;
                    font-weight:800;
                    margin-top:4px;
                ">
                    {safe_html(
                        current_application_type
                    )}
                </div>

            </div>

            <div>
                {badge_html(overall_status)}
            </div>

        </div>
        """
    )


    # ========================================================
    # DOCUMENT ANALYSIS
    # ========================================================

    st.html(
        """
        <div class="section-title">
            Document analysis
        </div>

        <div class="section-subtitle">
            Review the detected document type, confidence,
            quality and expiry information.
        </div>
        """
    )


    for index, result in enumerate(
        results,
        start=1,
    ):

        file_name = result.get(
            "file_name",
            f"Document {index}",
        )

        detected_type = (
            get_detected_type(
                result
            )
        )

        confidence = (
            get_confidence(
                result
            )
        )

        quality = (
            get_quality(
                result
            )
        )

        expiry_status = result.get(
            "expiry_status",
            "Unknown",
        )

        error = result.get(
            "error"
        )

        if error:
            status = "Needs Review"

        elif detected_type == "Unknown Document":
            status = "Needs Review"

        elif confidence < 60:
            status = "Needs Review"

        else:
            status = "Detected"


        st.html(
            f"""
            <div class="result-card">

                <div style="
                    display:flex;
                    align-items:center;
                    justify-content:space-between;
                    gap:16px;
                    flex-wrap:wrap;
                ">

                    <div>

                        <div class="result-name">
                            📄 {safe_html(file_name)}
                        </div>

                        <div class="result-type">
                            Detected as:
                            <strong>
                                {safe_html(
                                    detected_type
                                )}
                            </strong>
                        </div>

                    </div>

                    <div>
                        {badge_html(status)}
                    </div>

                </div>

            </div>
            """
        )


        # ----------------------------------------------------
        # DOCUMENT METRICS
        # ----------------------------------------------------

        doc_col1, doc_col2, doc_col3 = (
            st.columns(
                3,
                gap="medium",
            )
        )

        with doc_col1:

            metric_card(
                "Detection confidence",
                f"{confidence}%",
                "Content-based classification",
            )

        with doc_col2:

            metric_card(
                "Quality score",
                f"{quality}/100",
                "Image/document quality",
            )

        with doc_col3:

            metric_card(
                "Expiry",
                expiry_status,
                "Date screening result",
            )


        # ----------------------------------------------------
        # QUALITY ISSUES
        # ----------------------------------------------------

        quality_issues = result.get(
            "quality_issues",
            [],
        )

        if quality_issues:

            with st.expander(
                "⚠️ Quality issues"
            ):

                for issue in quality_issues:

                    st.write(
                        f"• {issue}"
                    )


        # ----------------------------------------------------
        # PROCESSING ERROR
        # ----------------------------------------------------

        if error:

            st.error(
                f"Processing error: {error}"
            )


        # ----------------------------------------------------
        # DETAILS
        # ----------------------------------------------------

        with st.expander(
            f"View details — {file_name}"
        ):

            tab1, tab2, tab3 = st.tabs(
                [
                    "📊 Classification",
                    "🔎 OCR text",
                    "📋 Details",
                ]
            )


            # -----------------------------------------------
            # CLASSIFICATION
            # -----------------------------------------------

            with tab1:

                scores = (
                    result.get(
                        "classification_scores",
                        result.get(
                            "scores",
                            {},
                        ),
                    )
                )

                if scores:

                    sorted_scores = sorted(
                        scores.items(),
                        key=lambda x: x[1],
                        reverse=True,
                    )

                    for document_type, score in (
                        sorted_scores
                    ):

                        try:
                            score_int = int(
                                score
                            )
                        except Exception:
                            score_int = 0

                        st.write(
                            f"**{document_type}** "
                            f"— {score_int}%"
                        )

                        st.progress(
                            min(
                                max(
                                    score_int / 100,
                                    0.0,
                                ),
                                1.0,
                            )
                        )

                else:

                    st.info(
                        "No classification scores available."
                    )


            # -----------------------------------------------
            # OCR
            # -----------------------------------------------

            with tab2:

                ocr_text = get_ocr_text(
                    result
                )

                if ocr_text.strip():

                    st.text_area(
                        "Extracted OCR text",
                        value=ocr_text,
                        height=320,
                        key=f"ocr_{index}",
                    )

                else:

                    st.info(
                        "No OCR text was extracted."
                    )


            # -----------------------------------------------
            # DETAILS
            # -----------------------------------------------

            with tab3:

                fields = result.get(
                    "fields",
                    {},
                )

                if fields:

                    st.json(
                        fields
                    )

                else:

                    st.write(
                        "No structured fields were extracted."
                    )

                st.write(
                    "**Expiry date:**",
                    result.get(
                        "expiry_date",
                        "Not detected",
                    ),
                )

                st.write(
                    "**Duplicate key:**",
                    result.get(
                        "duplicate_key",
                        "Not available",
                    ),
                )


    # ========================================================
    # APPLICATION CHECKLIST
    # ========================================================

    st.html(
        """
        <div class="section-title">
            Application checklist
        </div>

        <div class="section-subtitle">
            Required documents compared with the documents
            detected in this submission.
        </div>
        """
    )


    checklist = get_checklist(
        report
    )


    if checklist:

        for item in checklist:

            if not isinstance(
                item,
                dict
            ):
                continue

            required = (
                item.get(
                    "Required Document"
                )
                or item.get(
                    "Document"
                )
                or item.get(
                    "required_document"
                )
                or "Document"
            )

            detected = (
                item.get(
                    "Detected"
                )
                or item.get(
                    "detected"
                )
                or "—"
            )

            status = (
                item.get(
                    "Status"
                )
                or item.get(
                    "status"
                )
                or "Unknown"
            )

            details = (
                item.get(
                    "Details"
                )
                or item.get(
                    "details"
                )
                or ""
            )

            st.html(
                f"""
                <div class="result-card">

                    <div style="
                        display:grid;
                        grid-template-columns:
                        1.4fr 1.4fr 0.8fr;
                        gap:20px;
                        align-items:center;
                    ">

                        <div>

                            <div style="
                                font-size:0.68rem;
                                color:#8994a5;
                                font-weight:700;
                                text-transform:uppercase;
                            ">
                                Required
                            </div>

                            <div style="
                                color:#253149;
                                font-size:0.88rem;
                                font-weight:750;
                                margin-top:4px;
                            ">
                                {safe_html(required)}
                            </div>

                        </div>

                        <div>

                            <div style="
                                font-size:0.68rem;
                                color:#8994a5;
                                font-weight:700;
                                text-transform:uppercase;
                            ">
                                Detected
                            </div>

                            <div style="
                                color:#566378;
                                font-size:0.84rem;
                                font-weight:600;
                                margin-top:4px;
                            ">
                                {safe_html(detected)}
                            </div>

                        </div>

                        <div>
                            {badge_html(status)}
                        </div>

                    </div>

                    {
                        f'''
                        <div style="
                            margin-top:12px;
                            padding-top:12px;
                            border-top:1px solid #edf0f5;
                            color:#6d798b;
                            font-size:0.78rem;
                        ">
                            {safe_html(details)}
                        </div>
                        '''
                        if details
                        else ""
                    }

                </div>
                """
            )

    else:

        st.info(
            "No application checklist was returned."
        )


    # ========================================================
    # RECOMMENDED ACTIONS
    # ========================================================

    actions = get_actions(
        report
    )

    if actions:

        st.html(
            """
            <div class="section-title">
                Recommended actions
            </div>
            """
        )

        for action in actions:

            st.html(
                f"""
                <div class="card"
                     style="
                        padding:12px 16px;
                        margin-bottom:8px;
                     ">

                    <span style="
                        color:#59677b;
                        font-size:0.82rem;
                    ">
                        • {safe_html(action)}
                    </span>

                </div>
                """
            )


    # ========================================================
    # REPORTS
    # ========================================================

    st.html(
        """
        <div class="section-title">
            Reports
        </div>

        <div class="section-subtitle">
            Export the screening results for record keeping.
        </div>
        """
    )


    report_col1, report_col2 = (
        st.columns(
            2,
            gap="medium",
        )
    )


    # --------------------------------------------------------
    # JSON
    # --------------------------------------------------------

    json_path = (
        REPORT_DIR
        / "verification_report.json"
    )

    try:

        make_json_report(
            report,
            json_path,
        )

        if json_path.exists():

            with open(
                json_path,
                "rb",
            ) as file:

                json_bytes = file.read()

            with report_col1:

                st.download_button(
                    "⬇️  Download JSON report",
                    data=json_bytes,
                    file_name=(
                        "verification_report.json"
                    ),
                    mime="application/json",
                    width="stretch",
                )

    except Exception as exc:

        with report_col1:

            st.warning(
                f"JSON report unavailable: {exc}"
            )


    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    pdf_path = (
        REPORT_DIR
        / "verification_report.pdf"
    )

    try:

        make_pdf_report(
            report,
            pdf_path,
        )

        if pdf_path.exists():

            with open(
                pdf_path,
                "rb",
            ) as file:

                pdf_bytes = file.read()

            with report_col2:

                st.download_button(
                    "⬇️  Download PDF report",
                    data=pdf_bytes,
                    file_name=(
                        "verification_report.pdf"
                    ),
                    mime="application/pdf",
                    width="stretch",
                )

    except Exception as exc:

        with report_col2:

            st.warning(
                f"PDF report unavailable: {exc}"
            )


# ============================================================
# DEVELOPER DIAGNOSTICS
# ============================================================

if (
    "results" in st.session_state
    and st.session_state["results"]
):

    with st.expander(
        "🛠️ Developer diagnostics"
    ):

        st.caption(
            "Useful during testing. "
            "This section can be removed before final deployment."
        )

        for result in st.session_state[
            "results"
        ]:

            st.write(
                "DEBUG —",
                result.get(
                    "file_name"
                ),
                "→ detected_type=",
                repr(
                    get_detected_type(
                        result
                    )
                ),
                ", confidence=",
                f"{get_confidence(result)}%",
            )

            st.write(
                "DEBUG KEYS —",
                list(
                    result.keys()
                ),
            )

            ocr_preview = (
                get_ocr_text(
                    result
                )
            )

            st.write(
                "DEBUG OCR —",
                repr(
                    ocr_preview[:3000]
                ),
            )

            st.write(
                "DEBUG ERROR —",
                result.get(
                    "error"
                ),
            )

            st.divider()


# ============================================================
# DISCLAIMER
# ============================================================

st.html(
    """
    <div class="disclaimer">

        <strong>Important:</strong>
        This application performs preliminary document
        screening only. OCR and automated checks can contain
        errors and cannot prove that a document is authentic
        or fake. Results should not replace official
        verification, document authorities, or human review.

    </div>
    """
)
