# Codex Codes - Claim App

A secure Flask web application for Codex Club members to claim their unique access hashes.

## Prerequisites

1.  **Python 3.8+**
2.  **Google Cloud Service Account** with Google Sheets API enabled.

## Setup Instructions

### 1. Google Sheets Setup
1.  Create a Google Sheet named **"Codex Codes"**.
2.  Set up the following columns in the first sheet:
    -   **A**: `names` (Member Name)
    -   **B**: `hashs` (The unique code)
    -   **C**: `taken` (Boolean, set all to `FALSE` initially)
    -   **D**: `emails` (Optional)
    -   **E**: `normalized_name` (Uppercased and trimmed name for lookup, e.g., "JOHN DOE")
3.  **Share the sheet** with the email address of your Service Account (e.g., `my-service-account@project-id.iam.gserviceaccount.com`) as an **Editor**.

### 2. Application Setup
1.  **Clone/Download** this project.
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Credentials**:
    -   Place your Google Service Account JSON key file in the root directory.
    -   Rename it to `credentials.json`.
    -   **IMPORTANT**: Never commit `credentials.json` to public repositories.

### 3. Running the App
Run the Flask server:
```bash
python app.py
```
Visit `http://127.0.0.1:5000` in your browser.

## Deployment
This app can be deployed on Render, Railway, or Heroku.
-   Ensure you add `credentials.json` contents as an environment variable or secure file in your deployment settings.
-   Update `app.py` to read credentials from environment variables if deploying to production (recommended for security).

## Security Note
The Google Sheet is used as a backend database and is never exposed directly to the client. Users can only retrieve their code by providing a valid name.
