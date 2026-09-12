from config import (
    EXCEL_FILE,
    CERTIFICATE_FOLDER,
    LOG_FILE,
    DRY_RUN,
    TEST_LIMIT
)

from validator import (
    load_recipients,
    load_certificates,
    validate_recipients
)

from email_sender import (
    run_dry_run,
    send_batch
)

from logger import (
    save_log,
    show_resume_status
)


def main():

    print()

    print("========================================")

    print("CERTIFICATE SENDER")

    print("========================================")

    print(
        f"Excel file: {EXCEL_FILE}"
    )

    print(
        f"Certificate folder: "
        f"{CERTIFICATE_FOLDER}"
    )

    print(
        f"Dry Run: {DRY_RUN}"
    )

    print(
        f"Test Limit: {TEST_LIMIT}"
    )

    df = load_recipients(
        EXCEL_FILE
    )

    if df is None:

        print()

        print(
            "Program stopped."
        )

        return

    certificate_map = load_certificates(
        CERTIFICATE_FOLDER
    )

    if not certificate_map:

        print()

        print(
            "ERROR: No certificates found."
        )

        return

    result = validate_recipients(
        df,
        certificate_map
    )

    ready_recipients = (
        result["ready_recipients"]
    )

    if not ready_recipients:

        print()

        print(
            "No recipients are ready."
        )

        return

    already_sent_rows = show_resume_status(
        LOG_FILE,
        len(ready_recipients)
    )

    if DRY_RUN:

        (
            processed_count,
            log_rows
        ) = run_dry_run(
            ready_recipients
        )

        save_log(
            LOG_FILE,
            log_rows
        )

        print()

        print("========================================")

        print("DRY RUN SUMMARY")

        print("========================================")

        print(
            f"Emails prepared: "
            f"{processed_count}"
        )

        print(
            "No real emails were sent."
        )

    else:

        (
            sent_count,
            failed_count,
            skipped_count,
            log_rows
        ) = send_batch(
            ready_recipients,
            already_sent_rows
        )

        save_log(
            LOG_FILE,
            log_rows
        )

        print()

        print("========================================")

        print("SENDING SUMMARY")

        print("========================================")

        print(
            f"Sent: {sent_count}"
        )

        print(
            f"Failed: {failed_count}"
        )

        print(
            f"Already sent / skipped: "
            f"{skipped_count}"
        )

    print()

    print("========================================")

    print("PROGRAM FINISHED")

    print("========================================")


if __name__ == "__main__":

    main()