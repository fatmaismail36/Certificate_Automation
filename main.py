import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from main_window import CertificateAutomationApp


def main():

    app = QApplication(
        sys.argv
    )

    app.setApplicationName(
        "AFRIC 2026 Certificate Automation"
    )

    app.setFont(
        QFont(
            "Segoe UI",
            10,
        )
    )

    window = CertificateAutomationApp()

    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()