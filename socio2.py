import os
import base64
import re
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from bs4 import BeautifulSoup

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    """Authenticate using OAuth 2.0 and return the Gmail API service."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("socio.json", SCOPES)
        creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)

def get_recent_emails(service, user_id="me", max_results=5):
    """Retrieve the latest emails from Gmail."""
    results = service.users().messages().list(userId=user_id, maxResults=max_results).execute()
    return results.get("messages", [])

def get_email_body(service, user_id, msg_id):
    """Extract the email body from a given email ID."""
    message = service.users().messages().get(userId=user_id, id=msg_id, format="full").execute()
    payload = message["payload"]
    body = ""

    if "parts" in payload:
        for part in payload["parts"]:
            if part.get("mimeType") == "text/html":
                body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                break
    elif "body" in payload:
        body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")

    return body

def extract_links(html_content):
    """Extract all links from an email using BeautifulSoup."""
    soup = BeautifulSoup(html_content, "html.parser")
    links = [a["href"] for a in soup.find_all("a", href=True)]
    return links

def main():
    service = authenticate_gmail()
    messages = get_recent_emails(service)

    for msg in messages:
        email_body = get_email_body(service, "me", msg["id"])
        links = extract_links(email_body)

        print("Extracted Links:", links)

if __name__ == "__main__":
    main()
