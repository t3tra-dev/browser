import sys
import urllib.parse

from PySide6.QtCore import QUrl
from PySide6.QtGui import QShortcut, QIcon, QMovie
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
    QTabWidget,
)

from config import Config


class BrowserTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.dev_tools_window = None
        self.dev_tools_view = None
        self.is_dev_tools_docked = True

        self.dev_tools_shortcut = QShortcut(Config.get_keysequence("dev_tools"), self)
        self.dev_tools_dock_shortcut = QShortcut(Config.get_keysequence("dev_tools_dock"), self)

        self.navigation_bar = QWidget()
        self.navigation_bar.setObjectName("navigationBar")
        self.navigation_layout = QHBoxLayout()
        self.navigation_layout.setSpacing(4)
        self.navigation_layout.setContentsMargins(8, 4, 8, 4)
        self.navigation_bar.setLayout(self.navigation_layout)

        self.back_button = QPushButton("←")
        self.back_button.setObjectName("navButton")
        self.forward_button = QPushButton("→")
        self.forward_button.setObjectName("navButton")
        self.reload_button = QPushButton("↻")
        self.reload_button.setObjectName("navButton")

        self.url_bar = QLineEdit()
        self.url_bar.setObjectName("urlBar")
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        self.navigation_layout.addWidget(self.back_button)
        self.navigation_layout.addWidget(self.forward_button)
        self.navigation_layout.addWidget(self.reload_button)
        self.navigation_layout.addWidget(self.url_bar)

        self.content_widget = QSplitter()
        self.content_layout = QHBoxLayout()
        self.content_layout.setSpacing(0)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        self.web_view = QWebEngineView()
        self.web_view.javaScriptConsoleMessage = lambda *args: None
        self.web_view.setObjectName("webView")
        self.web_view.loadFinished.connect(self.update_url)
        self.web_view.loadFinished.connect(self.on_load_finished)
        self.web_view.loadStarted.connect(self.on_load_started)
        self.web_view.iconChanged.connect(self.update_favicon)
        self.web_view.titleChanged.connect(self.update_tab_title)

        self.content_widget.addWidget(self.web_view)

        platform = sys.platform
        if platform == "darwin":
            user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        elif platform == "win32":
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        else:  # Linux
            user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        self.web_view.page().profile().setHttpUserAgent(user_agent)
        self.web_view.page().createWindow = self.create_window

        self.back_button.clicked.connect(self.web_view.back)
        self.forward_button.clicked.connect(self.web_view.forward)
        self.reload_button.clicked.connect(self.handle_reload_click)
        self.reload_button.clicked.connect(self.web_view.reload)
        self.dev_tools_shortcut.activated.connect(self.toggle_dev_tools)
        self.dev_tools_dock_shortcut.activated.connect(self.toggle_dev_tools_dock)

        self.favicon = QIcon("assets/file.svg")
        self.loading_movie = QMovie("assets/loading.gif")
        self.loading_movie.frameChanged.connect(self.update_loading_icon)

        self.layout.addWidget(self.navigation_bar)
        self.layout.addWidget(self.content_widget)

        self.web_view.setUrl(QUrl(Config.DEFAULT_URL))

    def closeEvent(self, event):
        if self.dev_tools_window:
            self.dev_tools_window.close()
        self.close_dev_tools()
        super().closeEvent(event)

    def close_dev_tools(self):
        if self.dev_tools_view:
            if self.web_view and self.web_view.page():
                self.web_view.page().setDevToolsPage(None)

            if self.is_dev_tools_docked:
                widget = self.content_widget.widget(1)
                if widget:
                    widget.setParent(None)
                    widget.deleteLater()
            else:
                if self.dev_tools_window:
                    self.dev_tools_window.close()
                    self.dev_tools_window.hide()
                    self.dev_tools_window.setParent(None)
                    self.dev_tools_window.deleteLater()
                    self.dev_tools_window = None

            self.dev_tools_view.setParent(None)
            self.dev_tools_view.deleteLater()
            self.dev_tools_view = None

    def navigate_to_url(self):
        url = self.url_bar.text().strip()

        if not url:
            self.web_view.setUrl(QUrl(Config.DEFAULT_URL))
            return

        if not url.startswith(("http://", "https://")):
            if "." in url and " " not in url:
                url = "https://" + url
            else:
                search_url = QUrl(Config.SEARCH_ENGINE_URL)
                search_url.setQuery(f"{Config.SEARCH_QUERY_PARAM}={urllib.parse.quote(url)}")
                self.web_view.setUrl(search_url)
                return
        self.web_view.setUrl(QUrl(url))

    def update_url(self):
        self.url_bar.setText(self.web_view.url().toString())

    def toggle_dev_tools(self):
        if not self.dev_tools_view:
            self.dev_tools_view = QWebEngineView()
            self.web_view.page().setDevToolsPage(self.dev_tools_view.page())

            self.dev_tools_view.page().setInspectedPage(self.web_view.page())
            self.dev_tools_view.setWindowTitle(f"{self.web_view.title()} (Developer Tools)")

            self.dev_tools_view.page().windowCloseRequested.connect(self.close_dev_tools)

            if self.is_dev_tools_docked:
                self.content_widget.addWidget(self.dev_tools_view)
                self.content_widget.setSizes([600, 400])
            else:
                self.dev_tools_window = QWidget()
                self.dev_tools_window.setWindowTitle("Developer Tools")
                layout = QVBoxLayout()
                layout.setContentsMargins(0, 0, 0, 0)
                layout.addWidget(self.dev_tools_view)
                self.dev_tools_window.setLayout(layout)
                self.dev_tools_window.resize(800, 600)

                dev_tools_shortcut_window = QShortcut(Config.get_keysequence("dev_tools"), self.dev_tools_window)
                dev_tools_dock_shortcut_window = QShortcut(Config.get_keysequence("dev_tools_dock"), self.dev_tools_window)
                dev_tools_shortcut_window.activated.connect(self.toggle_dev_tools)
                dev_tools_dock_shortcut_window.activated.connect(self.toggle_dev_tools_dock)

                self.dev_tools_window.show()
        else:
            self.close_dev_tools()

    def toggle_dev_tools_dock(self):
        if not self.dev_tools_view:
            self.is_dev_tools_docked = not self.is_dev_tools_docked
            self.toggle_dev_tools()
            return

        if self.is_dev_tools_docked:
            self.content_widget.widget(1).setParent(None)
            self.dev_tools_window = QWidget()
            self.dev_tools_window.setWindowTitle("Developer Tools")
            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.dev_tools_view)
            self.dev_tools_window.setLayout(layout)
            self.dev_tools_window.resize(800, 600)

            dev_tools_shortcut_window = QShortcut(Config.get_keysequence("dev_tools"), self.dev_tools_window)
            dev_tools_dock_shortcut_window = QShortcut(Config.get_keysequence("dev_tools_dock"), self.dev_tools_window)
            dev_tools_shortcut_window.activated.connect(self.toggle_dev_tools)
            dev_tools_dock_shortcut_window.activated.connect(self.toggle_dev_tools_dock)

            self.dev_tools_window.show()
        else:
            self.dev_tools_window.hide()
            self.dev_tools_window.setParent(None)
            self.dev_tools_window.deleteLater()
            self.dev_tools_window = None

            self.content_widget.addWidget(self.dev_tools_view)
            self.content_widget.setSizes([600, 400])

        self.is_dev_tools_docked = not self.is_dev_tools_docked

    def handle_reload_click(self):
        if self.web_view.page().isLoading():
            self.web_view.stop()
        else:
            self.web_view.reload()

    def on_load_started(self):
        self.reload_button.setText("×")
        self.loading_movie.start()
        parent = self.parent()
        while parent and not isinstance(parent, QTabWidget):
            parent = parent.parent()
        if parent:
            parent.setTabIcon(parent.indexOf(self), QIcon())
            parent.setTabIcon(parent.indexOf(self), QIcon(self.loading_movie.currentPixmap()))

    def on_load_finished(self, success):
        self.reload_button.setText("↻")
        self.loading_movie.stop()
        if not self.web_view.icon().isNull():
            self.update_favicon(self.web_view.icon())
        else:
            self.update_favicon(QIcon("assets/file.svg"))

    def update_favicon(self, icon):
        self.favicon = icon
        parent = self.parent()
        while parent and not isinstance(parent, QTabWidget):
            parent = parent.parent()
        if parent:
            parent.setTabIcon(parent.indexOf(self), self.favicon)

    def update_loading_icon(self):
        parent = self.parent()
        while parent and not isinstance(parent, QTabWidget):
            parent = parent.parent()

        if parent and self.loading_movie.state() == QMovie.Running:
            parent.setTabIcon(parent.indexOf(self), QIcon(self.loading_movie.currentPixmap()))

    def create_window(self, window_type):
        parent = self.parent()
        while parent and not isinstance(parent, QTabWidget):
            parent = parent.parent()

        if parent:
            current_index = parent.indexOf(self)

            new_tab = BrowserTab()
            parent.insertTab(current_index + 1, new_tab, "New Tab")
            parent.setCurrentWidget(new_tab)

            return new_tab.web_view

        return None

    def update_tab_title(self, title):
        parent = self.parent()
        while parent and not isinstance(parent, QTabWidget):
            parent = parent.parent()
        if parent:
            parent.setTabText(parent.indexOf(self), title)
