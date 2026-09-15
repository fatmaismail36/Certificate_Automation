from pathlib import Path

from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QAbstractItemView,
)


TEXT = "#2F4156"

MUTED = "#6B7280"

WHITE = "#FFFFFF"

BORDER = "#D7DEE5"

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
        layout.addWidget(title_label)
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


class RecipientsPage(QWidget):
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
                "Recipients",
                "Review validation status for every recipient.",
            )
        )
        controls = QHBoxLayout()
        self.recipient_search = QLineEdit()
        self.recipient_search.setPlaceholderText(
            "Search by name or email..."
        )
        self.recipient_search.textChanged.connect(
            self.filter_recipient_table
        )
        controls.addWidget(
            self.recipient_search,
            1,
        )
        self.recipient_status_filter = QComboBox()
        self.recipient_status_filter.addItems(
            [
                "All",
                "READY",
                "SENT",
                "INVALID",
                "MISSING CERTIFICATE",
                "DUPLICATE",
            ]
        )
        self.recipient_status_filter.currentTextChanged.connect(
            self.filter_recipient_table
        )
        controls.addWidget(
            self.recipient_status_filter
        )
        layout.addLayout(
            controls
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
        self.recipients_table = QTableWidget()
        self.recipients_table.setColumnCount(
            5
        )
        self.recipients_table.setHorizontalHeaderLabels(
            [
                "Name",
                "Email",
                "Certificate",
                "Status",
                "Reason",
            ]
        )
        self.prepare_table(
            self.recipients_table
        )
        card_layout.addWidget(
            self.recipients_table
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

    def load_recipients_table(self):
        table = self.recipients_table
        table.setRowCount(0)
        if self.app.validation_result is None:
            return
        result = self.app.validation_result
        rows = []
        for item in result.get(
            "ready_recipients",
            [],
        ):
            key = self.app.send_page.recipient_key(
                item
            )
            status = (
                "SENT"
                if key in self.app.already_sent
                else "READY"
            )
            reason = (
                "Already sent"
                if status == "SENT"
                else "Exact name + certificate match"
            )
            rows.append(
                (
                    item,
                    status,
                    reason,
                )
            )
        for item in result.get(
            "invalid_recipients",
            [],
        ):
            rows.append(
                (
                    item,
                    "INVALID",
                    "Invalid email",
                )
            )
        for item in result.get(
            "missing_certificate_recipients",
            [],
        ):
            rows.append(
                (
                    item,
                    "MISSING CERTIFICATE",
                    item.get(
                        "reason",
                        "Certificate not found",
                    ),
                )
            )
        for item in result.get(
            "duplicate_recipients",
            [],
        ):
            rows.append(
                (
                    item,
                    "DUPLICATE",
                    "Duplicate Name + Email",
                )
            )
        table.setRowCount(
            len(rows)
        )
        for row_index, (
            item,
            status,
            reason,
        ) in enumerate(rows):
            name = str(
                item.get(
                    "Name",
                    item.get(
                        "name",
                        "",
                    ),
                )
            )
            email = str(
                item.get(
                    "Email",
                    item.get(
                        "email",
                        "",
                    ),
                )
            ).strip().lower()
            certificate_path = item.get(
                "certificate_path"
            )
            if certificate_path:
                certificate = Path(
                    certificate_path
                ).name
            else:
                certificate = str(
                    item.get(
                        "certificate",
                        "",
                    )
                )
            table.setItem(
                row_index,
                0,
                QTableWidgetItem(
                    name
                ),
            )
            table.setItem(
                row_index,
                1,
                QTableWidgetItem(
                    email
                ),
            )
            table.setItem(
                row_index,
                2,
                QTableWidgetItem(
                    certificate
                ),
            )
            badge = StatusBadge(
                status,
                self.status_type(status),
            )
            table.setCellWidget(
                row_index,
                3,
                badge,
            )
            table.setItem(
                row_index,
                4,
                QTableWidgetItem(
                    reason
                ),
            )
        self.filter_recipient_table()

    def filter_recipient_table(self):
        search = (
            self.recipient_search
            .text()
            .lower()
            .strip()
        )
        status_filter = (
            self.recipient_status_filter
            .currentText()
        )
        for row in range(
            self.recipients_table.rowCount()
        ):
            name = self.recipients_table.item(
                row,
                0,
            )
            email = self.recipients_table.item(
                row,
                1,
            )
            status_widget = (
                self.recipients_table.cellWidget(
                    row,
                    3,
                )
            )
            if (
                not name
                or not email
                or not status_widget
            ):
                self.recipients_table.setRowHidden(
                    row,
                    True,
                )
                continue
            name_text = name.text().lower()
            email_text = email.text().lower()
            status_text = status_widget.text()
            matches_search = (
                not search
                or search in name_text
                or search in email_text
            )
            matches_status = (
                status_filter == "All"
                or status_text == status_filter
            )
            self.recipients_table.setRowHidden(
                row,
                not (
                    matches_search
                    and matches_status
                ),
            )

    def status_type(self, status):
        status = status.upper()
        if status in (
            "READY",
            "SENT",
            "MATCHED",
        ):
            return "success"
        if status in (
            "DUPLICATE",
            "SKIPPED",
            "UNMATCHED",
        ):
            return "warning"
        if status in (
            "FAILED",
            "INVALID",
            "MISSING CERTIFICATE",
        ):
            return "danger"
        return "default"

    def refresh(self):
        self.load_recipients_table()