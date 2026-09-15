import re
from pathlib import Path
import pandas as pd


def normalize_email(email):
    if pd.isna(email):
        return ""
    return str(email).strip().lower()


def is_valid_email(email):
    if not email:
        return False
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return bool(re.match(pattern, email))


def exact_name(name):
    if pd.isna(name):
        return ""
    return str(name)


def load_recipients(excel_file):
    print()
    print("========================================")
    print("LOADING EXCEL FILE")
    print("========================================")

    if not excel_file.exists():
        print("ERROR: Excel file not found:")
        print(excel_file)
        return None

    try:
        df = pd.read_excel(excel_file)
    except Exception as error:
        print(f"ERROR reading Excel: {error}")
        return None

    print("Excel loaded successfully!")
    print(f"Total rows: {len(df)}")

    required_columns = ["Name", "Email"]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        print()
        print("ERROR: Missing required columns:")

        for column in missing_columns:
            print(f" - {column}")

        return None

    return df


def load_certificates(certificate_folder):
    print()
    print("========================================")
    print("LOADING CERTIFICATES")
    print("========================================")

    if not certificate_folder.exists():
        print("ERROR: Certificate folder not found:")
        print(certificate_folder)
        return {}

    pdf_files = list(certificate_folder.glob("*.pdf"))

    print(f"PDF certificates found: {len(pdf_files)}")

    certificate_map = {}
    duplicate_certificates = []

    for pdf_file in pdf_files:
        certificate_name = pdf_file.stem

        if certificate_name in certificate_map:
            duplicate_certificates.append(pdf_file.name)
        else:
            certificate_map[certificate_name] = pdf_file

    if duplicate_certificates:
        print()
        print("WARNING: Duplicate certificate files:")

        for certificate in duplicate_certificates:
            print(f" - {certificate}")

    return certificate_map


