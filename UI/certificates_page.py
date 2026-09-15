from pathlib import Path

from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QAbstractItemView,
)

TEXT = "#2F4156"
MUTED = "#6B7280"
SUCCESS = "#2E7D32"
WARNING = "#B7791F"
DANGER = "#C62828"

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

class StatusBadge(QLabel):
    def __init__(
        self,
        text,
        badge_type="default",
        parent=None,
    ):
        super().__init__(
            str(text),
            parent,
        )
        self.setAlignment(
            Qt.AlignCenter
        )
        self.setMinimumHeight(28)
        styles = {
            "success": (
                "#E8F5E9",
                SUCCESS,
            ),
            "warning": (
                "#FFF8E1",
                WARNING,
            ),
            "danger": (
                "#FFEBEE",
                DANGER,
            ),
            "default": (
                "#EEF2F5",
                TEXT,
            ),
        }
        background, foreground = styles.get(
            badge_type,
            styles["default"],
        )
        self.setStyleSheet(
            f"""
            QLabel {{
                background: {background};
                color: {foreground};
                border-radius: 12px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 700;
            }}
            """
        )

class CertificatesPage(QWidget):
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
                "Certificates",
                "Review certificate files and exact recipient matches.",
            )
        )

        folder_card = QFrame()
        folder_card.setObjectName(
            "contentCard"
        )
        folder_layout = QHBoxLayout(
            folder_card
        )
        folder_layout.setContentsMargins(
            15,
            12,
            15,
            12,
        )
        self.certificate_folder_input = QLineEdit()
        self.certificate_folder_input.setReadOnly(
            True
        )
        folder_layout.addWidget(
            self.certificate_folder_input,
            1,
        )
        browse_button = QPushButton(
            "Browse Folder"
        )
        browse_button.clicked.connect(
            self.select_certificate_folder
        )
        folder_layout.addWidget(
            browse_button
        )
        layout.addWidget(
            folder_card
        )

        card = QFrame()
        card.setObjectName(
            "contentCard"
        )
        card_layout = QVBoxLayout(
            card
        )
        card_layout.setContentsMargins(
            12,
            12,
            12,
            12,
        )
        self.certificates_table = QTableWidget()
        self.certificates_table.setColumnCount(
            3
        )
        self.certificates_table.setHorizontalHeaderLabels(
            [
                "Certificate",
                "Recipient Name",
                "Status",
            ]
        )
        self.prepare_table(
            self.certificates_table
        )
        card_layout.addWidget(
            self.certificates_table
        )
        layout.addWidget(
            card,
            1,
        )

    def prepare_table(self, table):
        table.setAlternatingRowColors(
            True
        )
        table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )
        table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )
        table.verticalHeader().setVisible(
            False
        )
        table.horizontalHeader().setStretchLastSection(
            True
        )
        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

    def select_certificate_folder(self):
        self.app.send_page.select_certificate_folder()

    def load_certificates_table(self):
        table = self.certificates_table
        table.setRowCount(0)
        if not self.app.certificate_folder.exists():
            return
        certificate_files = sorted(
            self.app.certificate_folder.glob(
                "*.pdf"
            ),
            key=lambda path: path.name.lower(),
        )
        table.setRowCount(
            len(certificate_files)
        )
        recipient_names = set()
        if self.app.recipients_df is not None:
            recipient_names = set(
                self.app.recipients_df[
                    "Name"
                ]
                .fillna("")
                .astype(str)
                .tolist()
            )
        for row, path in enumerate(
            certificate_files
        ):
            certificate_name = path.name
            recipient_name = path.stem
            status = (
                "MATCHED"
                if recipient_name in recipient_names
                else "UNMATCHED"
            )
            table.setItem(
                row,
                0,
                QTableWidgetItem(
                    certificate_name
                ),
            )
            table.setItem(
                row,
                1,
                QTableWidgetItem(
                    recipient_name
                ),
            )
            badge = StatusBadge(
                status,
                (
                    "success"
                    if status == "MATCHED"
                    else "warning"
                ),
            )
            table.setCellWidget(
                row,
                2,
                badge,
            )
        self.certificate_folder_input.setText(
            str(
                self.app.certificate_folder
            )
        )

    def refresh(self):
        self.load_certificates_table()