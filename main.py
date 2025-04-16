import sys

from PySide6.QtWidgets import QApplication

from window import BrowserWindow


def main():
    app = QApplication(sys.argv)
    window = BrowserWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
