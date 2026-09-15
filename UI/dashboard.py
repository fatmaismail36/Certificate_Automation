from pathlib import Path

import pandas as pd

from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from logger import get_sent_recipients

BG = "#F5EFEB"
PRIMARY = "#567C8D"
SECONDARY = "#C8D9E6"
WHITE = "#FFFFFF"
TEXT = "#2F4156"
MUTED = "#6B7280"
BORDER = "#D7DEE5"

class StatCard(QFrame):
    def __init__(self, title, value="0", parent=None):
        super().__init__(parent)
        self.setObjectName("statCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        title_label = QLabel(title)
        title_label.setStyleSheet(
            f"""
            QLabel {{
                color: {MUTED};
                font-size: 12px;
                font-weight: 600;
            }}
            """
        )
        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet(
            f"""
            QLabel {{
                color: {TEXT};
                font-size: 28px;
                font-weight: 700;
            }}
            """
        )
        layout.addWidget(title_label)
        layout.addWidget(self.value_label)

    def set_value(self, value):
        self.value_label.setText(str(value))

class PageTitle(QWidget):
    def __init__(self, title, subtitle="", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 10)
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
        layout.addWidget(title_label)
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet(
                f"""
                QLabel {{
                    color: {MUTED};
                    font-size: 13px;
                }}
                """
            )
            layout.addWidget(subtitle_label)

class DashboardPage(QWidget):
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
        page_title = PageTitle(
            "Dashboard",
            "Monitor certificate validation and email distribution.",
        )
        layout.addWidget(page_title)
        cards_layout = QGridLayout()
        cards_layout.setSpacing(14)
        self.total_recipients_card = StatCard(
            "Total Recipients",
            "0",
        )
        self.total_certificates_card = StatCard(
            "Certificates",
            "0",
        )
        self.ready_card = StatCard(
            "Ready to Send",
            "0",
        )
        self.sent_card = StatCard(
            "Sent",
            "0",
        )
        cards_layout.addWidget(
            self.total_recipients_card,
            0,
            0,
        )
        cards_layout.addWidget(
            self.total_certificates_card,
            0,
            1,
        )
        cards_layout.addWidget(
            self.ready_card,
            0,
            2,
        )
        cards_layout.addWidget(
            self.sent_card,
            0,
            3,
        )
        layout.addLayout(cards_layout)
        validation_card = QFrame()
        validation_card.setObjectName("contentCard")
        validation_layout = QVBoxLayout(
            validation_card
        )
        validation_layout.setContentsMargins(
            22,
            20,
            22,
            20,
        )
        validation_title = QLabel(
            "Validation"
        )
        validation_title.setStyleSheet(
            f"""
            QLabel {{
                color: {TEXT};
                font-size: 17px;
                font-weight: 700;
            }}
            """
        )
        validation_layout.addWidget(
            validation_title
        )
        self.dashboard_validation_label = QLabel(
            "Please validate your Excel file and certificate folder."
        )
        self.dashboard_validation_label.setWordWrap(
            True
        )
        self.dashboard_validation_label.setStyleSheet(
            f"""
            QLabel {{
                color: {MUTED};
                padding: 8px 0;
            }}
            """
        )
        validation_layout.addWidget(
            self.dashboard_validation_label
        )
        self.dashboard_validation_button = QPushButton(
            "Validate Files"
        )
        self.dashboard_validation_button.clicked.connect(
            self.validate_files
        )
        validation_layout.addWidget(
            self.dashboard_validation_button,
            alignment=Qt.AlignLeft,
        )
        layout.addWidget(
            validation_card
        )
        activity_card = QFrame()
        activity_card.setObjectName("contentCard")
        activity_layout = QVBoxLayout(
            activity_card
        )
        activity_layout.setContentsMargins(
            22,
            20,
            22,
            20,
        )
        activity_title = QLabel(
            "Recent Activity"
        )
        activity_title.setStyleSheet(
            f"""
            QLabel {{
                color: {TEXT};
                font-size: 17px;
                font-weight: 700;
            }}
            """
        )
        activity_layout.addWidget(
            activity_title
        )
        self.dashboard_activity = QLabel(
            "No sending activity yet."
        )
        self.dashboard_activity.setStyleSheet(
            f"""
            QLabel {{
                color: {MUTED};
                padding-top: 8px;
            }}
            """
        )
        activity_layout.addWidget(
            self.dashboard_activity
        )
        layout.addWidget(
            activity_card
        )
        layout.addStretch()

    def validate_files(self):
        """
        Validation itself belongs to SendPage.
        Dashboard only triggers it.
        """
        self.app.send_page.validate_files()

    def update_dashboard(self):
        total_recipients = 0
        if self.app.recipients_df is not None:
            total_recipients = len(
                self.app.recipients_df
            )
        elif self.app.excel_file.exists():
            try:
                df = pd.read_excel(
                    self.app.excel_file
                )
                total_recipients = len(df)
            except Exception:
                total_recipients = 0
        total_certificates = 0
        if self.app.certificate_folder.exists():
            total_certificates = len(
                list(
                    self.app.certificate_folder.glob(
                        "*.pdf"
                    )
                )
            )
        sent_count = 0
        if self.app.log_file.exists():
            try:
                logs = pd.read_csv(
                    self.app.log_file
                )
                if (
                    not logs.empty
                    and "status" in logs.columns
                ):
                    sent_count = int(
                        (
                            logs["status"]
                            .astype(str)
                            .str.upper()
                            .eq("SENT")
                        ).sum()
                    )
            except Exception:
                sent_count = 0
        ready_count = 0
        if self.app.ready_recipients:
            sent_keys = get_sent_recipients(
                self.app.log_file
            )
            for recipient in self.app.ready_recipients:
                if (
                    self.app.send_page.recipient_key(
                        recipient
                    )
                    not in sent_keys
                ):
                    ready_count += 1
        self.total_recipients_card.set_value(
            total_recipients
        )
        self.total_certificates_card.set_value(
            total_certificates
        )
        self.ready_card.set_value(
            ready_count
        )
        self.sent_card.set_value(
            sent_count
        )
        if self.app.log_file.exists():
            try:
                logs = pd.read_csv(
                    self.app.log_file
                )
                if not logs.empty:
                    last_row = logs.iloc[-1]
                    name = str(
                        last_row.get(
                            "name",
                            "",
                        )
                    )
                    status = str(
                        last_row.get(
                            "status",
                            "",
                        )
                    )
                    self.dashboard_activity.setText(
                        f"Latest activity: {name} — {status}"
                    )
                else:
                    self.dashboard_activity.setText(
                        "No sending activity yet."
                    )
            except Exception:
                self.dashboard_activity.setText(
                    "Unable to read sending log."
                )
        else:
            self.dashboard_activity.setText(
                "No sending activity yet."
            )

    def refresh(self):
        self.update_dashboard()