def validate_recipients(df, certificate_map):
    print()
    print("========================================")
    print("VALIDATING RECIPIENTS")
    print("========================================")

    df["Name"] = df["Name"].fillna("").astype(str)
    df["Email"] = df["Email"].fillna("").astype(str)

    df["NormalizedEmail"] = df["Email"].apply(normalize_email)

    duplicate_names = (
        df[
            (df["Name"].duplicated(keep=False))
            & (df["Name"] != "")
        ]["Name"]
        .unique()
    )

    duplicate_emails = (
        df[
            (df["NormalizedEmail"].duplicated(keep=False))
            & (df["NormalizedEmail"] != "")
        ]["NormalizedEmail"]
        .unique()
    )

    if len(duplicate_names) > 0:
        print()
        print(
            f"WARNING: Duplicate recipient names: "
            f"{len(duplicate_names)}"
        )

        for name in duplicate_names:
            print(f" - {repr(name)}")

    if len(duplicate_emails) > 0:
        print()
        print(
            f"WARNING: Duplicate emails: "
            f"{len(duplicate_emails)}"
        )

        for email in duplicate_emails:
            print(f" - {email}")

    seen_recipient_pairs = set()

    ready_recipients = []
    duplicate_recipients = []
    invalid_recipients = []
    missing_certificate_recipients = []

    for index, row in df.iterrows():
        row_number = index + 2

        name = exact_name(row["Name"])
        email = normalize_email(row["Email"])

        recipient_info = {
            "row_number": row_number,
            "Name": name,
            "Email": email,
            "status": "",
            "reason": "",
            "certificate_path": None
        }

        if not is_valid_email(email):
            recipient_info["status"] = "SKIPPED"
            recipient_info["reason"] = "Invalid email"

            invalid_recipients.append(recipient_info)

            print()
            print("SKIPPED - Invalid email")
            print(f"Row: {row_number}")
            print(f"Name: {repr(name)}")
            print(f"Email: {repr(email)}")

            continue

        certificate_path = certificate_map.get(name)

        if certificate_path is None:
            recipient_info["status"] = "SKIPPED"
            recipient_info["reason"] = "Exact certificate not found"

            missing_certificate_recipients.append(
                recipient_info
            )

            print()
            print("SKIPPED - Exact certificate not found")
            print(f"Row: {row_number}")
            print(f"Name: {repr(name)}")
            print("Expected exact filename:")
            print(f"{name}.pdf")

            continue

        expected_filename = f"{name}.pdf"

        if certificate_path.name != expected_filename:
            recipient_info["status"] = "SKIPPED"
            recipient_info["reason"] = "Certificate filename mismatch"

            missing_certificate_recipients.append(
                recipient_info
            )

            print()
            print("BLOCKED - Certificate filename mismatch")
            print(f"Row: {row_number}")
            print(f"Name: {repr(name)}")
            print(f"Expected: {repr(expected_filename)}")
            print(f"Found:    {repr(certificate_path.name)}")

            continue

        recipient_pair = (name, email)

        if recipient_pair in seen_recipient_pairs:
            recipient_info["status"] = "DUPLICATE"
            recipient_info["reason"] = (
                "Duplicate Name + Email. "
                "Certificate already assigned to "
                "the first identical recipient row."
            )

            duplicate_recipients.append(recipient_info)

            print()
            print("BLOCKED - Duplicate recipient")
            print(f"Row: {row_number}")
            print(f"Name: {repr(name)}")
            print(f"Email: {email}")
            print(
                "Reason: Same Name + same Email "
                "already appeared earlier."
            )

            continue

        seen_recipient_pairs.add(recipient_pair)

        recipient_info["status"] = "READY"
        recipient_info["reason"] = (
            "Exact name + certificate match"
        )
        recipient_info["certificate_path"] = certificate_path

        ready_recipients.append(recipient_info)

    recipient_names = set(df["Name"].tolist())

    unmatched_certificates = []

    for certificate_name, certificate_path in certificate_map.items():
        if certificate_name not in recipient_names:
            unmatched_certificates.append(
                certificate_path.name
            )

    if unmatched_certificates:
        print()
        print("WARNING: Unmatched certificates:")

        for certificate in unmatched_certificates:
            print(f" - {certificate}")

    print()
    print("========================================")
    print("VALIDATION SUMMARY")
    print("========================================")

    print(f"Total recipients: {len(df)}")

    print(
        f"Ready to send: "
        f"{len(ready_recipients)}"
    )

    print(
        f"Duplicate recipients blocked: "
        f"{len(duplicate_recipients)}"
    )

    print(
        f"Invalid emails: "
        f"{len(invalid_recipients)}"
    )

    print(
        f"Missing certificates: "
        f"{len(missing_certificate_recipients)}"
    )

    print(
        f"Unmatched certificates: "
        f"{len(unmatched_certificates)}"
    )

    print(
        f"Duplicate recipient names: "
        f"{len(duplicate_names)}"
    )

    print(
        f"Duplicate emails: "
        f"{len(duplicate_emails)}"
    )

    print()
    print("========================================")
    print("SECURITY RULES")
    print("========================================")

    print("✓ Certificate matching: EXACT NAME")
    print("✓ Same Name + Different Email: ALLOWED")
    print("✓ Different Name + Same Email: ALLOWED")
    print(
        "✓ Same Name + Same Email: "
        "FIRST SEND / OTHERS BLOCKED"
    )
    print("✓ Duplicate Names: WARNING ONLY")
    print("✓ Duplicate Emails: WARNING ONLY")
    print("✓ Unmatched Certificates: WARNING ONLY")

    print("========================================")

    return {
        "ready_recipients": ready_recipients,
        "duplicate_recipients": duplicate_recipients,
        "invalid_recipients": invalid_recipients,
        "missing_certificate_recipients":
            missing_certificate_recipients,
        "invalid_email_count":
            len(invalid_recipients),
        "missing_certificate_count":
            len(missing_certificate_recipients),
        "duplicate_recipient_count":
            len(duplicate_recipients),
        "unmatched_certificates":
            unmatched_certificates,
        "duplicate_names":
            duplicate_names,
        "duplicate_emails":
            duplicate_emails
    }