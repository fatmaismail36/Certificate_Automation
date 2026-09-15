from PySide6.QtCore import Qt

from PySide6.QtWidgets import (

    QCheckBox,

    QFrame,

    QGridLayout,

    QLabel,

    QLineEdit,

    QMessageBox,

    QPlainTextEdit,

    QPushButton,

    QSpinBox,

    QVBoxLayout,

    QHBoxLayout,

    QWidget,

)
from config import (

    DRY_RUN,

    EMAIL_DELAY,

    EMAIL_SUBJECT,

    SMTP_EMAIL,

    SMTP_PASSWORD,

    SMTP_PORT,

    SMTP_SERVER,

    TEST_LIMIT,

)


TEXT = "#2F4156"

MUTED = "#6B7280"

SECONDARY = "#C8D9E6"


DEFAULT_EMAIL_MESSAGE = """Dear {name},

Thank you for attending AFRIC 2026 and for being part of this successful event.

Please find attached your Certificate of Attendance for the conference.

We truly appreciate your participation and look forward to welcoming you again at future AFRIC events.

Best regards,

AFRIC 2026 Team"""


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
            f"""
            QLabel {{
                color: {TEXT};
                font-size: 25px;
                font-weight: 700;
            }}
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
                f"""
                QLabel {{
                    color: {MUTED};
                    font-size: 13px;
                }}
                """
            )
            layout.addWidget(
                subtitle_label
            )


class SettingsPage(QWidget):

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
                "Settings",
                "Configure SMTP and customize the certificate email.",
            )
        )

        settings_frame = QFrame()
        settings_frame.setObjectName(
            "contentCard"
        )
        form = QGridLayout(
            settings_frame
        )
        form.setContentsMargins(
            24,
            24,
            24,
            24,
        )
        form.setHorizontalSpacing(
            15
        )
        form.setVerticalSpacing(
            13
        )

        smtp_server_value = (
            self.app.get_saved_value(
                "smtp_server",
                SMTP_SERVER,
            )
        )
        smtp_port_value = (
            self.app.get_saved_value(
                "smtp_port",
                SMTP_PORT,
            )
        )
        smtp_email_value = (
            self.app.get_saved_value(
                "smtp_email",
                SMTP_EMAIL,
            )
        )
        subject_value = (
            self.app.get_saved_value(
                "email_subject",
                EMAIL_SUBJECT,
            )
        )
        message_value = (
            self.app.get_saved_value(
                "email_message",
                DEFAULT_EMAIL_MESSAGE,
            )
        )
        delay_value = (
            self.app.get_saved_value(
                "delay",
                EMAIL_DELAY,
            )
        )
        retry_value = (
            self.app.get_saved_value(
                "retries",
                3,
            )
        )
        test_mode_value = (
            self.app.get_saved_value(
                "test_mode",
                DRY_RUN,
            )
        )

        smtp_server_label = QLabel(
            "SMTP Server"
        )
        self.smtp_server_input = QLineEdit(
            str(
                smtp_server_value
            )
        )
        form.addWidget(
            smtp_server_label,
            0,
            0,
        )
        form.addWidget(
            self.smtp_server_input,
            0,
            1,
        )

        smtp_port_label = QLabel(
            "SMTP Port"
        )
        self.smtp_port_input = QSpinBox()
        self.smtp_port_input.setRange(
            1,
            65535,
        )
        self.smtp_port_input.setValue(
            int(
                smtp_port_value
            )
        )
        form.addWidget(
            smtp_port_label,
            1,
            0,
        )
        form.addWidget(
            self.smtp_port_input,
            1,
            1,
        )

        smtp_email_label = QLabel(
            "Sender Email"
        )
        self.smtp_email_input = QLineEdit(
            str(
                smtp_email_value
            )
        )
        form.addWidget(
            smtp_email_label,
            2,
            0,
        )
        form.addWidget(
            self.smtp_email_input,
            2,
            1,
        )

        smtp_password_label = QLabel(
            "SMTP Password"
        )
        self.smtp_password_input = QLineEdit()
        self.smtp_password_input.setEchoMode(
            QLineEdit.Password
        )
        self.smtp_password_input.setText(
            SMTP_PASSWORD
        )
        self.smtp_password_input.setPlaceholderText(
            "Enter SMTP password"
        )
        form.addWidget(
            smtp_password_label,
            3,
            0,
        )
        form.addWidget(
            self.smtp_password_input,
            3,
            1,
        )

        password_note = QLabel(
            "The SMTP password is used only during the current application session and is not saved in settings.json."
        )
        password_note.setWordWrap(
            True
        )
        password_note.setStyleSheet(
            f"""
            QLabel {{
                color: {MUTED};
                font-size: 11px;
            }}
            """
        )
        form.addWidget(
            password_note,
            4,
            1,
        )

        subject_label = QLabel(
            "Email Subject"
        )
        self.email_subject_input = QLineEdit(
            str(
                subject_value
            )
        )
        form.addWidget(
            subject_label,
            5,
            0,
        )
        form.addWidget(
            self.email_subject_input,
            5,
            1,
        )

        message_label = QLabel(
            "Email Message"
        )
        self.email_message_input = QPlainTextEdit(
            str(
                message_value
            )
        )
        self.email_message_input.setMinimumHeight(
            190
        )
        form.addWidget(
            message_label,
            6,
            0,
            Qt.AlignTop,
        )
        form.addWidget(
            self.email_message_input,
            6,
            1,
        )

        message_note = QLabel(
            "Use {name} to insert the recipient's exact name automatically."
        )
        message_note.setStyleSheet(
            f"""
            QLabel {{
                color: {MUTED};
                font-size: 11px;
            }}
            """
        )
        form.addWidget(
            message_note,
            7,
            1,
        )

        delay_label = QLabel(
            "Delay Between Emails"
        )
        self.delay_input = QSpinBox()
        self.delay_input.setRange(
            0,
            3600,
        )
        self.delay_input.setValue(
            max(
                int(delay_value),
                0,
            )
        )
        self.delay_input.setSuffix(
            " seconds"
        )
        form.addWidget(
            delay_label,
            8,
            0,
        )
        form.addWidget(
            self.delay_input,
            8,
            1,
        )

        retry_label = QLabel(
            "Retries"
        )
        self.retry_input = QSpinBox()
        self.retry_input.setRange(
            0,
            10,
        )
        self.retry_input.setValue(
            max(
                int(retry_value),
                0,
            )
        )
        form.addWidget(
            retry_label,
            9,
            0,
        )
        form.addWidget(
            self.retry_input,
            9,
            1,
        )

        self.test_mode_checkbox = QCheckBox(
            "Test Mode — send only a limited number of emails"
        )
        self.test_mode_checkbox.setChecked(
            bool(
                test_mode_value
            )
        )
        self.test_mode_checkbox.setToolTip(
            f"Test Mode sends only the first {TEST_LIMIT} validated recipient(s)."
        )
        form.addWidget(
            self.test_mode_checkbox,
            10,
            0,
            1,
            2,
        )

        test_limit_label = QLabel(
            f"Current Test Limit: {TEST_LIMIT} recipient(s)"
        )
        test_limit_label.setStyleSheet(
            f"""
            QLabel {{
                color: {MUTED};
                font-size: 11px;
            }}
            """
        )
        form.addWidget(
            test_limit_label,
            11,
            0,
            1,
            2,
        )

        buttons_layout = QHBoxLayout()
        preview_button = QPushButton(
            "Preview Email"
        )
        preview_button.setProperty(
            "class",
            "secondary",
        )
        preview_button.clicked.connect(
            self.preview_email
        )
        buttons_layout.addWidget(
            preview_button
        )

        save_button = QPushButton(
            "Save Settings"
        )
        save_button.clicked.connect(
            self.save_settings
        )
        buttons_layout.addWidget(
            save_button
        )

        buttons_layout.addStretch()
        form.addLayout(
            buttons_layout,
            12,
            0,
            1,
            2,
        )

        layout.addWidget(
            settings_frame
        )
        layout.addStretch()

    def preview_email(self):
        subject = (
            self.email_subject_input
            .text()
            .strip()
        )
        message = (
            self.email_message_input
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

    def save_settings(self):
        server = (
            self.smtp_server_input
            .text()
            .strip()
        )
        port = (
            self.smtp_port_input
            .value()
        )
        email = (
            self.smtp_email_input
            .text()
            .strip()
        )
        password = (
            self.smtp_password_input
            .text()
        )
        subject = (
            self.email_subject_input
            .text()
            .strip()
        )
        message = (
            self.email_message_input
            .toPlainText()
        )
        delay = (
            self.delay_input
            .value()
        )
        retries = (
            self.retry_input
            .value()
        )
        test_mode = (
            self.test_mode_checkbox
            .isChecked()
        )

        if not server:
            QMessageBox.warning(
                self,
                "Invalid Settings",
                "SMTP server cannot be empty.",
            )
            return

        if not email:
            QMessageBox.warning(
                self,
                "Invalid Settings",
                "SMTP email cannot be empty.",
            )
            return

        if not password:
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

        settings = {
            "smtp_server": server,
            "smtp_port": port,
            "smtp_email": email,
            "email_subject": subject,
            "email_message": message,
            "delay": delay,
            "retries": retries,
            "test_mode": test_mode,
        }

        try:
            self.app.save_settings_to_file(
                settings
            )
            self.app.saved_settings = {
                **settings,
                "smtp_password": password,
            }

            QMessageBox.information(
                self,
                "Settings Saved",
                (
                    "Settings have been saved successfully.\n\n"
                    "The selected subject and message will be used "
                    "for the next sending process."
                ),
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Save Error",
                (
                    "Could not save settings.\n\n"
                    f"{error}"
                ),
            )

    def refresh(self):
        """
        Settings are loaded when the page is created.
        Nothing is required here currently.
        """
        pass