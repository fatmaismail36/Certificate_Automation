import time

import threading

from datetime import datetime

from pathlib import Path

from PySide6.QtCore import QThread, Signal

from logger import save_log

from email_sender import connect_to_smtp, send_with_retry


class EmailSenderWorker(QThread):

    """
    Background worker responsible for sending certificate emails.
    Runs in a separate QThread so the GUI remains responsive.
    """

    progress = Signal(
        int,
        int,
        str,
        str,
    )

    recipient_finished = Signal(
        str,
        str,
        str,
        str,
    )

    worker_finished = Signal(
        int,
        int,
        int,
        bool,
    )

    critical_error = Signal(
        str
    )

    def __init__(
        self,
        recipients,
        certificate_folder,
        log_file,
        smtp_server,
        smtp_port,
        smtp_email,
        smtp_password,
        subject,
        message,
        delay,
        retries,
        parent=None,
    ):
        super().__init__(parent)
        self.recipients = recipients
        self.certificate_folder = Path(
            certificate_folder
        )
        self.log_file = Path(
            log_file
        )
        self.smtp_server = smtp_server
        self.smtp_port = int(
            smtp_port
        )
        self.smtp_email = smtp_email
        self.smtp_password = smtp_password
        self.subject = subject
        self.message = message
        self.delay = max(
            float(delay),
            0,
        )
        self.retries = max(
            int(retries),
            0,
        )

        self.pause_event = threading.Event()
        self.pause_event.set()

        self.stop_event = threading.Event()

    def pause(self):
        """
        Pause the sending process.
        """
        self.pause_event.clear()

    def resume(self):
        """
        Resume the sending process.
        """
        self.pause_event.set()

    def stop(self):
        """
        Stop the sending process safely.
        """
        self.stop_event.set()
        self.pause_event.set()

    def write_log(
        self,
        name,
        email,
        certificate,
        status,
        error="",
    ):
        """
        Save one sending result to the CSV log.
        """
        row = {
            "name": name,
            "email": email,
            "certificate": certificate,
            "status": status,
            "timestamp": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "error": error,
        }

        save_log(
            self.log_file,
            [row],
        )

    def run(self):
        """
        Main background sending process.
        """
        smtp = None
        sent_count = 0
        failed_count = 0
        skipped_count = 0
        stopped = False

        try:
            try:
                smtp = connect_to_smtp(
                    self.smtp_server,
                    self.smtp_port,
                    self.smtp_email,
                    self.smtp_password,
                )

            except Exception as error:
                self.critical_error.emit(
                    "Could not connect to the SMTP server.\n\n"
                    f"{error}"
                )

                self.worker_finished.emit(
                    0,
                    0,
                    0,
                    True,
                )

                return

            total = len(
                self.recipients
            )

            for index, recipient in enumerate(
                self.recipients,
                start=1,
            ):
                if self.stop_event.is_set():
                    stopped = True
                    break

                self.pause_event.wait()

                if self.stop_event.is_set():
                    stopped = True
                    break

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

                certificate_path = recipient.get(
                    "certificate_path"
                )

                if not certificate_path:
                    certificate_path = (
                        self.certificate_folder
                        / certificate
                    )
                else:
                    certificate_path = Path(
                        certificate_path
                    )

                self.progress.emit(
                    index,
                    total,
                    name,
                    email,
                )

                if not certificate_path.exists():
                    error_message = (
                        "Certificate file not found: "
                        f"{certificate_path}"
                    )

                    self.write_log(
                        name=name,
                        email=email,
                        certificate=certificate,
                        status="FAILED",
                        error=error_message,
                    )

                    failed_count += 1

                    self.recipient_finished.emit(
                        name,
                        email,
                        "FAILED",
                        error_message,
                    )

                    continue

                success, error_message = send_with_retry(
                    smtp=smtp,
                    recipient=recipient,
                    certificate_path=certificate_path,
                    subject=self.subject,
                    message=self.message,
                    sender_email=self.smtp_email,
                    retries=self.retries,
                )

                if success:
                    sent_count += 1

                    self.write_log(
                        name=name,
                        email=email,
                        certificate=certificate,
                        status="SENT",
                        error="",
                    )

                    self.recipient_finished.emit(
                        name,
                        email,
                        "SENT",
                        "",
                    )

                else:
                    failed_count += 1

                    self.write_log(
                        name=name,
                        email=email,
                        certificate=certificate,
                        status="FAILED",
                        error=error_message,
                    )

                    self.recipient_finished.emit(
                        name,
                        email,
                        "FAILED",
                        error_message,
                    )

                if (
                    index < total
                    and self.delay > 0
                ):
                    remaining_delay = self.delay

                    while (
                        remaining_delay > 0
                        and not self.stop_event.is_set()
                    ):
                        self.pause_event.wait()

                        if self.stop_event.is_set():
                            stopped = True
                            break

                        sleep_time = min(
                            0.2,
                            remaining_delay,
                        )

                        time.sleep(
                            sleep_time
                        )

                        remaining_delay -= (
                            sleep_time
                        )

                    if self.stop_event.is_set():
                        stopped = True
                        break

        except Exception as error:
            self.critical_error.emit(
                "A critical error occurred during sending.\n\n"
                f"{error}"
            )

            stopped = True

        finally:
            if smtp is not None:
                try:
                    smtp.quit()
                except Exception:
                    pass

            self.worker_finished.emit(
                sent_count,
                failed_count,
                skipped_count,
                stopped,
            )