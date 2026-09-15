from pathlib import Path

import pandas as pd


def save_log(log_file, rows):
    """
    Append new log records to the CSV file.
    """
    if not rows:
        return

    log_file = Path(log_file)
    log_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    new_data = pd.DataFrame(rows)

    if log_file.exists():
        try:
            existing_data = pd.read_csv(
                log_file
            )
            combined_data = pd.concat(
                [existing_data, new_data],
                ignore_index=True
            )
        except Exception:
            combined_data = new_data
    else:
        combined_data = new_data

    combined_data.to_csv(
        log_file,
        index=False
    )


def get_sent_recipients(log_file):
    """
    Return recipients that were successfully sent.

    Identity is based on:
        Name + Email + Certificate

    NOT only row_number.
    This makes resume safer if the Excel rows move.
    """
    log_file = Path(log_file)

    if not log_file.exists():
        return set()

    try:
        df = pd.read_csv(log_file)
    except Exception:
        return set()

    if df.empty:
        return set()

    required_columns = [
        "name",
        "email",
        "certificate",
        "status"
    ]

    for column in required_columns:
        if column not in df.columns:
            return set()

    sent_df = df[
        df["status"]
        .astype(str)
        .str.upper()
        .eq("SENT")
    ]

    sent_recipients = set()

    for _, row in sent_df.iterrows():
        name = str(
            row["name"]
        )
        email = str(
            row["email"]
        ).strip().lower()
        certificate = str(
            row["certificate"]
        )

        sent_recipients.add(
            (
                name,
                email,
                certificate
            )
        )

    return sent_recipients


def is_already_sent(
    log_file,
    name,
    email,
    certificate
):
    """
    Check whether this exact recipient +
    certificate combination was already sent.
    """
    sent_recipients = get_sent_recipients(
        log_file
    )

    key = (
        name,
        str(email).strip().lower(),
        certificate
    )

    return key in sent_recipients


def show_resume_status(
    log_file,
    total_recipients
):
    """
    Show sending resume information.
    """
    sent_recipients = get_sent_recipients(
        log_file
    )

    sent_count = len(sent_recipients)

    remaining = max(
        total_recipients - sent_count,
        0
    )

    print()
    print("========================================")
    print("RESUME STATUS")
    print("========================================")
    print(
        f"Already sent: {sent_count}"
    )
    print(
        f"Remaining: {remaining}"
    )

    return sent_recipients