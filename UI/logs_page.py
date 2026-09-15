import pandas as pd

from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QAbstractItemView,
)

TEXT = "#2F4156"

MUTED = "#6B7280"

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

class LogsPage(QWidget):
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
                "Sending Logs",
                "Track successful, failed, and resumed certificate deliveries.",
            )
        )
        controls = QHBoxLayout()
        self.log_search = QLineEdit()
        self.log_search.setPlaceholderText(
            "Search logs..."
        )
        self.log_search.textChanged.connect(
            self.filter_logs
        )
        controls.addWidget(
            self.log_search,
            1,
        )
        self.log_status_filter = QComboBox()
        self.log_status_filter.addItems(
            [
                "All",
                "SENT",
                "FAILED",
            ]
        )
        self.log_status_filter.currentTextChanged.connect(
            self.filter_logs
        )
        controls.addWidget(
            self.log_status_filter
        )
        export_button = QPushButton(
            "Export CSV"
        )
        export_button.setProperty(
            "class",
            "secondary",
        )
        export_button.clicked.connect(
            self.export_logs
        )
        controls.addWidget(
            export_button
        )
        refresh_button = QPushButton(
            "Refresh"
        )
        refresh_button.clicked.connect(
            self.load_logs_table
        )
        controls.addWidget(
            refresh_button
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
        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(
            6
        )
        self.logs_table.setHorizontalHeaderLabels(
            [
                "Name",
                "Email",
                "Certificate",
                "Status",
                "Timestamp",
                "Error",
            ]
        )
        self.prepare_table(
            self.logs_table
        )
        card_layout.addWidget(
            self.logs_table
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

    def load_logs_table(self):
        table = self.logs_table
        table.setRowCount(0)
        if not self.app.log_file.exists():
            return
        try:
            df = pd.read_csv(
                self.app.log_file
            )
        except Exception as error:
            QMessageBox.warning(
                self,
                "Log Error",
                (
                    "Could not read log file.\n\n"
                    f"{error}"
                ),
            )
            return
        if df.empty:
            return
        table.setRowCount(
            len(df)
        )
        for row, (
            _,
            data,
        ) in enumerate(
            df.iterrows()
        ):
            values = [
                str(
                    data.get(
                        "name",
                        "",
                    )
                ),
                str(
                    data.get(
                        "email",
                        "",
                    )
                ),
                str(
                    data.get(
                        "certificate",
                        "",
                    )
                ),
                str(
                    data.get(
                        "status",
                        "",
                    )
                ),
                str(
                    data.get(
                        "timestamp",
                        data.get(
                            "date",
                            "",
                        ),
                    )
                ),
                str(
                    data.get(
                        "error",
                        "",
                    )
                ),
            ]
            for column, value in enumerate(
                values
            ):
                table.setItem(
                    row,
                    column,
                    QTableWidgetItem(
                        value
                    ),
                )
        self.filter_logs()

    def filter_logs(self):
        search = (
            self.log_search
            .text()
            .lower()
            .strip()
        )
        status_filter = (
            self.log_status_filter
            .currentText()
        )
        for row in range(
            self.logs_table.rowCount()
        ):
            values = []
            for column in range(
                self.logs_table.columnCount()
            ):
                item = self.logs_table.item(
                    row,
                    column,
                )
                if item:
                    values.append(
                        item.text().lower()
                    )
            row_text = " ".join(
                values
            )
            status_item = (
                self.logs_table.item(
                    row,
                    3,
                )
            )
            status = (
                status_item.text()
                if status_item
                else ""
            )
            matches_search = (
                not search
                or search in row_text
            )
            matches_status = (
                status_filter == "All"
                or status == status_filter
            )
            self.logs_table.setRowHidden(
                row,
                not (
                    matches_search
                    and matches_status
                ),
            )

    def export_logs(self):
        if not self.app.log_file.exists():
            QMessageBox.information(
                self,
                "No Logs",
                "There is no sending log to export.",
            )
            return
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Sending Logs",
            "sending_log_export.csv",
            "CSV Files (*.csv)",
        )
        if not save_path:
            return
        try:
            df = pd.read_csv(
                self.app.log_file
            )
            df.to_csv(
                save_path,
                index=False,
            )
            QMessageBox.information(
                self,
                "Export Complete",
                (
                    "Logs exported successfully.\n\n"
                    f"{save_path}"
                ),
            )
        except Exception as error:
            QMessageBox.critical(
                self,
                "Export Error",
                (
                    "Could not export logs.\n\n"
                    f"{error}"
                ),
            )

    def refresh(self):
        self.load_logs_table()