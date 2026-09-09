import os
import threading
import time

import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("MS_GRAPH_CLIENT_ID")
CLIENT_SECRET = os.getenv("MS_GRAPH_CLIENT_SECRET")
TENANT_ID = os.getenv("MS_GRAPH_TENANT_ID")
MS365_ADDRESS = os.getenv("MS365_ADDRESS")
TOKEN_URL = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"
TOKEN_EXPIRY_BUFFER = 60
MESSAGE_LIMIT = 100

_token = None
_token_expires_at = 0
_token_lock = threading.Lock()


def _get_token():
    global _token, _token_expires_at

    with _token_lock:
        if _token and time.time() < _token_expires_at - TOKEN_EXPIRY_BUFFER:
            return _token

        response = requests.post(
            TOKEN_URL,
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "scope": "https://graph.microsoft.com/.default",
                "grant_type": "client_credentials",
            },
            timeout=30,
        )
        response.raise_for_status()
        token_data = response.json()
        _token = token_data["access_token"]
        _token_expires_at = time.time() + int(token_data.get("expires_in", 3600))
        return _token


def _headers():
    return {
        "Authorization": f"Bearer {_get_token()}",
        "Content-Type": "application/json",
    }


def send_mail(to, subject, html):
    response = requests.post(
        f"{GRAPH_BASE_URL}/users/{MS365_ADDRESS}/sendMail",
        headers=_headers(),
        json={
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML",
                    "content": html,
                },
                "toRecipients": [{
                    "emailAddress": {"address": to}
                }],
            },
            "saveToSentItems": True,
        },
        timeout=30,
    )
    response.raise_for_status()


def list_recent_messages(since_iso):
    response = requests.get(
        f"{GRAPH_BASE_URL}/users/{MS365_ADDRESS}/messages",
        headers=_headers(),
        params={
            "$filter": f"receivedDateTime ge {since_iso}",
            "$select": "subject,from,body,receivedDateTime",
            "$orderby": "receivedDateTime desc",
            "$top": MESSAGE_LIMIT,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json().get("value", [])
