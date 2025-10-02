#!/usr/bin/env python3.11
"""
Complete OAuth authentication with authorization code
"""

import os
# Allow insecure transport for localhost (required for OAuth with http://localhost)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets'
]

# Authorization response URL from user
auth_response = "http://localhost/?state=6LOsqYEvy28WyyT21fZy2hDbZ2tSST&code=4/0AVGzR1DcwGbT0Ji50VdL_44bUtAfRgRAD4qgYWJKXK1d7UDRuKpIPv4oMNPyg0yoKBiv2A&scope=https://www.googleapis.com/auth/drive%20https://www.googleapis.com/auth/spreadsheets"

print("🔐 Completing authentication...")

# Create flow
flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
flow.redirect_uri = 'http://localhost'

# Fetch token using the authorization response
flow.fetch_token(authorization_response=auth_response)

# Get credentials
creds = flow.credentials

# Save to token.json
with open('token.json', 'w') as token:
    token.write(creds.to_json())

print("✅ Authentication complete!")
print("✅ Token saved to token.json")
print("\nYou can now run: python3.11 run_automation.py")
