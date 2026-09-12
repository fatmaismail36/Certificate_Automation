import pandas as pd


def save_log(log_file, rows):

    """
    Save sending results to CSV.

    If the log file already exists,
    append the new results to it.
    """

    if not rows:

        return

    new_log = pd.DataFrame(rows)

    if log_file.exists():

        try:

            old_log = pd.read_csv(
                log_file
            )

            new_log = pd.concat(
                [
                    old_log,
                    new_log
                ],
                ignore_index=True
            )

        except Exception:

            pass

    new_log.to_csv(
        log_file,
        index=False,
        encoding="utf-8-sig"
    )

    print()

    print(
        f"Log saved to: {log_file}"
    )


def get_sent_rows(log_file):

    """
    Return Excel row numbers that were successfully sent.

    IMPORTANT:

    We only consider SENT records.

    READY, FAILED and SKIPPED are NOT considered sent.
    """

    if not log_file.exists():

        return set()

    try:

        log_df = pd.read_csv(
            log_file
        )

    except Exception:

        return set()

    if log_df.empty:

        return set()

    if "status" not in log_df.columns:

        return set()

    if "row_number" not in log_df.columns:

        return set()

    sent_df = log_df[
        log_df["status"] == "SENT"
    ]

    sent_rows = set()

    for row_number in sent_df[
        "row_number"
    ]:

        try:

            sent_rows.add(
                int(row_number)
            )

        except (ValueError, TypeError):

            pass

    return sent_rows


def show_resume_status(
    log_file,
    total_recipients
):

    """
    Display how many recipients were already sent.
    """

    sent_rows = get_sent_rows(
        log_file
    )

    already_sent = len(
        sent_rows
    )

    remaining = (
        total_recipients
        - already_sent
    )

    print()

    print("========================================")

    print("RESUME STATUS")

    print("========================================")

    print(
        f"Already sent: {already_sent}"
    )

    print(
        f"Remaining: {remaining}"
    )

    return sent_rows