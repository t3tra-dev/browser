
from PySide6.QtCore import QFileSystemWatcher
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from tab import BrowserTab
from config import Config


class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(Config.APP_NAME)
        self.setGeometry(100, 100, Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT)

        menubar = self.menuBar()
        menubar.setContentsMargins(0, 0, 0, 0)

        self.setContentsMargins(0, 0, 0, 0)

        self.load_stylesheet()

        self.central_widget = QWidget()
        self.central_widget.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.central_widget.setLayout(self.layout)

        self.load_stylesheet()

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)

        self.tabs.setUsesScrollButtons(True)
        self.tabs.setMovable(True)

        self.add_tab_button = QPushButton("+")
        self.add_tab_button.setObjectName("addTabButton")
        self.add_tab_button.clicked.connect(self.add_new_tab)
        self.tabs.setCornerWidget(self.add_tab_button)

        self.watcher = QFileSystemWatcher(self)
        self.watcher.addPath("styles.qss")
        self.watcher.fileChanged.connect(self.reload_stylesheet)

        self.create_menu_bar()

        self.layout.addWidget(self.tabs)

        self.add_new_tab()

    def add_new_tab(self):
        new_tab = BrowserTab()
        index = self.tabs.addTab(new_tab, "New Tab")
        self.tabs.setCurrentIndex(index)

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.close()

    def create_menu_bar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")

        new_tab_action = QAction("New Tab", self)
        new_tab_action.setShortcut(Config.get_keysequence("new_tab"))
        new_tab_action.triggered.connect(self.add_new_tab)
        file_menu.addAction(new_tab_action)

        close_tab_action = QAction("Close Tab", self)
        close_tab_action.setShortcut(Config.get_keysequence("close_tab"))
        close_tab_action.triggered.connect(
            lambda: self.close_tab(self.tabs.currentIndex())
        )
        file_menu.addAction(close_tab_action)

        exit_action = QAction("Exit", self)
        exit_action.setShortcut(Config.get_keysequence("quit"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        view_menu = menubar.addMenu("View")
        dev_tools_action = QAction("Developer Tools", self)
        dev_tools_action.setShortcut(Config.get_keysequence("dev_tools"))
        dev_tools_action.triggered.connect(
            lambda: self.tabs.currentWidget().toggle_dev_tools()
        )
        view_menu.addAction(dev_tools_action)

    def load_stylesheet(self):
        try:
            with open("styles.qss", "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError as e:
            raise e

    def reload_stylesheet(self):
        try:
            with open("styles.qss", "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError as e:
            raise e
