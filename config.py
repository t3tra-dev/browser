from typing import Dict
from PySide6.QtGui import QKeySequence


class Config:
    APP_NAME: str = "Simple Browser"
    WINDOW_WIDTH: int = 1024
    WINDOW_HEIGHT: int = 720

    DEFAULT_URL: str = "https://www.google.com"
    SEARCH_ENGINE_URL: str = "https://www.google.com/search"
    SEARCH_QUERY_PARAM: str = "q"

    KEYBINDINGS: Dict[str, str] = {
        "new_tab": "Ctrl+T",
        "close_tab": "Ctrl+W",
        "quit": "Ctrl+Q",
        "dev_tools": "F12",
        "dev_tools_dock": "Ctrl+Shift+D"
    }

    @classmethod
    def get_keysequence(cls, action: str) -> QKeySequence:
        return QKeySequence(cls.KEYBINDINGS.get(action, ""))
