from __future__ import annotations

import os
from datetime import datetime
from typing import List

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def _credentials_from_env():
    cred_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
    if not cred_file:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_FILE is not set")
    return service_account.Credentials.from_service_account_file(cred_file, scopes=SCOPES)


def append_application_row(
    spreadsheet_id: str,
    sheet_name: str,
    url: str,
    company: str,
    title: str,
    status: str,
    suggested_bullets: List[str],
):
    creds = _credentials_from_env()
    service = build("sheets", "v4", credentials=creds)

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    row = [
        now,
        company,
        title,
        url,
        status,
        " | ".join(suggested_bullets[:5]),
    ]

    body = {"values": [row]}
    return (
        service.spreadsheets()
        .values()
        .append(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A:F",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body=body,
        )
        .execute()
    )
