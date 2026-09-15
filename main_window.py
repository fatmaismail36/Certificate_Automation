import sys

import json

from pathlib import Path

import pandas as pd

from PySide6.QtCore import Qt

from PySide6.QtGui import QFont

from PySide6.QtWidgets import (

    QApplication,

    QFrame,

    QHBoxLayout,

    QLabel,

    QMainWindow,

    QMessageBox,

    QPushButton,

    QStackedWidget,

    QVBoxLayout,

    QWidget,

)

from config import (

    CERTIFICATE_FOLDER,

    LOG_FILE,

    SMTP_SERVER,

    SMTP_PORT,

    SMTP_EMAIL,

    SMTP_PASSWORD,

    EMAIL_SUBJECT,

    EMAIL_DELAY,

    DRY_RUN,

)

from validator import (

    load_recipients,

    load_certificates,

    validate_recipients,

)

from logger import get_sent_recipients

from email_worker import EmailSenderWorker

from UI.dashboard import DashboardPage

from UI.recipients_page import RecipientsPage

from UI.certificates_page import CertificatesPage

from UI.send_page import SendPage

from UI.logs_page import LogsPage

from UI.settings_page import SettingsPage


BG = "#F5EFEB"

SIDEBAR = "#2F4156"

PRIMARY = "#567C8D"

SECONDARY = "#C8D9E6"

WHITE = "#FFFFFF"

TEXT = "#2F4156"

MUTED = "#6B7280"

SUCCESS = "#2E7D32"

WARNING = "#B7791F"

DANGER = "#C62828"

BORDER = "#D7DEE5"


SETTINGS_FILE = Path(
    "data/settings.json"
)


DEFAULT_EMAIL_MESSAGE = """Dear {name},

Thank you for attending AFRIC 2026 and for being part of this successful event.

Please find attached your Certificate of Attendance for the conference.

We truly appreciate your participation and look forward to welcoming you again at future AFRIC events.

Best regards,

AFRIC 2026 Team"""


