import os
import subprocess
import customtkinter as ctk

import util.common_util as common_util
import util.file_util as file_util
from constant.Enum import STORAGE, WIDGET
from util.jira_util import JiraUtil


class ToolTip(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Information")
        self.transient(parent)
        self.resizable(width=False, height=False)
        self.jira_info = JiraUtil()
        self._build()

    def _build(self):
        rows = [
            ("Jira Email", self.jira_info.mail, None),
            ("Jira Site", self.jira_info.prefix_url, lambda: common_util.open_url(self.jira_info.full_url)),
            ("Store path", STORAGE.STORAGE_PATH.value, lambda: self._open_explorer(STORAGE.STORAGE_PATH.value)),
        ]
        if file_util.find(STORAGE.STORAGE_PATH.value, STORAGE.INFORMATION_FILE.value):
            try:
                info = file_util.read_json(STORAGE.STORAGE_PATH.value, STORAGE.INFORMATION_FILE.value)
                sheet_url = f"https://docs.google.com/spreadsheets/d/{info['spreadsheetId']}"
                rows.append(("Google Sheet", "Open", lambda u=sheet_url: common_util.open_url(u)))
            except Exception:
                pass
        self._render_rows(rows)

    def _render_rows(self, rows: list):
        for idx, (key, value, action) in enumerate(rows):
            ctk.CTkLabel(self, text=key).grid(row=idx, column=0, padx=WIDGET.PAD_X.value)
            val_label = ctk.CTkLabel(self, text=value)
            if callable(action):
                val_label.bind("<Button-1>", lambda e, fn=action: fn())
                val_label.configure(cursor="hand2", text_color="#1f6aa5")
            val_label.grid(row=idx, column=1, padx=WIDGET.PAD_X.value)

    def _open_explorer(self, path: str):
        path = os.path.normpath(path.strip())
        if os.path.isdir(path):
            subprocess.Popen(['explorer', path])
        elif os.path.isfile(path):
            subprocess.Popen(['explorer', '/select,', path])
