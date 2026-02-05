import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# --- Configuration ---
# Path to your service account key file. 
# Make sure this file is in the project root and NOT committed to version control if you use git.
CREDENTIALS_FILE = 'credentials.json'
SHEET_NAME = 'Codex Codes'  # The name of your Google Sheet

def get_sheet_connection():
    """Establishes connection to Google Sheets."""
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ]
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).sheet1  # Assuming data is in the first sheet
        return sheet
    except Exception as e:
        print(f"Error connecting to Google Sheet: {e}")
        return None

def normalize_name(name):
    """Normalizes the name to uppercase and stripped of whitespace."""
    if not name:
        return ""
    return name.strip().upper()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/claim', methods=['POST'])
def claim_code():
    data = request.json
    input_name = data.get('name')
    
    if not input_name:
        return jsonify({'status': 'error', 'message': 'Name is required.'}), 400

    sheet = get_sheet_connection()
    if not sheet:
        return jsonify({'status': 'error', 'message': 'Server error: Could not connect to database.'}), 500

    normalized_input_name = normalize_name(input_name)
    
    try:
        # Fetch all records to search
        # Note: For very large sheets, this might be slow, but for a club member list (~100s-1000s) it's fine.
        records = sheet.get_all_records()
        
        # We need to find the row index (1-based for gspread updates)
        # We'll use get_all_records which returns list of dicts.
        # However, to update, we need the row number. 
        # So maybe reading cell by cell or using find method is better?
        # gspread 'find' method is good for this.
        
        # Searching in the 'normalized_name' column (Column E -> 5 in 1-based index if A=1)
        # But 'find' searches the whole sheet or range.
        
        # Optimization: Fetch column E to search locally, then find row index.
        # But gspread find is easier to implement first.
        
        cell = sheet.find(normalized_input_name, in_column=5) # Column E is index 5
        
        if not cell:
             return jsonify({'status': 'not_found', 'message': 'No matching member found.'})
        
        row_idx = cell.row
        
        # Check 'taken' status (Column C -> 3)
        taken_val = sheet.cell(row_idx, 3).value  # Get status of 'taken'
        
        # Convert to boolean logic. Excel/Sheets 'TRUE' string usually
        is_taken = str(taken_val).strip().upper() == "TRUE"
        
        if is_taken:
            return jsonify({'status': 'claimed', 'message': 'Your code has already been claimed.'})
        
        # Not taken, return hash (Column B -> 2) and mark as taken
        hash_code = sheet.cell(row_idx, 2).value
        
        # Update 'taken' column to TRUE
        sheet.update_cell(row_idx, 3, "TRUE")
        
        return jsonify({'status': 'success', 'code': hash_code})

    except Exception as e:
        print(f"Error processing claim: {e}")
        return jsonify({'status': 'error', 'message': 'An unexpected error occurred.'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)