class CertificateAutomationApp(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "AFRIC 2026 Certificate Automation"
        )
        self.resize(
            1450,
            900,
        )
        self.setMinimumSize(
            1100,
            700,
        )

        self.recipients_df = None
        self.certificate_map = {}
        self.validation_result = None
        self.ready_recipients = []
        self.already_sent = set()
        self.excel_file = Path(
            "data/recipients.xlsx"
        )
        self.certificate_folder = Path(
            CERTIFICATE_FOLDER
        )
        self.log_file = Path(
            LOG_FILE
        )
        self.worker = None
        self.is_sending = False
        self.current_page = "dashboard"
        self.critical_error_occurred = False
        self.saved_settings = {}

        self.load_saved_settings()

        self.build_ui()

        self.refresh_all()

    def load_saved_settings(self):

        if not SETTINGS_FILE.exists():
            self.saved_settings = {}
            return

        try:
            with open(
                SETTINGS_FILE,
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

            if isinstance(
                data,
                dict,
            ):
                self.saved_settings = data
            else:
                self.saved_settings = {}

        except Exception:
            self.saved_settings = {}

    def save_settings_to_file(
        self,
        settings,
    ):

        SETTINGS_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        safe_settings = dict(
            settings
        )

        safe_settings.pop(
            "smtp_password",
            None,
        )

        with open(
            SETTINGS_FILE,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                safe_settings,
                file,
                indent=4,
                ensure_ascii=False,
            )

    def get_saved_value(
        self,
        key,
        default=None,
    ):

        return self.saved_settings.get(
            key,
            default,
        )

    def build_ui(self):

        self.setStyleSheet(
            f"""
            QMainWindow {{
                background: {BG};
            }}
            QWidget {{
                font-family: "Segoe UI";
                color: {TEXT};
            }}
            QFrame#sidebar {{
                background: {SIDEBAR};
            }}
            QFrame#statCard {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 14px;
            }}
            QFrame#contentCard {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 14px;
            }}
            QLineEdit,
            QPlainTextEdit,
            QSpinBox,
            QComboBox {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 8px;
                color: {TEXT};
            }}
            QLineEdit:focus,
            QPlainTextEdit:focus,
            QSpinBox:focus,
            QComboBox:focus {{
                border: 2px solid {PRIMARY};
            }}
            QPushButton {{
                background: {PRIMARY};
                color: {WHITE};
                border: none;
                border-radius: 8px;
                padding: 9px 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: {SIDEBAR};
            }}
            QPushButton:disabled {{
                background: #B9C2C9;
                color: #EEF2F5;
            }}
            QPushButton[class="secondary"] {{
                background: {SECONDARY};
                color: {TEXT};
            }}
            QPushButton[class="danger"] {{
                background: {DANGER};
                color: {WHITE};
            }}
            QPushButton[class="success"] {{
                background: {SUCCESS};
                color: {WHITE};
            }}
            QTableWidget {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 8px;
                gridline-color: {BORDER};
                selection-background-color: {SECONDARY};
                selection-color: {TEXT};
            }}
            QHeaderView::section {{
                background: {SIDEBAR};
                color: {WHITE};
                padding: 9px;
                border: none;
                font-weight: 600;
            }}
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QProgressBar {{
                background: #E7EDF1;
                border: none;
                border-radius: 8px;
                text-align: center;
                height: 18px;
            }}
            QProgressBar::chunk {{
                background: {PRIMARY};
                border-radius: 8px;
            }}
            QCheckBox {{
                spacing: 8px;
            }}
            """
        )

        central = QWidget()

        self.setCentralWidget(
            central
        )

        main_layout = QHBoxLayout(
            central
        )

        main_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        main_layout.setSpacing(
            0
        )

        sidebar = self.build_sidebar()

        main_layout.addWidget(
            sidebar
        )

        self.stack = QStackedWidget()

        self.dashboard_page = DashboardPage(
            self
        )

        self.recipients_page = RecipientsPage(
            self
        )

        self.certificates_page = CertificatesPage(
            self
        )

        self.send_page = SendPage(
            self
        )

        self.logs_page = LogsPage(
            self
        )

        self.settings_page = SettingsPage(
            self
        )

        self.stack.addWidget(
            self.dashboard_page
        )

        self.stack.addWidget(
            self.recipients_page
        )

        self.stack.addWidget(
            self.certificates_page
        )

        self.stack.addWidget(
            self.send_page
        )

        self.stack.addWidget(
            self.logs_page
        )

        self.stack.addWidget(
            self.settings_page
        )

        main_layout.addWidget(
            self.stack
        )

        self.set_active_nav(
            0
        )

    def build_sidebar(self):

        sidebar = QFrame()

        sidebar.setObjectName(
            "sidebar"
        )

        sidebar.setFixedWidth(
            240
        )

        layout = QVBoxLayout(
            sidebar
        )

        layout.setContentsMargins(
            16,
            22,
            16,
            20,
        )

        layout.setSpacing(
            8
        )

        title = QLabel(
            "AFRIC 2026"
        )

        title.setStyleSheet(
            f"""
            QLabel {{
                color: {WHITE};
                font-size: 22px;
                font-weight: 700;
                padding: 10px;
            }}
            """
        )

        layout.addWidget(
            title
        )

        subtitle = QLabel(
            "Certificate Automation"
        )

        subtitle.setStyleSheet(
            f"""
            QLabel {{
                color: {SECONDARY};
                font-size: 11px;
                padding-left: 10px;
                padding-bottom: 18px;
            }}
            """
        )

        layout.addWidget(
            subtitle
        )

        self.nav_buttons = []

        navigation = [
            (
                "Dashboard",
                self.show_dashboard,
            ),
            (
                "Recipients",
                self.show_recipients,
            ),
            (
                "Certificates",
                self.show_certificates,
            ),
            (
                "Send Certificates",
                self.show_send,
            ),
            (
                "Sending Logs",
                self.show_logs,
            ),
            (
                "Settings",
                self.show_settings,
            ),
        ]

        for index, (
            text,
            handler,
        ) in enumerate(navigation):

            button = QPushButton(
                text
            )

            button.setCheckable(
                True
            )

            button.setMinimumHeight(
                44
            )

            button.setStyleSheet(
                f"""
                QPushButton {{
                    text-align: left;
                    padding-left: 16px;
                    background: transparent;
                    color: {WHITE};
                    border-radius: 8px;
                }}
                QPushButton:hover {{
                    background: #40576F;
                }}
                QPushButton:checked {{
                    background: {PRIMARY};
                    color: {WHITE};
                }}
                QPushButton:disabled {{
                    color: #91A0AD;
                    background: transparent;
                }}
                """
            )

            button.clicked.connect(
                handler
            )

            self.nav_buttons.append(
                button
            )

            layout.addWidget(
                button
            )

        layout.addStretch()

        footer = QLabel(
            "AFRIC 2026\nCertificate Distribution"
        )

        footer.setAlignment(
            Qt.AlignCenter
        )

        footer.setStyleSheet(
            f"""
            QLabel {{
                color: #B8C5D0;
                font-size: 10px;
                padding: 10px;
            }}
            """
        )

        layout.addWidget(
            footer
        )

        return sidebar

    def set_active_nav(
        self,
        index,
    ):

        for i, button in enumerate(
            self.nav_buttons
        ):

            button.setChecked(
                i == index
            )

        self.stack.setCurrentIndex(
            index
        )

    def show_dashboard(self):

        self.current_page = "dashboard"

        self.set_active_nav(
            0
        )

        self.dashboard_page.refresh()

    def show_recipients(self):

        self.current_page = "recipients"

        self.set_active_nav(
            1
        )

        self.recipients_page.refresh()

    def show_certificates(self):

        self.current_page = "certificates"

        self.set_active_nav(
            2
        )

        self.certificates_page.refresh()

    def show_send(self):

        self.current_page = "send"

        self.set_active_nav(
            3
        )

        self.send_page.refresh()

    def show_logs(self):

        self.current_page = "logs"

        self.set_active_nav(
            4
        )

        self.logs_page.refresh()

    def show_settings(self):

        self.current_page = "settings"

        self.set_active_nav(
            5
        )

        self.settings_page.refresh()

    def refresh_all(self):

        self.send_page.refresh()

        self.dashboard_page.refresh()

        self.recipients_page.refresh()

        self.certificates_page.refresh()

        self.logs_page.refresh()

        self.settings_page.refresh()

    def validate_current_files(self):
        """
        This method is kept as a central entry point.
        Actual validation logic belongs to SendPage because
        validation is part of the sending workflow.
        """

        self.send_page.validate_files()

    def update_dashboard(self):
        """
        Compatibility method.
        Dashboard-specific calculations are handled by
        DashboardPage.
        """

        self.dashboard_page.refresh()

    def load_recipients_table(self):
        """
        Compatibility method for old code.
        Recipient table logic now belongs to RecipientsPage.
        """

        self.recipients_page.refresh()

    def load_certificates_table(self):
        """
        Compatibility method for old code.
        Certificate table logic now belongs to
        CertificatesPage.
        """

        self.certificates_page.refresh()

    def load_logs_table(self):
        """
        Compatibility method for old code.
        Log table logic now belongs to LogsPage.
        """

        self.logs_page.refresh()

    def refresh_after_sending(self):

        self.already_sent = (
            get_sent_recipients(
                self.log_file
            )
        )

        self.dashboard_page.refresh()

        self.recipients_page.refresh()

        self.certificates_page.refresh()

        self.logs_page.refresh()

        self.send_page.refresh()

    def closeEvent(
        self,
        event,
    ):

        if (
            self.is_sending
            and self.worker
        ):

            reply = QMessageBox.question(
                self,
                "Sending in Progress",
                (
                    "Certificate sending is currently running.\n\n"
                    "Stopping the application will stop the sending process.\n\n"
                    "Do you want to exit?"
                ),
                QMessageBox.Yes
                | QMessageBox.No,
                QMessageBox.No,
            )

            if reply != QMessageBox.Yes:

                event.ignore()

                return

            self.worker.stop()

            self.worker.wait(
                5000
            )

            event.accept()

            return

        reply = QMessageBox.question(
            self,
            "Exit",
            "Are you sure you want to close the application?",
            QMessageBox.Yes
            | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:

            event.accept()

        else:

            event.ignore()