import re

import pandas as pd


def normalize_name(name):

    """
    Convert a name to a standard format
    so Excel names and PDF names can be compared.
    """

    if pd.isna(name):

        return ""

    name = str(name).strip().lower()

    name = re.sub(
        r"\s+",
        " ",
        name
    )

    return name


def normalize_email(email):

    """
    Convert email to lowercase and remove spaces.
    """

    if pd.isna(email):

        return ""

    return str(email).strip().lower()


def is_valid_email(email):

    """
    Basic email format validation.
    """

    if not email:

        return False

    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    return bool(
        re.match(
            pattern,
            email
        )
    )


def load_recipients(excel_file):

    print()

    print("========================================")

    print("LOADING EXCEL FILE")

    print("========================================")

    if not excel_file.exists():

        print(
            f"ERROR: Excel file not found:"
        )

        print(
            excel_file
        )

        return None

    try:

        df = pd.read_excel(
            excel_file
        )

    except Exception as error:

        print(
            f"ERROR reading Excel: {error}"
        )

        return None

    print(
        "Excel loaded successfully!"
    )

    print(
        f"Total rows: {len(df)}"
    )

    required_columns = [
        "Name",
        "Email"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        print()

        print(
            "ERROR: Missing required columns:"
        )

        for column in missing_columns:

            print(
                f" - {column}"
            )

        return None

    return df


def load_certificates(certificate_folder):

    print()

    print("========================================")

    print("LOADING CERTIFICATES")

    print("========================================")

    if not certificate_folder.exists():

        print(
            "ERROR: Certificate folder not found:"
        )

        print(
            certificate_folder
        )

        return {}

    pdf_files = list(
        certificate_folder.glob("*.pdf")
    )

    print(
        f"PDF certificates found: "
        f"{len(pdf_files)}"
    )

    certificate_map = {}

    duplicate_certificates = []

    for pdf_file in pdf_files:

        normalized_name = normalize_name(
            pdf_file.stem
        )

        if normalized_name in certificate_map:

            duplicate_certificates.append(
                pdf_file.name
            )

        else:

            certificate_map[
                normalized_name
            ] = pdf_file

    if duplicate_certificates:

        print()

        print(
            "WARNING: Duplicate certificate files:"
        )

        for certificate in duplicate_certificates:

            print(
                f" - {certificate}"
            )

    return certificate_map


def validate_recipients(
    df,
    certificate_map
):

    print()

    print("========================================")

    print("VALIDATING RECIPIENTS")

    print("========================================")

    df["Name"] = (
        df["Name"]
        .fillna("")
        .astype(str)
    )

    df["Email"] = (
        df["Email"]
        .fillna("")
        .astype(str)
    )

    df["NormalizedName"] = (
        df["Name"]
        .apply(normalize_name)
    )

    df["NormalizedEmail"] = (
        df["Email"]
        .apply(normalize_email)
    )

    duplicate_names = (
        df[
            (
                df["NormalizedName"]
                .duplicated(keep=False)
            )
            &
            (
                df["NormalizedName"] != ""
            )
        ]["NormalizedName"]
        .unique()
    )

    duplicate_emails = (
        df[
            (
                df["NormalizedEmail"]
                .duplicated(keep=False)
            )
            &
            (
                df["NormalizedEmail"] != ""
            )
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

            print(
                f" - {name}"
            )

    if len(duplicate_emails) > 0:

        print()

        print(
            f"WARNING: Duplicate emails: "
            f"{len(duplicate_emails)}"
        )

        for email in duplicate_emails:

            print(
                f" - {email}"
            )

    ready_recipients = []

    invalid_email_count = 0

    missing_certificate_count = 0

    for index, row in df.iterrows():

        name = str(
            row["Name"]
        ).strip()

        email = normalize_email(
            row["Email"]
        )

        normalized_name = normalize_name(
            name
        )

        if not is_valid_email(email):

            invalid_email_count += 1

            print()

            print(
                "SKIPPED - Invalid email"
            )

            print(
                f"Name: {name}"
            )

            print(
                f"Email: {email}"
            )

            continue

        certificate_path = certificate_map.get(
            normalized_name
        )

        if certificate_path is None:

            missing_certificate_count += 1

            print()

            print(
                "SKIPPED - Certificate not found"
            )

            print(
                f"Name: {name}"
            )

            print(
                f"Expected:"
            )

            print(
                f"{name}.pdf"
            )

            continue

        ready_recipients.append(
            {
                "row_number": index + 2,
                "Name": name,
                "Email": email,
                "certificate_path": certificate_path
            }
        )

    recipient_names = set(
        df["NormalizedName"]
        .tolist()
    )

    unmatched_certificates = []

    for (
        normalized_name,
        certificate_path
    ) in certificate_map.items():

        if normalized_name not in recipient_names:

            unmatched_certificates.append(
                certificate_path.name
            )

    if unmatched_certificates:

        print()

        print(
            "WARNING: Unmatched certificates:"
        )

        for certificate in unmatched_certificates:

            print(
                f" - {certificate}"
            )

    print()

    print("========================================")

    print("VALIDATION SUMMARY")

    print("========================================")

    print(
        f"Total recipients: {len(df)}"
    )

    print(
        f"Ready to send: "
        f"{len(ready_recipients)}"
    )

    print(
        f"Invalid emails: "
        f"{invalid_email_count}"
    )

    print(
        f"Missing certificates: "
        f"{missing_certificate_count}"
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

    return {
        "ready_recipients": ready_recipients,

        "invalid_email_count": invalid_email_count,

        "missing_certificate_count": (
            missing_certificate_count
        ),

        "unmatched_certificates": (
            unmatched_certificates
        ),

        "duplicate_names": duplicate_names,

        "duplicate_emails": duplicate_emails
    }