from pathlib import Path

from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config import (
    DRY_RUN,
    EMAIL_DELAY,
    EMAIL_SUBJECT,
    LOG_FILE,
    SMTP_EMAIL,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_SERVER,
    TEST_LIMIT,
)

from validator import (
    load_certificates,
    load_recipients,
    validate_recipients,
)

from logger import get_sent_recipients


class PageTitle(QWidget):
    def __init__(
        self,
        title,
        subtitle="",
        parent=None,
    ):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            0,
            0,
            0,
            10,
        )
        layout.setSpacing(4)
        title_label = QLabel(title)
        title_label.setStyleSheet(
            """
            QLabel {
                font-size: 25px;
                font-weight: 700;
            }
            """
        )
        layout.addWidget(
            title_label
        )
        if subtitle:
            subtitle_label = QLabel(
                subtitle
            )
            subtitle_label.setStyleSheet(
                """
                QLabel {
                    font-size: 13px;
                }
                """
            )
            layout.addWidget(
                subtitle_label
            )


class SendPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            30,
            28,
            30,
            28,
        )
        layout.setSpacing(18)
        layout.addWidget(
            PageTitle(
                "Send Certificates",
                "Validate your files, review the email, then start distribution.",
            )
        )
        files_card = QFrame()
        files_card.setObjectName(
            "contentCard"
        )
        files_layout = QFormLayout(
            files_card
        )
        files_layout.setContentsMargins(
            20,
            20,
            20,
            20,
        )
        self.excel_input = QLineEdit()
        self.excel_input.setReadOnly(
            True
        )
        excel_browse = QPushButton(
            "Browse"
        )
        excel_browse.clicked.connect(
            self.select_excel
        )
        excel_container = QHBoxLayout()
        excel_container.addWidget(
            self.excel_input,
            1,
        )
        excel_container.addWidget(
            excel_browse
        )
        files_layout.addRow(
            "Recipients Excel:",
            excel_container,
        )
        self.send_certificate_input = QLineEdit()
        self.send_certificate_input.setReadOnly(
            True
        )
        certificate_browse = QPushButton(
            "Browse"
        )
        certificate_browse.clicked.connect(
            self.select_certificate_folder
        )
        certificate_container = QHBoxLayout()
        certificate_container.addWidget(
            self.send_certificate_input,
            1,
        )
        certificate_container.addWidget(
            certificate_browse
        )
        files_layout.addRow(
            "Certificate Folder:",
            certificate_container,
        )
        layout.addWidget(
            files_card
        )
        validation_card = QFrame()
        validation_card.setObjectName(
            "contentCard"
        )
        validation_layout = QVBoxLayout(
            validation_card
        )
        validation_layout.setContentsMargins(
            20,
            18,
            20,
            18,
        )
        self.validate_button = QPushButton(
            "Validate Files"
        )
        self.validate_button.clicked.connect(
            self.validate_files
        )
        validation_layout.addWidget(
            self.validate_button,
            alignment=Qt.AlignLeft,
        )
        self.send_validation_label = QLabel(
            "Please validate before sending."
        )
        self.send_validation_label.setWordWrap(
            True
        )
        validation_layout.addWidget(
            self.send_validation_label
        )
        layout.addWidget(
            validation_card
        )
        sending_card = QFrame()
        sending_card.setObjectName(
            "contentCard"
        )
        sending_layout = QVBoxLayout(
            sending_card
        )
        sending_layout.setContentsMargins(
            20,
            18,
            20,
            18,
        )
        progress_title = QLabel(
            "Sending Progress"
        )
        progress_title.setStyleSheet(
            """
            QLabel {
                font-size: 16px;
                font-weight: 700;
            }
            """
        )
        sending_layout.addWidget(
            progress_title
        )
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(
            0
        )
        self.progress_bar.setMaximum(
            1
        )
        self.progress_bar.setValue(
            0
        )
        sending_layout.addWidget(
            self.progress_bar
        )
        self.current_recipient_label = QLabel(
            "Waiting to start..."
        )
        sending_layout.addWidget(
            self.current_recipient_label
        )
        buttons = QHBoxLayout()
        self.start_button = QPushButton(
            "Start Sending"
        )
        self.start_button.setProperty(
            "class",
            "success",
        )
        self.start_button.clicked.connect(
            self.start_sending
        )
        buttons.addWidget(
            self.start_button
        )
        self.pause_button = QPushButton(
            "Pause"
        )
        self.pause_button.clicked.connect(
            self.toggle_pause
        )
        self.pause_button.setEnabled(
            False
        )
        buttons.addWidget(
            self.pause_button
        )
        self.stop_button = QPushButton(
            "Stop"
        )
        self.stop_button.setProperty(
            "class",
            "danger",
        )
        self.stop_button.clicked.connect(
            self.stop_sending
        )
        self.stop_button.setEnabled(
            False
        )
        buttons.addWidget(
            self.stop_button
        )
        buttons.addStretch()
        sending_layout.addLayout(
            buttons
        )
        layout.addWidget(
            sending_card
        )
        layout.addStretch()

    def select_excel(self):
        if self.app.is_sending:
            return
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Recipients Excel File",
            "",
            "Excel Files (*.xlsx *.xls)",
        )
        if not file_path:
            return
        self.app.excel_file = Path(
            file_path
        )
        self.excel_input.setText(
            str(
                self.app.excel_file
            )
        )
        self.invalidate_previous_validation()
        self.app.dashboard_page.update_dashboard()

    def select_certificate_folder(self):
        if self.app.is_sending:
            return
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Certificate Folder",
        )
        if not folder_path:
            return
        self.app.certificate_folder = Path(
            folder_path
        )
        folder_text = str(
            self.app.certificate_folder
        )
        self.send_certificate_input.setText(
            folder_text
        )
        self.app.certificates_page.certificate_folder_input.setText(
            folder_text
        )
        self.invalidate_previous_validation()
        self.app.dashboard_page.update_dashboard()

    def invalidate_previous_validation(self):
        if self.app.is_sending:
            return
        self.app.validation_result = None
        self.app.ready_recipients = []
        self.start_button.setEnabled(
            False
        )
        self.send_validation_label.setText(
            "Files changed. Please validate again."
        )
        self.app.dashboard_page.dashboard_validation_label.setText(
            "Files changed. Please validate again."
        )

    def validate_files(self):
        if self.app.is_sending:
            return
        try:
            if not self.app.excel_file.exists():
                QMessageBox.warning(
                    self,
                    "Excel File Not Found",
                    (
                        "The selected Excel file does not exist:\n\n"
                        f"{self.app.excel_file}"
                    ),
                )
                return
            if not self.app.certificate_folder.exists():
                QMessageBox.warning(
                    self,
                    "Certificate Folder Not Found",
                    (
                        "The selected certificate folder does not exist:\n\n"
                        f"{self.app.certificate_folder}"
                    ),
                )
                return
            self.app.recipients_df = load_recipients(
                self.app.excel_file
            )
            if self.app.recipients_df is None:
                QMessageBox.critical(
                    self,
                    "Validation Error",
                    (
                        "The Excel file could not be loaded "
                        "or is missing required columns."
                    ),
                )
                return
            self.app.certificate_map = load_certificates(
                self.app.certificate_folder
            )
            self.app.validation_result = validate_recipients(
                self.app.recipients_df,
                self.app.certificate_map,
            )
            self.app.ready_recipients = (
                self.app.validation_result.get(
                    "ready_recipients",
                    [],
                )
            )
            self.app.already_sent = (
                get_sent_recipients(
                    self.app.log_file
                )
            )
            remaining = 0
            for recipient in self.app.ready_recipients:
                key = self.recipient_key(
                    recipient
                )
                if key not in self.app.already_sent:
                    remaining += 1
            total = len(
                self.app.recipients_df
            )
            invalid_count = (
                self.app.validation_result.get(
                    "invalid_email_count",
                    0,
                )
            )
            missing_count = (
                self.app.validation_result.get(
                    "missing_certificate_count",
                    0,
                )
            )
            duplicate_count = (
                self.app.validation_result.get(
                    "duplicate_recipient_count",
                    0,
                )
            )
            unmatched_count = len(
                self.app.validation_result.get(
                    "unmatched_certificates",
                    [],
                )
            )
            duplicate_names = len(
                self.app.validation_result.get(
                    "duplicate_names",
                    [],
                )
            )
            duplicate_emails = len(
                self.app.validation_result.get(
                    "duplicate_emails",
                    [],
                )
            )
            already_sent_count = (
                len(
                    self.app.ready_recipients
                )
                - remaining
            )
            self.app.dashboard_page.update_dashboard()
            self.app.recipients_page.load_recipients_table()
            self.app.certificates_page.load_certificates_table()
            validation_text = (
                "Validation completed successfully."
                "<br><br>"
                f"<b>Total recipients:</b> {total}<br>"
                f"<b>Ready to send:</b> "
                f"{len(self.app.ready_recipients)}<br>"
                f"<b>Already sent:</b> "
                f"{already_sent_count}<br>"
                f"<b>Remaining:</b> {remaining}<br>"
                f"<b>Invalid emails:</b> "
                f"{invalid_count}<br>"
                f"<b>Missing certificates:</b> "
                f"{missing_count}<br>"
                f"<b>Duplicate recipient rows:</b> "
                f"{duplicate_count}<br>"
                f"<b>Duplicate names:</b> "
                f"{duplicate_names}<br>"
                f"<b>Duplicate emails:</b> "
                f"{duplicate_emails}<br>"
                f"<b>Unmatched certificates:</b> "
                f"{unmatched_count}"
            )
            self.send_validation_label.setText(
                validation_text
            )
            self.app.dashboard_page.dashboard_validation_label.setText(
                (
                    "Validation completed. "
                    f"{remaining} recipient(s) are ready for sending."
                )
            )
            self.start_button.setEnabled(
                remaining > 0
            )
            QMessageBox.information(
                self,
                "Validation Complete",
                (
                    "Validation completed successfully.\n\n"
                    f"Total recipients: {total}\n"
                    f"Ready to send: "
                    f"{len(self.app.ready_recipients)}\n"
                    f"Already sent: {already_sent_count}\n"
                    f"Remaining: {remaining}\n"
                    f"Invalid emails: {invalid_count}\n"
                    f"Missing certificates: {missing_count}\n"
                    f"Duplicate recipient rows: "
                    f"{duplicate_count}\n"
                    f"Duplicate names: {duplicate_names}\n"
                    f"Duplicate emails: {duplicate_emails}\n"
                    f"Unmatched certificates: "
                    f"{unmatched_count}"
                ),
            )
        except Exception as error:
            QMessageBox.critical(
                self,
                "Validation Error",
                (
                    "An error occurred during validation.\n\n"
                    f"{error}"
                ),
            )

    def prepare_recipient_for_sending(
        self,
        recipient,
    ):
        name = str(
            recipient.get(
                "Name",
                "",
            )
        )
        email = str(
            recipient.get(
                "Email",
                "",
            )
        ).strip().lower()
        certificate_path = recipient.get(
            "certificate_path"
        )
        certificate = (
            Path(
                certificate_path
            ).name
            if certificate_path
            else ""
        )
        return {
            "name": name,
            "email": email,
            "certificate": certificate,
            "certificate_path": certificate_path,
            "row_number": recipient.get(
                "row_number"
            ),
        }

    def recipient_key(
        self,
        recipient,
    ):
        name = str(
            recipient.get(
                "Name",
                recipient.get(
                    "name",
                    "",
                ),
            )
        )
        email = str(
            recipient.get(
                "Email",
                recipient.get(
                    "email",
                    "",
                ),
            )
        ).strip().lower()
        certificate_path = recipient.get(
            "certificate_path"
        )
        if certificate_path:
            certificate = Path(
                certificate_path
            ).name
        else:
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

    def preview_email(self):
        subject = (
            self.app.settings_page
            .email_subject_input
            .text()
            .strip()
        )
        message = (
            self.app.settings_page
            .email_message_input
            .toPlainText()
        )
        if not subject:
            QMessageBox.warning(
                self,
                "Invalid Subject",
                "Email subject cannot be empty.",
            )
            return
        if not message.strip():
            QMessageBox.warning(
                self,
                "Invalid Message",
                "Email message cannot be empty.",
            )
            return
        preview_name = "Recipient"
        if self.app.ready_recipients:
            preview_name = str(
                self.app.ready_recipients[0].get(
                    "Name",
                    "Recipient",
                )
            )
        preview_message = message.replace(
            "{name}",
            preview_name,
        )
        QMessageBox.information(
            self,
            "Email Preview",
            (
                f"Subject:\n{subject}\n\n"
                "Message:\n"
                f"{preview_message}"
            ),
        )

    def start_sending(self):
        if self.app.is_sending:
            return
        if not self.app.validation_result:
            QMessageBox.warning(
                self,
                "Validation Required",
                "Please validate the files before sending.",
            )
            return
        self.app.already_sent = (
            get_sent_recipients(
                self.app.log_file
            )
        )
        remaining = []
        for recipient in self.app.ready_recipients:
            key = self.recipient_key(
                recipient
            )
            if key not in self.app.already_sent:
                remaining.append(
                    recipient
                )
        if not remaining:
            QMessageBox.information(
                self,
                "Already Completed",
                "All validated certificates have already been sent.",
            )
            return
        settings_page = (
            self.app.settings_page
        )
        smtp_server = (
            settings_page
            .smtp_server_input
            .text()
            .strip()
        )
        smtp_port = (
            settings_page
            .smtp_port_input
            .value()
        )
        smtp_email = (
            settings_page
            .smtp_email_input
            .text()
            .strip()
        )
        smtp_password = (
            settings_page
            .smtp_password_input
            .text()
        )
        subject = (
            settings_page
            .email_subject_input
            .text()
            .strip()
        )
        message = (
            settings_page
            .email_message_input
            .toPlainText()
        )
        delay = (
            settings_page
            .delay_input
            .value()
        )
        retries = (
            settings_page
            .retry_input
            .value()
        )
        if not smtp_server:
            QMessageBox.warning(
                self,
                "Invalid Settings",
                "SMTP server cannot be empty.",
            )
            return
        if not smtp_email:
            QMessageBox.warning(
                self,
                "Invalid Settings",
                "SMTP email cannot be empty.",
            )
            return
        if not smtp_password:
            QMessageBox.warning(
                self,
                "Invalid Settings",
                "SMTP password cannot be empty.",
            )
            return
        if not subject:
            QMessageBox.warning(
                self,
                "Invalid Settings",
                "Email subject cannot be empty.",
            )
            return
        if not message.strip():
            QMessageBox.warning(
                self,
                "Invalid Settings",
                "Email message cannot be empty.",
            )
            return
        sending_list = [
            self.prepare_recipient_for_sending(
                recipient
            )
            for recipient in remaining
        ]
        test_mode = (
            settings_page
            .test_mode_checkbox
            .isChecked()
        )
        if test_mode:
            sending_list = sending_list[
                :TEST_LIMIT
            ]
            mode_text = (
                "TEST MODE\n"
                f"Only {len(sending_list)} email(s) will be sent."
            )
        else:
            production_answer = QMessageBox.warning(
                self,
                "Production Sending Warning",
                (
                    "You are about to send real emails.\n\n"
                    f"Recipients: {len(sending_list)}\n\n"
                    "This will send certificates to the selected "
                    "recipients using the current email subject "
                    "and message.\n\n"
                    "Are you sure you want to continue?"
                ),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if production_answer != QMessageBox.Yes:
                return
            mode_text = (
                "PRODUCTION MODE\n"
                f"{len(sending_list)} email(s) will be sent."
            )
        preview_name = "Recipient"
        if sending_list:
            preview_name = str(
                sending_list[0].get(
                    "name",
                    "Recipient",
                )
            )
        preview_message = message.replace(
            "{name}",
            preview_name,
        )
        answer = QMessageBox.question(
            self,
            "Confirm Sending",
            (
                f"{mode_text}\n\n"
                f"Subject:\n{subject}\n\n"
                f"Message Preview:\n{preview_message}\n\n"
                f"SMTP:\n"
                f"{smtp_server}:{smtp_port}\n\n"
                f"Delay:\n"
                f"{delay} seconds\n\n"
                f"Retries:\n"
                f"{retries}\n\n"
                "Do you want to continue?"
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        self.progress_bar.setMaximum(
            len(sending_list)
        )
        self.progress_bar.setValue(
            0
        )
        self.current_recipient_label.setText(
            "Connecting to SMTP server..."
        )
        self.app.is_sending = True
        self.app.critical_error_occurred = False
        self.set_controls_for_sending(
            True
        )
        self.pause_button.setText(
            "Pause"
        )
        from email_worker import EmailSenderWorker
        self.app.worker = EmailSenderWorker(
            recipients=sending_list,
            certificate_folder=self.app.certificate_folder,
            log_file=self.app.log_file,
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            smtp_email=smtp_email,
            smtp_password=smtp_password,
            subject=subject,
            message=message,
            delay=delay,
            retries=retries,
        )
        self.app.worker.progress.connect(
            self.on_sending_progress
        )
        self.app.worker.recipient_finished.connect(
            self.on_recipient_finished
        )
        self.app.worker.worker_finished.connect(
            self.on_sending_finished
        )
        self.app.worker.critical_error.connect(
            self.on_critical_error
        )
        self.app.worker.start()

    def set_controls_for_sending(
        self,
        sending,
    ):
        self.start_button.setEnabled(
            not sending
        )
        self.validate_button.setEnabled(
            not sending
        )
        self.app.dashboard_page.dashboard_validation_button.setEnabled(
            not sending
        )
        self.pause_button.setEnabled(
            sending
        )
        self.stop_button.setEnabled(
            sending
        )
        for button in self.app.nav_buttons:
            button.setEnabled(
                not sending
            )
        self.excel_input.setEnabled(
            not sending
        )
        self.send_certificate_input.setEnabled(
            not sending
        )
        settings_page = (
            self.app.settings_page
        )
        settings_page.smtp_server_input.setEnabled(
            not sending
        )
        settings_page.smtp_port_input.setEnabled(
            not sending
        )
        settings_page.smtp_email_input.setEnabled(
            not sending
        )
        settings_page.smtp_password_input.setEnabled(
            not sending
        )
        settings_page.email_subject_input.setEnabled(
            not sending
        )
        settings_page.email_message_input.setEnabled(
            not sending
        )
        settings_page.delay_input.setEnabled(
            not sending
        )
        settings_page.retry_input.setEnabled(
            not sending
        )
        settings_page.test_mode_checkbox.setEnabled(
            not sending
        )

    def toggle_pause(self):
        if not self.app.worker:
            return
        if not self.app.is_sending:
            return
        if self.pause_button.text() == "Pause":
            self.app.worker.pause()
            self.pause_button.setText(
                "Resume"
            )
            self.current_recipient_label.setText(
                "Sending paused."
            )
        else:
            self.app.worker.resume()
            self.pause_button.setText(
                "Pause"
            )
            self.current_recipient_label.setText(
                "Sending resumed."
            )

    def stop_sending(self):
        if not self.app.worker:
            return
        if not self.app.is_sending:
            return
        answer = QMessageBox.question(
            self,
            "Stop Sending",
            (
                "Are you sure you want to stop "
                "the sending process?\n\n"
                "Emails that were already sent will "
                "remain recorded and will not be sent again."
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        self.current_recipient_label.setText(
            "Stopping safely..."
        )
        self.app.worker.stop()
        self.pause_button.setEnabled(
            False
        )
        self.stop_button.setEnabled(
            False
        )

    def on_sending_progress(
        self,
        current,
        total,
        name,
        email,
    ):
        self.progress_bar.setMaximum(
            total
        )
        self.progress_bar.setValue(
            current
        )
        self.current_recipient_label.setText(
            f"Sending {current} of {total}: "
            f"{name} — {email}"
        )

    def on_recipient_finished(
        self,
        name,
        email,
        status,
        error,
    ):
        if status == "SENT":
            self.current_recipient_label.setText(
                f"Sent successfully: "
                f"{name} — {email}"
            )
        else:
            self.current_recipient_label.setText(
                f"Failed: "
                f"{name} — {email}"
            )
        self.app.logs_page.load_logs_table()
        self.app.dashboard_page.update_dashboard()

    def on_critical_error(
        self,
        message,
    ):
        self.app.critical_error_occurred = True
        self.current_recipient_label.setText(
            "Critical error occurred."
        )
        QMessageBox.critical(
            self,
            "Critical Sending Error",
            message,
        )

    def on_sending_finished(
        self,
        sent_count,
        failed_count,
        skipped_count,
        stopped,
    ):
        self.app.is_sending = False
        self.set_controls_for_sending(
            False
        )
        self.pause_button.setText(
            "Pause"
        )
        self.app.already_sent = (
            get_sent_recipients(
                self.app.log_file
            )
        )
        self.app.logs_page.load_logs_table()
        self.app.dashboard_page.update_dashboard()
        self.app.recipients_page.load_recipients_table()
        if self.app.validation_result:
            remaining = 0
            for recipient in self.app.ready_recipients:
                if (
                    self.recipient_key(
                        recipient
                    )
                    not in self.app.already_sent
                ):
                    remaining += 1
            self.start_button.setEnabled(
                remaining > 0
            )
        if not stopped:
            self.progress_bar.setValue(
                self.progress_bar.maximum()
            )
        if stopped:
            self.current_recipient_label.setText(
                "Sending stopped safely."
            )
            if not self.app.critical_error_occurred:
                QMessageBox.information(
                    self,
                    "Sending Stopped",
                    (
                        "The sending process was stopped safely.\n\n"
                        f"Successfully sent: {sent_count}\n"
                        f"Failed: {failed_count}\n\n"
                        "You can continue later. "
                        "Already sent recipients will not be sent again."
                    ),
                )
        else:
            self.current_recipient_label.setText(
                "Sending process completed."
            )
            QMessageBox.information(
                self,
                "Sending Completed",
                (
                    "Certificate sending completed.\n\n"
                    f"Successfully sent: {sent_count}\n"
                    f"Failed: {failed_count}\n"
                    f"Skipped: {skipped_count}"
                ),
            )
        if self.app.worker:
            self.app.worker.deleteLater()
            self.app.worker = None

    def refresh(self):
        pass