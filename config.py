"""
Configuration file for Manus Automation
Adjust these settings as needed
"""

# Google Drive Folder IDs
PENDING_FOLDER_ID = '1VQxl_FC1jVSdwHzDphfcQtIxMvo5CeSI'
PROCESSED_FOLDER_ID = '1v-8MUeGW9irQDeKCYk8PPkINqeBL9Z2Z'
RAW_REPORTS_FOLDER_ID = '1VSoi7t9309t0jyfQrwoZg2hDVgpMMkax'
TRACKING_SHEET_ID = '1tC72KFZJ4mi6o2bb2tEF4SGmFMtDzfcghRjIHa8X-3g'

# Processing Settings
MAX_RETRIES = 3
PROCESSING_TIMEOUT_MINUTES = 10
TEST_MODE = False  # Set to True for testing

# Tracking Sheet Column Mapping
# Adjust these if your sheet has different column letters
COLUMN_MAP = {
    'instruction_id': 'A',
    'status': 'B',
    'manus_started': 'C',
    'manus_completed': 'D',
    'result_doc_id': 'E',
    'result_folder': 'F',
    'cases_found': 'G',
    'processing_time_ms': 'H',
    'error_message': 'I',
    'retry_count': 'J',
    'last_error_time': 'K'
}

# Sheet Tab Name
SHEET_TAB_NAME = 'Manus_Queue'
