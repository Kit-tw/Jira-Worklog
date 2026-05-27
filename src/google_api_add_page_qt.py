import re

from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt

import util.common_util as common_util
import util.file_util as file_util
from constant.Enum import STORAGE, URL


class GoogleApiPage(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Google API Credentials")
        self.setFixedSize(700, 380)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self._setup_ui()

    def _setup_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(40, 30, 40, 30)
        root.setSpacing(40)
        root.addLayout(self._build_steps(), 3)
        root.addLayout(self._build_upload(), 1)

    def _build_steps(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        title = QLabel("How to get Google API credentials")
        title.setObjectName("title")
        layout.addWidget(title)
        layout.addSpacing(8)

        steps = [
            ("1. Go to Google Developer Console", URL.GOOGLE_DEVELOPER_CONSOLE.value),
            ("2. Create project, enable Sheets & Drive API, then create OAuth credentials", None),
            ("3. Add your email as a test user in the OAuth consent screen", None),
            ("4. Download the credentials JSON and upload it here", None),
        ]
        for text, url in steps:
            if url:
                btn = QPushButton(text)
                btn.setObjectName("link")
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.clicked.connect(lambda _, u=url: common_util.open_url(u))
                layout.addWidget(btn)
            else:
                lbl = QLabel(text)
                lbl.setObjectName("subtitle")
                lbl.setWordWrap(True)
                layout.addWidget(lbl)

        layout.addSpacing(4)
        ref_btn = QPushButton("Reference Documentation")
        ref_btn.setObjectName("link")
        ref_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ref_btn.clicked.connect(lambda: common_util.open_url(URL.GSPREAD_GOOGLE_API_DOC.value))
        layout.addWidget(ref_btn)

        layout.addStretch()
        return layout

    def _build_upload(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.addStretch()

        label = QLabel("Upload credentials.json")
        label.setObjectName("subtitle")
        layout.addWidget(label)

        btn = QPushButton("Choose File")
        btn.clicked.connect(self._select_file)
        layout.addWidget(btn)

        layout.addStretch()
        return layout

    def _select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select credentials.json", "", "JSON Files (*.json)")
        if not path:
            return
        if self._validate_credential(path):
            try:
                file_util.copy_file(path, STORAGE.GOOGLE_API_CREDENTIALS_PATH.value)
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to copy file: {e}")

    def _validate_credential(self, file_path: str) -> bool:
        try:
            data = file_util.read_json_by_path(file_path)
            if data is not None and re.search(r"(client_id).*(project_id)", str(data)):
                return True
            raise ValueError("Missing required fields")
        except Exception:
            QMessageBox.warning(
                self, "Invalid File",
                "Not a valid OAuth client ID JSON. Please download the correct file."
            )
            return False
