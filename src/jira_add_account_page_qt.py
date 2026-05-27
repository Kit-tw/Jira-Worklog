import re

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt

import util.common_util as common_util
import util.file_util as file_util
from constant.Enum import STORAGE, URL


class AccountPage(QWidget):
    def __init__(self, app_window):
        super().__init__()
        self._app = app_window
        self._setup_ui()

    def _setup_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(60, 50, 60, 50)
        root.setSpacing(60)
        root.addLayout(self._build_steps(), 1)
        root.addLayout(self._build_form(), 1)

    def _build_steps(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        title = QLabel("How to get API token")
        title.setObjectName("title")
        layout.addWidget(title)
        layout.addSpacing(8)

        steps = [
            ("1. Go to Atlassian Account", URL.JIRA_GET_API_URL.value),
            ("2. Click Create API token", None),
            ("3. Enter name and expiry date, then create", None),
            ("4. Copy the token and paste it below", None),
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
                layout.addWidget(lbl)

        layout.addStretch()
        return layout

    def _build_form(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)

        title = QLabel("Jira Account Setup")
        title.setObjectName("title")
        layout.addWidget(title)
        layout.addSpacing(4)

        self.email_entry = QLineEdit()
        self.email_entry.setPlaceholderText("Email  e.g. example@gmail.com")
        layout.addWidget(self.email_entry)

        self.api_token_entry = QLineEdit()
        self.api_token_entry.setPlaceholderText("API Token")
        self.api_token_entry.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.api_token_entry)

        self.jira_url_entry = QLineEdit()
        self.jira_url_entry.setPlaceholderText("Jira site  e.g. company.atlassian.net")
        layout.addWidget(self.jira_url_entry)

        self.expire_date_entry = QLineEdit()
        self.expire_date_entry.setPlaceholderText("Expiry date  dd/mm/yyyy")
        layout.addWidget(self.expire_date_entry)

        layout.addSpacing(8)
        confirm_btn = QPushButton("Confirm")
        confirm_btn.clicked.connect(self._store_api)
        layout.addWidget(confirm_btn)

        layout.addStretch()
        return layout

    # ── submit ─────────────────────────────────────────────────────────────────

    def _store_api(self):
        email = self.email_entry.text().strip()
        api = self.api_token_entry.text().strip()
        url = self.jira_url_entry.text().strip()
        expire_date = self.expire_date_entry.text().strip()

        if not all([email, api, url, expire_date]):
            QMessageBox.warning(self, "Error", "Please fill in all fields.")
            return

        prefix = self._get_prefix(url)
        if not prefix:
            QMessageBox.warning(self, "Error", "Invalid Jira site URL.")
            return

        response = common_util.get_user(email, api, prefix)
        if response.status_code != 200:
            QMessageBox.warning(self, "Error", "Cannot authenticate with the provided credentials.")
            return

        data = {"jira_email": email, "jira_api": api, "jira_prefix": prefix, "expire_date": expire_date}
        try:
            file_util.save_json(STORAGE.STORAGE_PATH.value, STORAGE.TOKEN_FILE.value, data)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save credentials: {e}")
            return

        self._app.show_worklog_page()

    def _get_prefix(self, url: str) -> str | None:
        match = re.match(r'^(?:https?:\/?\/?)?([a-zA-Z0-9-]+)(?:\.atlassian\.net)?\/?$', url)
        return match.group(1) if match else None
