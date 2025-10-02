# Manus Content Pipeline Automation

Automated research processing system that integrates with Google Drive to process research instructions, perform web research, and generate comprehensive reports.

## Overview

This system automatically:
- Monitors a Google Drive folder for research instruction files
- Processes instructions in FIFO order (oldest first)
- Performs AI-powered web research
- Generates structured research reports
- Updates a tracking spreadsheet
- Archives processed files

## Features

✅ **Automated Processing**: Runs every 5 minutes via Manus scheduler  
✅ **Real Web Research**: Uses DuckDuckGo to find actual information  
✅ **Google Drive Integration**: Reads/writes files and updates sheets  
✅ **Error Handling**: Automatic retry logic (max 3 attempts)  
✅ **FIFO Queue**: Processes oldest instructions first  
✅ **Comprehensive Logging**: Detailed console output for monitoring  

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│           Manus Scheduler (Every 5 minutes)             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              run_automation.py                          │
│         (Entry point - downloads from GitHub)           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│           manus_automation.py                           │
│     (Main orchestration and Drive operations)           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│       manus_research_integrated.py                      │
│    (AI-powered research with web scraping)              │
└─────────────────────────────────────────────────────────┘
```

## Files

| File | Purpose |
|:-----|:--------|
| `run_automation.py` | Entry point for scheduled task |
| `manus_automation.py` | Main automation logic and workflow |
| `manus_research_integrated.py` | Web research engine |
| `config.py` | Configuration settings |
| `complete_auth.py` | OAuth authentication helper |
| `requirements.txt` | Python dependencies |
| `setup.sh` | Setup script for scheduled task |

## Prerequisites

1. **Google Cloud Project** with APIs enabled:
   - Google Drive API
   - Google Sheets API
   - Google Docs API

2. **OAuth Credentials** (Desktop app type)
   - Download as `credentials.json`

3. **Google Drive Structure**:
   - Pending folder (for instruction files)
   - Processed folder (for archived files)
   - Raw_Reports folder (for generated reports)
   - Tracking spreadsheet (Manus_Queue tab)

## Installation

### Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `manus-content-pipeline`
3. Description: "Automated research processing for content pipeline"
4. Set to **Public** (required for Manus to access without auth)
5. Click "Create repository"

### Step 2: Upload Files

```bash
# Clone this directory or upload files via GitHub web interface
cd manus-content-pipeline
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/manus-content-pipeline.git
git push -u origin main
```

### Step 3: Configure Settings

Edit `config.py` with your folder IDs:

```python
PENDING_FOLDER_ID = 'your_pending_folder_id'
PROCESSED_FOLDER_ID = 'your_processed_folder_id'
RAW_REPORTS_FOLDER_ID = 'your_raw_reports_folder_id'
TRACKING_SHEET_ID = 'your_tracking_sheet_id'
```

### Step 4: First-Time Authentication

Run locally once to generate `token.json`:

```bash
python3 complete_auth.py
```

This will:
1. Open a browser for Google OAuth
2. Save the authentication token
3. Upload `token.json` to your repository

### Step 5: Create Manus Scheduled Task

In Manus, create a scheduled task with this prompt:

```
Clone the automation repository from GitHub and execute the content pipeline processor.

Repository: https://github.com/YOUR_USERNAME/manus-content-pipeline

Steps:
1. Clone the repository
2. Install dependencies
3. Run the automation script

Execute: bash setup.sh
```

## Configuration

### Folder IDs

Get folder IDs from Google Drive URLs:
- Open folder in Drive
- URL format: `https://drive.google.com/drive/folders/FOLDER_ID_HERE`
- Copy the ID portion

### Tracking Sheet Structure

Your `Manus_Queue` sheet should have these columns:

