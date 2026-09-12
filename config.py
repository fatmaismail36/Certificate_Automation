from pathlib import Path

import os

from dotenv import load_dotenv

load_dotenv()

EXCEL_FILE = Path(
    "data/recipients.xlsx"
)

CERTIFICATE_FOLDER = Path(
    "certificates"
)

LOG_FOLDER = Path(
    "logs"
)

LOG_FILE = LOG_FOLDER / "sending_log.csv"

DRY_RUN = False

TEST_LIMIT = 1

TEST_LIMIT = 1

SMTP_SERVER = os.getenv(
    "SMTP_SERVER",
    "smtp.office365.com"
)

SMTP_PORT = int(
    os.getenv(
        "SMTP_PORT",
        "587"
    )
)

SMTP_EMAIL = os.getenv(
    "SMTP_EMAIL",
    ""
)

SMTP_PASSWORD = os.getenv(
    "SMTP_PASSWORD",
    ""
)

EMAIL_SUBJECT = (
    "Your Certificate of Participation"
)

EMAIL_DELAY = 2

CERTIFICATE_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

LOG_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)