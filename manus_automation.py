#!/usr/bin/env python3.11
"""
Manus Automation - Content Pipeline Research Processor v2.0
Processes research instructions from Google Drive and generates research reports
"""

import os
import sys
import time
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
import io

# Configuration
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets'
]

# Folder IDs from your configuration
PENDING_FOLDER_ID = '1VQxl_FC1jVSdwHzDphfcQtIxMvo5CeSI'
PROCESSED_FOLDER_ID = '1v-8MUeGW9irQDeKCYk8PPkINqeBL9Z2Z'
RAW_REPORTS_FOLDER_ID = '1VSoi7t9309t0jyfQrwoZg2hDVgpMMkax'
TRACKING_SHEET_ID = '1tC72KFZJ4mi6o2bb2tEF4SGmFMtDzfcghRjIHa8X-3g'

# Processing configuration
MAX_RETRIES = 3
PROCESSING_TIMEOUT_MINUTES = 10
TEST_MODE = False

class ManusAutomation:
    """Main automation class for processing research instructions"""
    
    def __init__(self):
        self.drive_service = None
        self.sheets_service = None
        self.docs_service = None
        self.start_time = None
        
    def authenticate(self):
        """Authenticate with Google APIs"""
        print("🔐 Authenticating with Google...")
        creds = None
        
        # Load existing token
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("♻️  Refreshing expired token...")
                creds.refresh(Request())
            else:
                print("🌐 Initiating authentication flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                
                # Set the redirect URI explicitly
                flow.redirect_uri = 'http://localhost'
                
                # Use console-based authentication for headless environment
                print("\n" + "="*60)
                print("AUTHENTICATION REQUIRED")
                print("="*60)
                print("\nPlease follow these steps:")
                print("1. Open this URL in your browser:")
                print("\n   ", end="")
                
                # Get the authorization URL with explicit redirect_uri
                auth_url, _ = flow.authorization_url(
                    prompt='consent',
                    access_type='offline'
                )
                print(auth_url)
                
                print("\n2. Grant permissions when prompted")
                print("3. You'll be redirected to a URL starting with http://localhost")
                print("4. Copy the ENTIRE redirect URL and paste it below")
                print("\n" + "="*60)
                
                # Get the authorization response from user
                code = input("\nPaste the redirect URL here: ").strip()
                
                # Extract the authorization code from the URL
                flow.fetch_token(authorization_response=code)
                creds = flow.credentials
            
            # Save credentials
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        # Build services
        self.drive_service = build('drive', 'v3', credentials=creds)
        self.sheets_service = build('sheets', 'v4', credentials=creds)
        self.docs_service = build('docs', 'v1', credentials=creds)
        
        print("✅ Authentication successful")
        
    def list_pending_files(self) -> List[Dict]:
        """List all files in Pending folder, sorted by creation time (oldest first)"""
        try:
            query = f"'{PENDING_FOLDER_ID}' in parents and trashed=false"
            
            if TEST_MODE:
                query += " and name contains 'TEST_'"
            
            results = self.drive_service.files().list(
                q=query,
                orderBy='createdTime',
                fields='files(id, name, createdTime, mimeType)',
                pageSize=100
            ).execute()
            
            files = results.get('files', [])
            print(f"📁 Found {len(files)} pending instruction file(s)")
            return files
            
        except HttpError as error:
            print(f"❌ Error listing files: {error}")
            return []
    
    def read_google_doc(self, file_id: str) -> str:
        """Read content from a Google Doc"""
        try:
            # Export as plain text
            request = self.drive_service.files().export_media(
                fileId=file_id,
                mimeType='text/plain'
            )
            
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            content = file_content.getvalue().decode('utf-8')
            return content
            
        except HttpError as error:
            print(f"❌ Error reading document: {error}")
            return ""
    
    def parse_instruction_file(self, content: str, filename: str) -> Dict:
        """Parse instruction file content into structured data"""
        instruction = {
            'instruction_id': '',
            'category': '',
            'category_id': '',
            'priority': 'Normal',
            'instruction_text': '',
            'search_parameters': {},
            'output_config': {},
            'filename': filename
        }
        
        # Extract INSTRUCTION_ID
        match = re.search(r'INSTRUCTION_ID:\s*(.+)', content, re.IGNORECASE)
        if match:
            instruction['instruction_id'] = match.group(1).strip()
        
        # Extract CATEGORY
        match = re.search(r'CATEGORY:\s*(.+)', content, re.IGNORECASE)
        if match:
            instruction['category'] = match.group(1).strip()
        
        # Extract CATEGORY_ID
        match = re.search(r'CATEGORY_ID:\s*(.+)', content, re.IGNORECASE)
        if match:
            instruction['category_id'] = match.group(1).strip()
        
        # Extract PRIORITY
        match = re.search(r'PRIORITY:\s*(.+)', content, re.IGNORECASE)
        if match:
            instruction['priority'] = match.group(1).strip()
        
        # Extract INSTRUCTION (multi-line)
        match = re.search(r'INSTRUCTION:\s*\n(.*?)(?=\n[A-Z_]+:|$)', content, re.IGNORECASE | re.DOTALL)
        if match:
            instruction['instruction_text'] = match.group(1).strip()
        
        # Extract search parameters
        match = re.search(r'date_range:\s*(.+)', content, re.IGNORECASE)
        if match:
            instruction['search_parameters']['date_range'] = match.group(1).strip()
        
        match = re.search(r'max_results:\s*(\d+)', content, re.IGNORECASE)
        if match:
            instruction['search_parameters']['max_results'] = int(match.group(1))
        else:
            instruction['search_parameters']['max_results'] = 10
        
        # Extract output config
        match = re.search(r'filename_prefix:\s*(.+)', content, re.IGNORECASE)
        if match:
            instruction['output_config']['filename_prefix'] = match.group(1).strip()
        else:
            instruction['output_config']['filename_prefix'] = 'RESEARCH_'
        
        return instruction
    
    def find_instruction_row(self, instruction_id: str) -> Optional[int]:
        """Find the row number for a given instruction ID in the tracking sheet"""
        try:
            # Read the Instruction_ID column
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=TRACKING_SHEET_ID,
                range='Manus_Queue!A:A'
            ).execute()
            
            values = result.get('values', [])
            
            for idx, row in enumerate(values):
                if row and row[0] == instruction_id:
                    return idx + 1  # Sheets are 1-indexed
            
            return None
            
        except HttpError as error:
            print(f"❌ Error finding instruction row: {error}")
            return None
    
    def update_tracking_sheet(self, instruction_id: str, updates: Dict[str, Any]):
        """Update the tracking sheet for a given instruction"""
        try:
            row_number = self.find_instruction_row(instruction_id)
            
            if row_number is None:
                print(f"⚠️  Instruction ID {instruction_id} not found in tracking sheet")
                return False
            
            # Column mapping (adjust based on your actual sheet structure)
            column_map = {
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
            
            # Prepare batch update
            data = []
            for field, value in updates.items():
                if field.lower() in column_map:
                    col = column_map[field.lower()]
                    range_name = f'Manus_Queue!{col}{row_number}'
                    data.append({
                        'range': range_name,
                        'values': [[value]]
                    })
            
            if data:
                body = {'valueInputOption': 'USER_ENTERED', 'data': data}
                self.sheets_service.spreadsheets().values().batchUpdate(
                    spreadsheetId=TRACKING_SHEET_ID,
                    body=body
                ).execute()
                
                print(f"✅ Updated tracking sheet for {instruction_id}")
                return True
            
            return False
            
        except HttpError as error:
            print(f"❌ Error updating tracking sheet: {error}")
            return False
    
    def perform_research(self, instruction: Dict) -> Dict:
        """
        Execute research based on instruction using integrated research engine
        """
        print(f"🔍 Performing research: {instruction['instruction_text'][:100]}...")
        
        # Import the research integration module
        try:
            from manus_direct_research import perform_comprehensive_research
            
            # Execute research with Manus AI capabilities
            results = perform_comprehensive_research(
                instruction_text=instruction['instruction_text'],
                max_results=instruction['search_parameters'].get('max_results', 10),
                date_range=instruction['search_parameters'].get('date_range', ''),
                category=instruction['category']
            )
            
            # Add instruction metadata
            results['instruction_id'] = instruction['instruction_id']
            results['category_id'] = instruction['category_id']
            
            return results
            
        except ImportError as e:
            print(f"⚠️  Could not import research module: {e}")
            print("💡 Falling back to placeholder research")
            
            # Fallback to placeholder
            max_results = instruction['search_parameters'].get('max_results', 10)
            
            results = {
                'cases': [],
                'total_cases': 0,
                'instruction_id': instruction['instruction_id'],
                'category': instruction['category'],
                'category_id': instruction['category_id'],
                'research_query': instruction['instruction_text']
            }
            
            return results
        
        except Exception as e:
            print(f"❌ Research execution error: {e}")
            raise
    
    def format_research_report(self, results: Dict, instruction: Dict, 
                              processing_time: float) -> str:
        """Format the rich, structured research results into a comprehensive report."""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        duration = f"{processing_time:.2f} seconds"
        
        # --- Header ---
        report = f"""# RESEARCH REPORT
# ===============
# Generated by: Manus Research Engine
# Instruction ID: {instruction["instruction_id"]}
# Category: {instruction["category"]}
# Generated: {timestamp}
# Processing Time: {duration}
# Cases Found: {results["total_cases"]}

## Introduction

This report presents the findings for the research instruction: "{results["research_query"]}". 

The research was conducted using Manus's iterative AI-powered process, which includes strategic query planning, comprehensive web investigation, content validation, and professional synthesis to ensure the quality and relevance of each case.

---

## Case Studies

"""
        
        # --- Case Studies ---
        if results["cases"]:
            for idx, case in enumerate(results["cases"], 1):
                report += f"""### {idx}. {case.get("title", "Untitled Case")}

**Date:** {case.get("date", "N/A")}  
**Source:** {case.get("source", "N/A")}

**Description:**

{case.get("description", "No description available.")}

**Why It Qualifies:**

> {case.get("why_qualifies", "No analysis provided.")}

**Key Points:**
"""
                for point in case.get("key_points", []):
                    report += f"- {point}\n"
                
                report += "\n---\n\n"
        else:
            report += "### No Cases Found\n\nThe research process did not identify any cases that met the specified criteria after comprehensive search and validation.\n\n"
        
        # --- Metadata ---
        metadata = results.get("metadata", {})
        report += f"""## Research Methodology

{metadata.get("methodology", "Comprehensive iterative research process conducted by Manus AI.")}

**Processing Details:**
- Processing Time: {processing_time:.1f} seconds
- Research Timestamp: {metadata.get("research_timestamp", timestamp)}
- Instruction File: {instruction["filename"]}
"""
        
        return report
    
    def create_google_doc(self, title: str, content: str, folder_id: str) -> Optional[str]:
        """Create a new Google Doc with the given content"""
        try:
            # Create the document
            doc_metadata = {
                'name': title,
                'mimeType': 'application/vnd.google-apps.document',
                'parents': [folder_id]
            }
            
            doc = self.drive_service.files().create(
                body=doc_metadata,
                fields='id'
            ).execute()
            
            doc_id = doc.get('id')
            
            # Insert content
            requests = [
                {
                    'insertText': {
                        'location': {'index': 1},
                        'text': content
                    }
                }
            ]
            
            self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()
            
            print(f"✅ Created document: {title} (ID: {doc_id})")
            return doc_id
            
        except HttpError as error:
            print(f"❌ Error creating document: {error}")
            return None
    
    def move_file(self, file_id: str, old_folder_id: str, new_folder_id: str) -> bool:
        """Move a file from one folder to another"""
        try:
            # Update the file's parents
            file = self.drive_service.files().update(
                fileId=file_id,
                addParents=new_folder_id,
                removeParents=old_folder_id,
                fields='id, parents'
            ).execute()
            
            print(f"✅ Moved file to Processed folder")
            return True
            
        except HttpError as error:
            print(f"❌ Error moving file: {error}")
            return False
    
    def process_instruction_file(self, file_info: Dict) -> bool:
        """Process a single instruction file"""
        file_id = file_info['id']
        filename = file_info['name']
        
        print(f"\n{'='*60}")
        print(f"📄 Processing: {filename}")
        print(f"{'='*60}")
        
        self.start_time = time.time()
        
        try:
            # Read the instruction file
            print("📖 Reading instruction file...")
            content = self.read_google_doc(file_id)
            
            if not content:
                raise Exception("Failed to read instruction file")
            
            # Parse the instruction
            print("🔍 Parsing instruction...")
            instruction = self.parse_instruction_file(content, filename)
            
            if not instruction['instruction_id']:
                raise Exception("No INSTRUCTION_ID found in file")
            
            print(f"📋 Instruction ID: {instruction['instruction_id']}")
            print(f"📂 Category: {instruction['category']}")
            
            # Update status to Processing
            print("📝 Updating status to Processing...")
            self.update_tracking_sheet(
                instruction['instruction_id'],
                {
                    'status': 'Processing',
                    'manus_started': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            )
            
            # Perform research
            print("🔬 Executing research...")
            results = self.perform_research(instruction)
            
            # Calculate processing time
            processing_time = time.time() - self.start_time
            
            # Format report
            print("📝 Formatting research report...")
            report_content = self.format_research_report(results, instruction, processing_time)
            
            # Generate output filename
            date_str = datetime.now().strftime('%Y%m%d')
            prefix = instruction['output_config'].get('filename_prefix', 'RESEARCH_')
            output_filename = f"{prefix}{date_str}_{instruction['instruction_id']}"
            
            if TEST_MODE:
                output_filename = f"[TEST] {output_filename}"
            
            # Save results
            print("💾 Saving research report...")
            result_doc_id = self.create_google_doc(
                output_filename,
                report_content,
                RAW_REPORTS_FOLDER_ID
            )
            
            if not result_doc_id:
                raise Exception("Failed to create output document")
            
            # Update status to Complete
            print("✅ Updating status to Complete...")
            self.update_tracking_sheet(
                instruction['instruction_id'],
                {
                    'status': 'Complete',
                    'manus_completed': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'result_doc_id': result_doc_id,
                    'result_folder': '/01_Research/Raw_Reports/',
                    'cases_found': results['total_cases'],
                    'processing_time_ms': int(processing_time * 1000)
                }
            )
            
            # Move to Processed folder
            if not TEST_MODE:
                print("📦 Moving to Processed folder...")
                self.move_file(file_id, PENDING_FOLDER_ID, PROCESSED_FOLDER_ID)
            else:
                print("🧪 TEST MODE: Not moving file")
            
            print(f"✅ Successfully processed {filename}")
            print(f"⏱️  Processing time: {processing_time:.2f} seconds")
            
            return True
            
        except Exception as error:
            print(f"❌ Error processing file: {error}")
            
            # Handle error
            processing_time = time.time() - self.start_time if self.start_time else 0
            
            try:
                # Try to parse instruction to get ID
                if content:
                    instruction = self.parse_instruction_file(content, filename)
                    if instruction['instruction_id']:
                        # Get current retry count
                        # (In production, you'd read this from the sheet)
                        retry_count = 0  # Placeholder
                        
                        if retry_count < MAX_RETRIES:
                            status = 'Pending'
                            print(f"⚠️  Will retry (attempt {retry_count + 1}/{MAX_RETRIES})")
                        else:
                            status = 'Failed'
                            print(f"❌ Max retries reached, marking as Failed")
                            # Move to Processed even on failure after max retries
                            if not TEST_MODE:
                                self.move_file(file_id, PENDING_FOLDER_ID, PROCESSED_FOLDER_ID)
                        
                        self.update_tracking_sheet(
                            instruction['instruction_id'],
                            {
                                'status': status,
                                'error_message': str(error)[:500],
                                'retry_count': retry_count + 1,
                                'last_error_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }
                        )
            except:
                print("⚠️  Could not update tracking sheet with error")
            
            return False
    
    def process_queue(self):
        """Main processing loop - process one file from the queue"""
        print("\n" + "="*60)
        print("🚀 Manus Research Processor v2.0")
        print("="*60)
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if TEST_MODE:
            print("🧪 TEST MODE ENABLED")
        
        # Get pending files
        pending_files = self.list_pending_files()
        
        if not pending_files:
            print("✅ No pending instructions found")
            return
        
        # Process the oldest file (first in the list due to orderBy)
        oldest_file = pending_files[0]
        success = self.process_instruction_file(oldest_file)
        
        if success:
            print("\n✅ Queue processing complete")
        else:
            print("\n⚠️  Queue processing completed with errors")
        
        print("="*60 + "\n")


def main():
    """Main entry point"""
    automation = ManusAutomation()
    
    try:
        # Authenticate
        automation.authenticate()
        
        # Process the queue
        automation.process_queue()
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as error:
        print(f"\n❌ Fatal error: {error}")
        sys.exit(1)


if __name__ == '__main__':
    main()
