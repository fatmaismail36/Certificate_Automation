import smtplib

import time

from email.message import EmailMessage

from datetime import datetime

from config import (
    SMTP_SERVER,
    SMTP_PORT,
    SMTP_EMAIL,
    SMTP_PASSWORD,
    EMAIL_SUBJECT,
    EMAIL_DELAY,
    TEST_LIMIT
)


def create_email(recipient_name, recipient_email, certificate_path):

    message = EmailMessage()

    message["From"] = SMTP_EMAIL

    message["To"] = recipient_email

    message["Subject"] = "AFRIC Certificate for 2026"

    body = f"""

Dear Doctor,

Thank you for attending AFRIC 2026 and for being part of this successful event.

Please find attached your Certificate of Attendance for the conference.

We truly appreciate your participation and look forward to welcoming you again at future AFRIC events.

"""

    message.set_content(body.strip())

    with open(certificate_path, "rb") as certificate_file:

        certificate_data = certificate_file.read()

    message.add_attachment(
        certificate_data,
        maintype="application",
        subtype="pdf",
        filename=certificate_path.name
    )

    return message


def connect_to_smtp():

    print()

    print("========================================")

    print("CONNECTING TO SMTP SERVER")

    print("========================================")

    if not SMTP_EMAIL:

        raise ValueError("SMTP_EMAIL is missing from .env")

    if not SMTP_PASSWORD:

        raise ValueError("SMTP_PASSWORD is missing from .env")

    print(f"Server: {SMTP_SERVER}")

    print(f"Port: {SMTP_PORT}")

    print(f"Email: {SMTP_EMAIL}")

    server = smtplib.SMTP(
        SMTP_SERVER,
        SMTP_PORT,
        timeout=30
    )

    server.ehlo()

    server.starttls()

    server.ehlo()

    server.login(
        SMTP_EMAIL,
        SMTP_PASSWORD
    )

    print()

    print("SMTP authentication successful!")

    return server


def send_one_email(
    server,
    recipient_name,
    recipient_email,
    certificate_path
):

    message = create_email(
        recipient_name,
        recipient_email,
        certificate_path
    )

    server.send_message(message)


def run_dry_run(ready_recipients):

    print()

    print("========================================")

    print("DRY RUN MODE")

    print("========================================")

    print("NO EMAILS WILL ACTUALLY BE SENT.")

    log_rows = []

    processed_count = 0

    for recipient in ready_recipients:

        if (
            TEST_LIMIT is not None
            and processed_count >= TEST_LIMIT
        ):

            break

        name = recipient["Name"]

        email = recipient["Email"]

        certificate_path = recipient["certificate_path"]

        row_number = recipient["row_number"]

        print()

        print("----------------------------------------")

        print(f"Recipient #{processed_count + 1}")

        print(f"Excel row: {row_number}")

        print(f"Name: {name}")

        print(f"Email: {email}")

        print(f"Certificate: {certificate_path.name}")

        print("Status: READY")

        log_rows.append({

            "timestamp": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

            "row_number": row_number,

            "name": name,

            "email": email,

            "certificate": certificate_path.name,

            "status": "READY",

            "error": ""

        })

        processed_count += 1

    return processed_count, log_rows


def show_final_confirmation(ready_recipients):

    if not ready_recipients:

        return False

    recipients_to_send = ready_recipients

    if TEST_LIMIT is not None:

        recipients_to_send = ready_recipients[:TEST_LIMIT]

    print()

    print("========================================")

    print("FINAL SENDING CONFIRMATION")

    print("========================================")

    print()

    print("The following email(s) will be sent:")

    print()

    for index, recipient in enumerate(
        recipients_to_send,
        start=1
    ):

        print("----------------------------------------")

        print(f"Email #{index}")

        print(f"Excel row: {recipient['row_number']}")

        print(f"Name: {recipient['Name']}")

        print(f"Email: {recipient['Email']}")

        print(
            f"Certificate: "
            f"{recipient['certificate_path'].name}"
        )

    print("----------------------------------------")

    print()

    print(
        f"TOTAL EMAILS TO BE SENT NOW: "
        f"{len(recipients_to_send)}"
    )

    print()

    print("IMPORTANT:")

    print("Only type 'yes' if everything above is correct.")

    print("Type anything else to cancel.")

    print()

    confirmation = input(
        "Continue with sending? (yes/no): "
    ).strip().lower()

    if confirmation == "yes":

        print()

        print("Confirmation accepted.")

        print("Starting email sending...")

        return True

    print()

    print("Sending cancelled by user.")

    return False


def send_batch(
    ready_recipients,
    already_sent_rows
):

    print()

    print("========================================")

    print("REAL EMAIL SENDING MODE")

    print("========================================")

    print("WARNING: REAL EMAILS WILL BE SENT.")

    recipients_to_check = []

    for recipient in ready_recipients:

        if recipient["row_number"] in already_sent_rows:

            continue

        if (
            TEST_LIMIT is not None
            and len(recipients_to_check) >= TEST_LIMIT
        ):

            break

        recipients_to_check.append(recipient)

    confirmed = show_final_confirmation(
        recipients_to_check
    )

    if not confirmed:

        return 0, 0, 0, []

    server = None

    sent_count = 0

    failed_count = 0

    skipped_count = 0

    log_rows = []

    try:

        server = connect_to_smtp()

        processed_for_test = 0

        for recipient in ready_recipients:

            row_number = recipient["row_number"]

            name = recipient["Name"]

            email = recipient["Email"]

            certificate_path = recipient["certificate_path"]

            if row_number in already_sent_rows:

                skipped_count += 1

                print()

                print("----------------------------------------")

                print(f"Excel row: {row_number}")

                print(f"Name: {name}")

                print("STATUS: ALREADY SENT - SKIPPED")

                continue

            if (
                TEST_LIMIT is not None
                and processed_for_test >= TEST_LIMIT
            ):

                break

            processed_for_test += 1

            print()

            print("----------------------------------------")

            print(f"Sending #{processed_for_test}")

            print(f"Excel row: {row_number}")

            print(f"Name: {name}")

            print(f"Email: {email}")

            print(f"Certificate: {certificate_path.name}")

            try:

                send_one_email(
                    server,
                    name,
                    email,
                    certificate_path
                )

                sent_count += 1

                print("STATUS: SENT")

                log_rows.append({

                    "timestamp": datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),

                    "row_number": row_number,

                    "name": name,

                    "email": email,

                    "certificate": certificate_path.name,

                    "status": "SENT",

                    "error": ""

                })

                time.sleep(EMAIL_DELAY)

            except Exception as error:

                failed_count += 1

                print("STATUS: FAILED")

                print(f"ERROR: {error}")

                log_rows.append({

                    "timestamp": datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),

                    "row_number": row_number,

                    "name": name,

                    "email": email,

                    "certificate": certificate_path.name,

                    "status": "FAILED",

                    "error": str(error)

                })

    except Exception as error:

        print()

        print("========================================")

        print("SMTP CONNECTION FAILED")

        print("========================================")

        print(error)

    finally:

        if server is not None:

            try:

                server.quit()

                print()

                print("SMTP connection closed.")

            except Exception:

                pass

    return (
        sent_count,
        failed_count,
        skipped_count,
        log_rows
    )