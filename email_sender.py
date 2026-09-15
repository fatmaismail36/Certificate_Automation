import time
import smtplib
from pathlib import Path
from email.message import EmailMessage


def connect_to_smtp(
    smtp_server,
    smtp_port,
    smtp_email,
    smtp_password,
):
    if not smtp_server:
        raise ValueError("SMTP server cannot be empty.")

    if not smtp_email:
        raise ValueError("SMTP email cannot be empty.")

    if not smtp_password:
        raise ValueError("SMTP password cannot be empty.")

    smtp = smtplib.SMTP(
        smtp_server,
        int(smtp_port),
        timeout=60,
    )

    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    smtp.login(
        smtp_email,
        smtp_password,
    )

    return smtp


def create_email(
    recipient,
    certificate_path,
    subject,
    message,
    sender_email,
):
    if not subject or not subject.strip():
        raise ValueError("Email subject cannot be empty.")

    if not message or not message.strip():
        raise ValueError("Email message cannot be empty.")

    if not sender_email or not sender_email.strip():
        raise ValueError("Sender email cannot be empty.")

    certificate_path = Path(
        certificate_path
    )

    if not certificate_path.exists():
        raise FileNotFoundError(
            f"Certificate file not found: {certificate_path}"
        )

    name = str(
        recipient.get(
            "name",
            "",
        )
    )

    email = str(
        recipient.get(
            "email",
            "",
        )
    ).strip().lower()

    if not email:
        raise ValueError(
            "Recipient email cannot be empty."
        )

    personalized_message = message.replace(
        "{name}",
        name,
    )

    msg = EmailMessage()

    msg["From"] = sender_email
    msg["To"] = email
    msg["Subject"] = subject

    msg.set_content(
        personalized_message
    )

    with open(
        certificate_path,
        "rb",
    ) as certificate_file:

        certificate_data = certificate_file.read()

    msg.add_attachment(
        certificate_data,
        maintype="application",
        subtype="pdf",
        filename=certificate_path.name,
    )

    return msg


def send_one_email(
    smtp,
    recipient,
    certificate_path,
    subject,
    message,
    sender_email,
):
    email_message = create_email(
        recipient=recipient,
        certificate_path=certificate_path,
        subject=subject,
        message=message,
        sender_email=sender_email,
    )

    smtp.send_message(
        email_message
    )


def send_with_retry(
    smtp,
    recipient,
    certificate_path,
    subject,
    message,
    sender_email,
    retries=3,
):
    retries = max(
        int(retries),
        0,
    )

    last_error = ""

    for attempt in range(
        retries + 1
    ):

        try:

            send_one_email(
                smtp=smtp,
                recipient=recipient,
                certificate_path=certificate_path,
                subject=subject,
                message=message,
                sender_email=sender_email,
            )

            return True, ""

        except Exception as error:

            last_error = str(error)

            if attempt < retries:
                time.sleep(2)

    return False, last_error


def recipient_key(recipient):
    name = str(
        recipient.get(
            "name",
            "",
        )
    )

    email = str(
        recipient.get(
            "email",
            "",
        )
    ).strip().lower()

    certificate = str(
        recipient.get(
            "certificate",
            "",
        )
    )

    return (
        name,
        email,
        certificate,
    )