| Column | Field | Type |
|:-------|:------|:-----|
| A | Instruction_ID | Text |
| B | Status | Text (Pending/Processing/Complete/Failed) |
| C | Manus_Started | Timestamp |
| D | Manus_Completed | Timestamp |
| E | Result_Doc_ID | Text |
| F | Result_Folder | Text |
| G | Cases_Found | Number |
| H | Processing_Time_MS | Number |
| I | Error_Message | Text |
| J | Retry_Count | Number |
| K | Last_Error_Time | Timestamp |

### Instruction File Format

```
INSTRUCTION_ID: UNIQUE_ID_HERE
CATEGORY: Category Name
CATEGORY_ID: CAT_CODE
PRIORITY: Normal

INSTRUCTION:
Your research instruction goes here.
Can be multiple lines.

SEARCH_PARAMETERS:
date_range: Last 6 months
max_results: 10
depth: Comprehensive
include_sources: true

OUTPUT_CONFIG:
filename_prefix: RESEARCH_PREFIX_
format: Structured with cases
```

## Usage

### Adding Instructions

1. Create a Google Doc with instruction format
2. Place in Pending folder
3. Add row to tracking sheet with matching Instruction_ID
4. Wait for scheduled task (runs every 5 minutes)

### Monitoring

**Tracking Sheet**:
- Watch Status column for progress
- Check Result_Doc_ID for generated reports
- Review Error_Message if failed

**Google Drive**:
- Pending folder: Files disappear when processed
- Processed folder: Archived instruction files
- Raw_Reports folder: Generated research reports

## Workflow

1. **Scan**: Lists files in Pending folder (oldest first)
2. **Read**: Extracts instruction content
3. **Parse**: Structures instruction data
4. **Update**: Sets Status="Processing" in sheet
5. **Research**: Performs web search and extraction
6. **Generate**: Creates formatted report document
7. **Save**: Uploads report to Raw_Reports folder
8. **Complete**: Updates Status="Complete" in sheet
9. **Archive**: Moves instruction to Processed folder

## Error Handling

- **Retry Logic**: Failed files remain in Pending for retry
- **Max Retries**: 3 attempts before marking as Failed
- **Error Logging**: All errors recorded in tracking sheet
- **Graceful Degradation**: Continues processing queue on errors

## Research Capabilities

The research engine:
- Generates multiple search query variations
- Searches DuckDuckGo (no API key required)
- Extracts titles, descriptions, URLs
- Deduplicates results
- Ranks by quality score
- Formats as structured cases with key points

## Troubleshooting

### Authentication Errors

```bash
# Regenerate token
python3 complete_auth.py
```

### API Not Enabled

Enable required APIs in Google Cloud Console:
- https://console.cloud.google.com/apis/library

### Files Not Processing

- Check folder IDs in config.py
- Verify Instruction_ID exists in tracking sheet
- Check scheduled task is running

### Empty Research Results

- Verify instruction text is not empty
- Check internet connectivity
- Review search queries in logs

## Development

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run once
python3 run_automation.py
```

### Updating Code

1. Make changes locally
2. Commit and push to GitHub
3. Next scheduled run will use updated code

## Security

- **Credentials**: Never commit `credentials.json` or `token.json` to public repo
- **Environment Variables**: Use for sensitive data
- **OAuth Scopes**: Limited to Drive and Sheets access
- **Rate Limiting**: Built-in delays to avoid API limits

## Performance

- **Processing Time**: 1-3 seconds per instruction
- **Research Time**: 5-15 seconds depending on queries
- **Schedule Interval**: 5 minutes (configurable)
- **Concurrent Processing**: One file at a time

## License

MIT License - Feel free to modify and use

## Support

For issues or questions:
- Check console output for error messages
- Review tracking sheet for error details
- Verify all configuration settings
- Test with sample instruction first

## Version

- **Version**: 2.0
- **Last Updated**: October 2, 2025
- **Python Version**: 3.11+
- **Manus Compatible**: Yes

---

**Built for Manus Content Pipeline Automation** 🚀
