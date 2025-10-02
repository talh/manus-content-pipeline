# Quick Start Guide

Get your automation running in 10 minutes!

## Prerequisites

- [ ] Google Cloud project with Drive, Sheets, and Docs APIs enabled
- [ ] OAuth credentials downloaded as `credentials.json`
- [ ] GitHub account
- [ ] Manus account with scheduling enabled

## 5-Step Setup

### 1. Create GitHub Repository (2 minutes)

1. Go to https://github.com/new
2. Name: `manus-content-pipeline`
3. Visibility: **Public**
4. Click "Create repository"

### 2. Upload Files (3 minutes)

Download the zip file and extract, then:

1. In GitHub, click "uploading an existing file"
2. Drag all files from `manus-content-pipeline` folder
3. Commit changes

### 3. Update Configuration (2 minutes)

Edit `config.py` in GitHub with your IDs:

```python
PENDING_FOLDER_ID = 'YOUR_PENDING_FOLDER_ID'
PROCESSED_FOLDER_ID = 'YOUR_PROCESSED_FOLDER_ID'  
RAW_REPORTS_FOLDER_ID = 'YOUR_RAW_REPORTS_FOLDER_ID'
TRACKING_SHEET_ID = 'YOUR_SHEET_ID'
```

### 4. Create Scheduled Task (2 minutes)

In Manus, create a new scheduled task:

- **Name**: Content Pipeline Research Processor
- **Type**: Interval
- **Interval**: 300 seconds
- **Repeat**: Yes

**Prompt**:
```
cd /tmp && rm -rf manus-content-pipeline && git clone https://github.com/YOUR_USERNAME/manus-content-pipeline.git && cd manus-content-pipeline && bash setup.sh
```

Replace `YOUR_USERNAME` with your GitHub username!

### 5. Test (1 minute)

1. Add a test instruction file to Pending folder
2. Add row to tracking sheet
3. Wait 5 minutes
4. Check results!

## Done! 🎉

Your automation is now running every 5 minutes.

## What Happens Next?

Every 5 minutes:
1. ✅ Checks Pending folder
2. ✅ Processes oldest file
3. ✅ Performs web research
4. ✅ Generates report
5. ✅ Updates tracking sheet
6. ✅ Moves file to Processed

## Monitoring

**Tracking Sheet**: Watch Status column  
**Processed Folder**: See archived files  
**Raw_Reports Folder**: Find generated reports  

## Need Help?

See `SETUP_INSTRUCTIONS.md` for detailed steps and troubleshooting.

---

**Happy Automating!** 🚀
