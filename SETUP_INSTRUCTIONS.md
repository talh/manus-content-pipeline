# Setup Instructions for Manus Content Pipeline Automation

Follow these steps to set up the automation system.

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Fill in:
   - **Repository name**: `manus-content-pipeline`
   - **Description**: "Automated research processing for content pipeline"
   - **Visibility**: **Public** (required for Manus to access without authentication)
3. **DO NOT** initialize with README (we have our own files)
4. Click "Create repository"

## Step 2: Upload Files to GitHub

### Option A: Using GitHub Web Interface (Easiest)

1. On your new repository page, click "uploading an existing file"
2. Drag and drop ALL files from the `manus-content-pipeline` folder:
   - `run_automation.py`
   - `manus_automation.py`
   - `manus_research_integrated.py`
   - `config.py`
   - `complete_auth.py`
   - `requirements.txt`
   - `setup.sh`
   - `README.md`
   - `.gitignore`
   - `credentials.json.template`
   - `SETUP_INSTRUCTIONS.md` (this file)
3. Commit message: "Initial commit - automation files"
4. Click "Commit changes"

### Option B: Using Git Command Line

```bash
cd /path/to/manus-content-pipeline
git init
git add .
git commit -m "Initial commit - automation files"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/manus-content-pipeline.git
git push -u origin main
```

## Step 3: Add Your Credentials

### 3.1: Add credentials.json

1. Copy your `credentials.json` file (the one you downloaded from Google Cloud Console)
2. In your GitHub repository, click "Add file" → "Upload files"
3. Upload `credentials.json`
4. Commit with message: "Add OAuth credentials"

**⚠️ IMPORTANT**: If your repository is public, anyone can see these credentials. Consider:
- Making the repository private (requires GitHub authentication in scheduled task)
- Or using environment variables (more complex setup)
- Or accepting that these are low-risk OAuth credentials (they still require user authorization)

### 3.2: Generate and Add token.json

You need to generate the OAuth token locally first:

1. Download the repository files to your local machine
2. Make sure you have Python 3.11+ installed
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the authentication script:
   ```bash
   python3 complete_auth.py
   ```
5. Follow the prompts:
   - Open the URL in your browser
   - Grant permissions
   - Copy the redirect URL
   - Paste it back
6. This creates `token.json`
7. Upload `token.json` to your GitHub repository

## Step 4: Configure Folder IDs

1. Edit `config.py` in your GitHub repository
2. Update with your actual folder IDs:

```python
PENDING_FOLDER_ID = '1VQxl_FC1jVSdwHzDphfcQtIxMvo5CeSI'  # Your Pending folder
PROCESSED_FOLDER_ID = '1v-8MUeGW9irQDeKCYk8PPkINqeBL9Z2Z'  # Your Processed folder
RAW_REPORTS_FOLDER_ID = '1VSoi7t9309t0jyfQrwoZg2hDVgpMMkax'  # Your Raw_Reports folder
TRACKING_SHEET_ID = '1tC72KFZJ4mi6o2bb2tEF4SGmFMtDzfcghRjIHa8X-3g'  # Your tracking sheet
```

3. Commit the changes

## Step 5: Update Scheduled Task

Now update your Manus scheduled task to use the GitHub repository:

### Delete the Old Task

1. In Manus, find your existing "Content Pipeline Research Processor" task
2. Delete it (since it was pointing to local files)

### Create New Task

Create a new scheduled task with these settings:

**Name**: `Content Pipeline Research Processor`

**Type**: `interval`

**Interval**: `300` (5 minutes)

**Repeat**: `true`

**Prompt**:
```
Execute the Manus Content Pipeline automation from GitHub repository.

Steps:
1. Clone the repository from GitHub
2. Install Python dependencies
3. Run the automation script

Repository: https://github.com/YOUR_USERNAME/manus-content-pipeline

Execute these commands:
```bash
cd /tmp
rm -rf manus-content-pipeline
git clone https://github.com/YOUR_USERNAME/manus-content-pipeline.git
cd manus-content-pipeline
bash setup.sh
```
```

**Replace `YOUR_USERNAME`** with your actual GitHub username!

**Playbook** (optional but recommended):
```
This task processes research instructions from Google Drive.

Workflow:
1. Clone automation code from GitHub
2. Install dependencies (google-api-python-client, beautifulsoup4, etc.)
3. Authenticate with Google using saved token
4. Check Pending folder for instruction files
5. Process oldest file (FIFO)
6. Perform web research using DuckDuckGo
7. Generate research report
8. Update tracking sheet
9. Move file to Processed folder

The repository contains:
- run_automation.py: Entry point
- manus_automation.py: Main logic
- manus_research_integrated.py: Research engine
- config.py: Configuration
- credentials.json: OAuth credentials
- token.json: OAuth token

Error handling: Max 3 retries, errors logged to tracking sheet
```

## Step 6: Test the Setup

### First Test Run

1. Add a test instruction file to your Pending folder
2. Add corresponding row to tracking sheet
3. Wait for the scheduled task to run (within 5 minutes)
4. Monitor the tracking sheet for status updates

### Check Results

- **Tracking Sheet**: Status should change from Pending → Processing → Complete
- **Processed Folder**: Instruction file should appear here
- **Raw_Reports Folder**: Research report should be created
- **Console Output**: Check Manus task logs for detailed output

## Troubleshooting

### "credentials.json not found"

- Make sure you uploaded `credentials.json` to the GitHub repository
- Check the file name is exactly `credentials.json`

### "token.json not found"

- Run `complete_auth.py` locally to generate the token
- Upload `token.json` to GitHub repository

### "API not enabled"

- Enable required APIs in Google Cloud Console:
  - Google Drive API
  - Google Sheets API
  - Google Docs API

### "Permission denied"

- Check OAuth scopes in credentials
- Regenerate token with correct scopes

### "Repository not found"

- Verify repository is public
- Check GitHub username in URL is correct
- Ensure repository name is `manus-content-pipeline`

### "Module not found"

- Check `requirements.txt` is in repository
- Verify `setup.sh` runs `pip install -r requirements.txt`

## Updating the Code

To update the automation:

1. Make changes to files locally or in GitHub web interface
2. Commit and push changes
3. Next scheduled run will automatically use updated code
4. No need to restart or reconfigure anything!

## Security Best Practices

1. **Credentials**: Consider using private repository or environment variables
2. **Token Rotation**: Regenerate OAuth token periodically
3. **Access Control**: Limit OAuth scopes to minimum required
4. **Monitoring**: Regularly check tracking sheet for errors
5. **Backups**: Keep backup of credentials and configuration

## Success Checklist

- [ ] GitHub repository created and public
- [ ] All automation files uploaded
- [ ] `credentials.json` added to repository
- [ ] `token.json` generated and uploaded
- [ ] `config.py` updated with your folder IDs
- [ ] Scheduled task created with correct GitHub URL
- [ ] Test instruction file processed successfully
- [ ] Tracking sheet updating correctly
- [ ] Reports generating in Raw_Reports folder

## Next Steps

Once everything is working:

1. Add more instruction files to process
2. Monitor the tracking sheet
3. Review generated reports
4. Adjust configuration as needed
5. Update research parameters for better results

## Support

If you encounter issues:

1. Check the Manus task console output
2. Review tracking sheet Error_Message column
3. Verify all folder IDs are correct
4. Test authentication locally
5. Check GitHub repository is accessible

---

**You're all set!** The automation will now run every 5 minutes automatically. 🎉
