import re

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QCheckBox, QMessageBox, QInputDialog, QDateEdit,
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QCursor

import util.common_util as common_util
import util.file_util as file_util
from constant.Enum import STORAGE, REGEX
from util.git_util import GitUtil
from util.jira_util import JiraUtil
from util.sheets_util import SheetsUtil
from util.qt_worker import AsyncWorker
from src.google_api_add_page_qt import GoogleApiPage


class WorklogPage(QWidget):
    def __init__(self, app_window):
        super().__init__()
        self._app = app_window
        self._workers: list[AsyncWorker] = []
        self._issue_name = ""
        self._current_issue_url: str | None = None
        self._google_api_dialog: GoogleApiPage | None = None
        self.jira_util = JiraUtil()
        self.api_credentials = file_util.find(STORAGE.STORAGE_PATH.value, STORAGE.GOOGLE_API_CREDENTIALS_FILE.value)
        self.worklog_history = common_util.get_worklog_history()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 20, 50, 30)
        layout.setSpacing(12)

        layout.addLayout(self._build_header())
        layout.addLayout(self._build_issue_row())

        self.issue_label = QLabel("")
        self.issue_label.setObjectName("issueLink")
        self.issue_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.issue_label.mousePressEvent = self._open_issue_url
        layout.addWidget(self.issue_label)

        layout.addLayout(self._build_form())
        layout.addLayout(self._build_options())
        layout.addStretch()
        layout.addLayout(self._build_footer())

    # ── header ─────────────────────────────────────────────────────────────────

    def _build_header(self):
        row = QHBoxLayout()

        if self.worklog_history:
            lbl = QLabel("History:")
            lbl.setObjectName("historyLabel")
            row.addWidget(lbl)

            self.history_combo = QComboBox()
            self.history_combo.setFixedWidth(300)
            self.history_combo.addItems([item["summary"] for item in self.worklog_history])
            self.history_combo.currentIndexChanged.connect(self._load_from_history)
            row.addWidget(self.history_combo)

            clear_btn = QPushButton("Clear History")
            clear_btn.setObjectName("secondary")
            clear_btn.setFixedHeight(32)
            clear_btn.clicked.connect(self._clear_history)
            row.addWidget(clear_btn)

        row.addStretch()

        help_btn = QPushButton("?")
        help_btn.setObjectName("secondary")
        help_btn.setFixedSize(32, 32)
        help_btn.clicked.connect(self._show_help)
        row.addWidget(help_btn)

        return row

    # ── issue row ──────────────────────────────────────────────────────────────

    def _build_issue_row(self):
        row = QHBoxLayout()
        self.issue_entry = QLineEdit()
        self.issue_entry.setPlaceholderText("Jira Issue URL or Key")
        row.addWidget(self.issue_entry)

        self.fetch_btn = QPushButton("Fetch")
        self.fetch_btn.setFixedWidth(90)
        self.fetch_btn.clicked.connect(lambda: self._fetch_command(self.issue_entry.text().strip()))
        row.addWidget(self.fetch_btn)
        return row

    # ── form ───────────────────────────────────────────────────────────────────

    def _build_form(self):
        layout = QVBoxLayout()
        layout.setSpacing(8)

        date_row = QHBoxLayout()
        date_lbl = QLabel("Date & Time")
        date_lbl.setFixedWidth(110)
        date_row.addWidget(date_lbl)
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setFixedWidth(150)
        date_row.addWidget(self.date_edit)
        self.time_entry = QLineEdit()
        self.time_entry.setPlaceholderText("Time spent  e.g. 3h, 20m, 1h30m")
        date_row.addWidget(self.time_entry)
        layout.addLayout(date_row)

        desc_row = QHBoxLayout()
        desc_lbl = QLabel("Description")
        desc_lbl.setFixedWidth(110)
        desc_row.addWidget(desc_lbl)
        self.description_entry = QLineEdit()
        self.description_entry.setPlaceholderText("Description")
        desc_row.addWidget(self.description_entry)
        layout.addLayout(desc_row)

        return layout

    # ── options ────────────────────────────────────────────────────────────────

    def _build_options(self):
        row = QHBoxLayout()
        row.addWidget(QLabel("Automate Worklog"))

        self.automate_combo = QComboBox()
        self.automate_combo.addItems(["Manual", "Git"])
        self.automate_combo.setFixedWidth(130)
        self.automate_combo.currentTextChanged.connect(self._automate_callback)
        row.addWidget(self.automate_combo)

        row.addStretch()

        self.sheet_checkbox = QCheckBox("Insert to Sheet")
        if self.api_credentials:
            self.sheet_checkbox.setChecked(True)
        self.sheet_checkbox.stateChanged.connect(self._checkbox_callback)
        row.addWidget(self.sheet_checkbox)
        return row

    # ── footer ─────────────────────────────────────────────────────────────────

    def _build_footer(self):
        row = QHBoxLayout()
        self.confirm_btn = QPushButton("Confirm & Log Work")
        self.confirm_btn.setFixedHeight(40)
        self.confirm_btn.clicked.connect(self._insert_worklog)
        row.addWidget(self.confirm_btn)

        reauth_btn = QPushButton("Re-authenticate")
        reauth_btn.setObjectName("secondary")
        reauth_btn.setFixedHeight(40)
        reauth_btn.clicked.connect(self._app.show_account_page)
        row.addWidget(reauth_btn)
        return row

    # ── fetch issue ────────────────────────────────────────────────────────────

    def _fetch_command(self, key: str):
        if not key:
            return
        self.fetch_btn.setEnabled(False)
        self.fetch_btn.setText("Fetching...")
        self.issue_label.setText("Fetching issue...")
        self._issue_name = ""
        self._current_issue_url = None

        worker = AsyncWorker(self.jira_util.fetch_issue(key))
        worker.success.connect(lambda name: self._on_fetch_success(name, key))
        worker.error.connect(self._on_fetch_error)
        self._track(worker)
        worker.start()

    def _on_fetch_success(self, name: str, key: str):
        self.fetch_btn.setEnabled(True)
        self.fetch_btn.setText("Fetch")
        self._issue_name = name
        self.issue_label.setText(f"Issue: {key} — {name}")
        self._current_issue_url = f"{self.jira_util.full_url}/browse/{key}"

    def _on_fetch_error(self, err: Exception):
        self.fetch_btn.setEnabled(True)
        self.fetch_btn.setText("Fetch")
        self.issue_label.setText("")
        QMessageBox.critical(self, "Error", str(err))

    def _open_issue_url(self, _event):
        if self._current_issue_url:
            common_util.open_url(self._current_issue_url)

    # ── history ────────────────────────────────────────────────────────────────

    def _load_from_history(self, index: int):
        if 0 <= index < len(self.worklog_history):
            key = self.worklog_history[index]["key"]
            self.issue_entry.setText(key)
            self._fetch_command(key)

    def _clear_history(self):
        reply = QMessageBox.question(self, "Confirm", "Clear worklog history?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                file_util.delete_file(STORAGE.STORAGE_PATH.value, STORAGE.HISTORY_FILE.value)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
                return
            self.worklog_history = []
            if hasattr(self, "history_combo"):
                self.history_combo.clear()

    # ── insert worklog ─────────────────────────────────────────────────────────

    def _insert_worklog(self):
        issue_key = self.issue_entry.text().strip()
        time_spend = self.time_entry.text().strip()
        date_str = self.date_edit.date().toString("dd/MM/yyyy")
        description = self.description_entry.text().strip()
        is_insert_sheet = self.sheet_checkbox.isChecked()

        if not issue_key:
            QMessageBox.warning(self, "Error", "Issue Key is required.")
            return
        if not time_spend or not re.match(REGEX.DATE.value, date_str):
            QMessageBox.warning(self, "Error", "Date and Time fields are required.")
            return

        date_iso = common_util.date_str_to_iso(date_str)
        self.confirm_btn.setEnabled(False)
        self.confirm_btn.setText("Processing...")

        async def process_insert():
            if not self._issue_name:
                self._issue_name = await self.jira_util.fetch_issue(issue_key)
            await self.jira_util.post_insert_worklog(issue_key, time_spend, date_iso, description)
            return self._issue_name

        worker = AsyncWorker(process_insert())
        worker.success.connect(
            lambda name: self._on_insert_success(name, issue_key, date_str, time_spend, description, is_insert_sheet)
        )
        worker.error.connect(self._on_insert_error)
        self._track(worker)
        worker.start()

    def _on_insert_success(self, name: str, key: str, date: str, time: str, desc: str, insert_sheet: bool):
        self._issue_name = name
        self.confirm_btn.setEnabled(True)
        self.confirm_btn.setText("Confirm & Log Work")
        if insert_sheet:
            self._insert_to_sheet(key, date, time, desc)
        self._save_history(key)

        msg = QMessageBox(self)
        msg.setWindowTitle("Success")
        msg.setText("Worklog inserted successfully!")
        msg.setIcon(QMessageBox.Icon.Information)
        view_btn = msg.addButton("View in Jira", QMessageBox.ButtonRole.ActionRole)
        msg.addButton(QMessageBox.StandardButton.Ok)
        msg.exec()
        if msg.clickedButton() == view_btn:
            common_util.open_url(f"{self.jira_util.full_url}/browse/{key}")

    def _on_insert_error(self, err: Exception):
        self.confirm_btn.setEnabled(True)
        self.confirm_btn.setText("Confirm & Log Work")
        QMessageBox.critical(self, "Error", str(err))

    def _insert_to_sheet(self, key: str, date: str, time: str, desc: str):
        if not self.api_credentials:
            msg = QMessageBox(self)
            msg.setWindowTitle("Warning")
            msg.setText("Google API credentials not found.")
            add_btn = msg.addButton("Add Credentials", QMessageBox.ButtonRole.ActionRole)
            msg.addButton(QMessageBox.StandardButton.Cancel)
            msg.exec()
            if msg.clickedButton() == add_btn:
                self._open_google_api_dialog()
            return
        try:
            SheetsUtil().insert(key=key, date=date, time=time, description=desc)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _save_history(self, key: str):
        if any(item["key"] == key for item in self.worklog_history):
            return
        entry = {"key": key, "name": self._issue_name, "summary": f"{key} : {self._issue_name}"}
        self.worklog_history.append(entry)
        try:
            file_util.save_json(STORAGE.STORAGE_PATH.value, STORAGE.HISTORY_FILE.value, self.worklog_history)
        except Exception:
            pass
        if hasattr(self, "history_combo"):
            self.history_combo.addItem(entry["summary"])

    # ── git autofill ───────────────────────────────────────────────────────────

    def _automate_callback(self, choice: str):
        if choice == "Git":
            self._git_insert_entry()

    def _git_insert_entry(self):
        self.automate_combo.setEnabled(False)
        git_util = GitUtil()

        async def process_git():
            key = git_util.get_issueName()
            await self.jira_util.fetch_issue(key)
            return key, git_util.get_git_detail()

        worker = AsyncWorker(process_git())
        worker.success.connect(self._on_git_success)
        worker.error.connect(self._on_git_error)
        self._track(worker)
        worker.start()

    def _on_git_success(self, result):
        self.automate_combo.setEnabled(True)
        key, obj = result
        self.issue_entry.setText(key)
        self.date_edit.setDate(QDate.fromString(obj["date"], "dd/MM/yyyy"))
        self.description_entry.setText(obj.get("description", ""))
        self._fetch_command(key)

        time_str = obj.get("time_spend", "")
        if obj.get("time_spend_minutes", 0) < common_util.get_min_time_spend():
            reply = QMessageBox.question(self, "Confirm", f"Add {time_str} to worklog?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.time_entry.setText(time_str)
            else:
                text, ok = QInputDialog.getText(self, "Time Spent", "Enter time spent (e.g. 15m, 1h):")
                self.time_entry.setText(text if ok and text else "")
        else:
            self.time_entry.setText(time_str)

    def _on_git_error(self, err: Exception):
        self.automate_combo.setEnabled(True)
        self.automate_combo.setCurrentText("Manual")
        QMessageBox.critical(self, "Error", str(err))

    # ── google api dialog ──────────────────────────────────────────────────────

    def _open_google_api_dialog(self):
        if self._google_api_dialog is None or not self._google_api_dialog.isVisible():
            self._google_api_dialog = GoogleApiPage(self)
            self._google_api_dialog.show()
        else:
            self._google_api_dialog.raise_()

    # ── checkbox callback ──────────────────────────────────────────────────────

    def _checkbox_callback(self, state: int):
        if state and not self.api_credentials:
            msg = QMessageBox(self)
            msg.setWindowTitle("Warning")
            msg.setText("Google API credentials not found.")
            add_btn = msg.addButton("Add Credentials", QMessageBox.ButtonRole.ActionRole)
            msg.addButton(QMessageBox.StandardButton.Cancel)
            msg.exec()
            if msg.clickedButton() == add_btn:
                self._open_google_api_dialog()
            else:
                self.sheet_checkbox.setChecked(False)

    def _show_help(self):
        QMessageBox.information(
            self, "Help",
            "Automate Worklog:\n"
            "  Manual — fill in all fields yourself\n"
            "  Git    — reads issue key & time from current branch\n\n"
            "Insert to Sheet — syncs the entry to Google Sheets\n"
            "                  (requires Google API credentials)\n\n"
            "Fetch — retrieves the issue name from Jira to confirm\n"
            "        the key is valid before logging."
        )

    # ── worker lifecycle ───────────────────────────────────────────────────────

    def _track(self, worker: AsyncWorker):
        self._workers.append(worker)
        worker.finished.connect(lambda: self._workers.remove(worker) if worker in self._workers else None)
