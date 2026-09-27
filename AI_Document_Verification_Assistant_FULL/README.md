# AI Document Verification Assistant

## 1. What this project does

This is a local Streamlit application for preliminary document screening.

It supports:

- Required-document checking
- Document-type classification
- Local OCR using Tesseract
- Basic image quality checking
- Blur detection
- Brightness and contrast checks
- Expiry-date extraction
- Expiry-date checking
- Missing-document detection
- Wrong-document detection
- Exact duplicate detection using SHA-256
- SQLite application metadata
- JSON reports
- PDF reports
- Human-review fallback

It does NOT prove document authenticity.

---

# 2. Software you need

Install:

1. Python 3.10 or newer
2. Tesseract OCR
3. Git (optional)

---

# 3. Windows setup

Open PowerShell.

Check Python:

```powershell
python --version
```

If that does not work, try:

```powershell
py --version
```

Create the project environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate again:

```powershell
.venv\Scripts\Activate.ps1
```

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

Install project packages:

```powershell
pip install -r requirements.txt
```

---

# 4. Install Tesseract OCR on Windows

Install Tesseract OCR separately.

After installation, open a NEW PowerShell window and run:

```powershell
tesseract --version
```

You should see a Tesseract version.

If Windows says that `tesseract` is not recognized, add the Tesseract installation folder to your PATH.

A common installation directory is:

```text
C:\Program Files\Tesseract-OCR
```

Close and reopen PowerShell after changing PATH.

Then test again:

```powershell
tesseract --version
```

---

# 5. macOS setup

Install Python and Tesseract.

With Homebrew:

```bash
brew install python
brew install tesseract
```

Create the environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Check Tesseract:

```bash
tesseract --version
```

---

# 6. Ubuntu/Debian setup

Install system packages:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip tesseract-ocr
```

Create the environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Check:

```bash
tesseract --version
```

---

# 7. Run the application

From the project root:

```bash
streamlit run app.py
```

Streamlit will display a local URL, normally similar to:

```text
http://localhost:8501
```

Open that address in your browser.

---

# 8. Test the application manually

Use synthetic/sample documents.

Example test:

Required:

```text
Passport
Emirates ID
Photograph
```

Upload only:

```text
passport.jpg
photograph.jpg
```

Expected result:

```text
Passport — Uploaded
Emirates ID — Missing
Photograph — Uploaded

Overall Status:
INCOMPLETE
```

For wrong-document testing, use a synthetic sample containing text such as:

```text
DRIVING LICENSE
```

when the application requires:

```text
Emirates ID
```

The system should report a correction or review condition rather than claiming authenticity.

---

# 9. Run automated tests

Make sure the virtual environment is activated.

Run:

```bash
pytest -q
```

The tests cover:

- Expired dates
- Future dates
- Unclear dates
- Missing documents
- Complete applications
- Wrong documents
- Basic image-quality output

---

# 10. Generate reports

After analysis, the Streamlit interface provides:

```text
Download JSON Report
Download PDF Report
```

The latest files are also written to:

```text
data/reports/
```

---

# 11. SQLite database

The application automatically creates:

```text
data/verification.db
```

The database stores application metadata and status.

Uploaded document contents are not permanently stored by the application.

---

# 12. Troubleshooting

## Error: No module named streamlit

Activate the environment and run:

```bash
pip install -r requirements.txt
```

## Error: TesseractNotFoundError

Check:

```bash
tesseract --version
```

If it fails, install Tesseract or add it to PATH.

## PDF cannot be processed

Reinstall PyMuPDF:

```bash
pip install --upgrade PyMuPDF
```

## OpenCV import error

Try:

```bash
pip install --upgrade opencv-python
```

## Streamlit does not start

Try:

```bash
python -m streamlit run app.py
```

## Tests fail because modules cannot be found

Run pytest from the project root:

```bash
pytest -q
```

Do not run pytest from inside the `tests` folder.

---

# 13. Production warning

This project is suitable as a learning/prototype system.

Before processing real government documents, add:

- Authentication
- Authorization
- Encryption
- Secure temporary storage
- Strict file-size limits
- Malware/file scanning
- Access logging
- Retention/deletion policies
- Secure deployment
- Privacy controls
- Human review workflows
- Security testing

Never treat OCR or keyword classification as proof that a document is genuine.

---

# 14. Architecture

```text
Streamlit UI
     |
     v
File Upload
     |
     v
PDF/Image Processing
     |
     +--> OpenCV Quality Analysis
     |
     +--> Tesseract OCR
     |
     +--> Document Classifier
     |
     +--> Date/Expiry Checker
     |
     +--> Duplicate Checker
     |
     v
Application Checker
     |
     v
Overall Status
     |
     +--> SQLite
     +--> JSON Report
     +--> PDF Report
```
