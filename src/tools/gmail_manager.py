import os
import re
import base64
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

class GmailManager:

    # Initialize Gmail API service
    def __init__(self):
        self.service = self._get_gmail_service()
    
    # Authenticate and build Gmail API service
    def _get_gmail_service(self):
        creds = None

        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json",
                    SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open("token.json", "w") as token:
                token.write(creds.to_json())

        service = build("gmail", "v1", credentials=creds)

        return service

    # Fetch emails that don't already have a draft reply
    def fetch_unanswered_emails(self, max_results=50, hours=8):
        recent_emails = self._fetch_recent_emails(max_results, hours)
        if not recent_emails:
            return []

        drafts = self._fetch_draft_replies()
        threads_with_drafts = set()

        for draft in drafts:
            threads_with_drafts.add(draft["threadId"])

        seen_threads = set()
        unanswered = []

        for email in recent_emails:
            thread_id = email["threadId"]
            if thread_id in seen_threads or thread_id in threads_with_drafts:
                continue

            seen_threads.add(thread_id)
            email_info = self._get_email_info(email["id"])
            if self._should_skip_email(email_info):
                continue

            unanswered.append(email_info)

        return unanswered

    # Fetch recent emails from Gmail within a time window
    def _fetch_recent_emails(self, max_results=50, hours=8):
        try:
            now = datetime.now()
            start_time = now - timedelta(hours=hours)

            after_ts = int(start_time.timestamp())
            before_ts = int(now.timestamp())

            query = f"after:{after_ts} before:{before_ts}"

            results = self.service.users().messages().list(
                userId="me",
                q=query,
                maxResults=max_results
            ).execute()

            return results.get("messages", [])

        except Exception as e:
            print("Error fetching emails within the {hours} hours timeframe:", e)
            return []

    # Fetch all draft replies from Gmail
    def _fetch_draft_replies(self):
        try:
            results = self.service.users().drafts().list(userId="me").execute()

            drafts = results.get("drafts", [])

            output = []

            for draft in drafts:
                msg = draft["message"]

                output.append({
                    "draft_id": draft["id"],
                    "threadId": msg.get("threadId"),
                    "id": msg.get("id")
                })

            return output

        except Exception as e:
            print("Error fetching drafts:", e)
            return []

    # Create a draft reply for an email
    def create_draft_reply(self, initial_email, reply_text):
        try:
            message = self._create_reply_message_body(initial_email, reply_text)

            draft = self.service.users().drafts().create(
                userId="me",
                body={"message": message}
            ).execute()

            return draft

        except Exception as e:
            print("Error creating draft:", e)
            return None

    # Send a reply email immediately
    def send_reply(self, initial_email, reply_text):
        try:
            message = self._create_reply_message_body(initial_email, reply_text)

            sent = self.service.users().messages().send(
                userId="me",
                body=message
            ).execute()

            return sent

        except Exception as e:
            print("Error sending email:", e)
            return None

    # Build a reply message structure
    def _create_reply_message_body(self, email, reply_text):

        message = self._create_email_message(
            email.sender,
            email.subject,
            reply_text
        )

        if email.messageId:
            message["In-Reply-To"] = email.messageId
            message["References"] = email.messageId

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        body = {
            "raw": raw,
            "threadId": email.threadId
        }

        return body

    
    # Skip emails sent by the same account
    def _should_skip_email(self, email_info):
        my_email = os.environ.get("MY_EMAIL")
        if not my_email:
            return False
        if my_email in email_info["sender"]:
            return True
        else:
            return False

    # Retrieve email metadata and body
    def _get_email_info(self, msg_id):

        message = self.service.users().messages().get(
            userId="me",
            id=msg_id,
            format="full"
        ).execute()

        payload = message.get("payload", {})
        headers_list = payload.get("headers", [])

        headers = {}

        for header in headers_list:
            headers[header["name"].lower()] = header["value"]

        return {
            "id": msg_id,
            "threadId": message.get("threadId"),
            "messageId": headers.get("message-id"),
            "sender": headers.get("from", "Unknown"),
            "subject": headers.get("subject", "No Subject"),
            "body": self._get_email_body(payload)
        }

    # Extract text body from email payload
    def _get_email_body(self, payload):

        parts = payload.get("parts")
        if not parts:
            data = payload.get("body",{}).get("data")
            if not data:
                return ""
            
            text = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
            if payload.get("mimeType") == "text/html":
                text = self._extract_text_from_html(text)

            return self._clean_text(text)

        text_body = ""
        html_body = ""

        stack = list(parts)
        while stack:
            part = stack.pop()

            mime = part.get("mimeType", "")
            body = part.get("body", {})
            data = body.get("data")

            if mime == "text/plain" and data:
                text_body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
            elif mime == "text/html" and data:
                html = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
                html_body = self._extract_text_from_html(html)
            if part.get("parts"):
                stack.extend(part["parts"])

        result = text_body if text_body else html_body
        clean_result = self._clean_text(result)
        return clean_result

    # Remove scripts/styles and extract visible text from HTML
    def _extract_text_from_html(self, html):

        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(["script", "style"]):
            tag.decompose()

        text = soup.get_text(separator=" ")

        return text

    # Normalize whitespace in text
    def _clean_text(self, text):

        text = text.replace("\r", " ").replace("\n", " ")

        return re.sub(r"\s+", " ", text).strip()

    # Create multipart email with plaintext and HTML
    def _create_email_message(self, recipient, subject, reply_text):

        message = MIMEMultipart("alternative")
        message["to"] = recipient

        if subject.startswith("Re:"):
            message["subject"] = subject
        else:
            message["subject"] = "Re: " + subject

        plain_part = MIMEText(reply_text, "plain")
        html_text = reply_text.replace("\n", "<br>")

        html_part = MIMEText(f"<html><body>{html_text}</body></html>", "html")

        message.attach(plain_part)
        message.attach(html_part)

        return message