import asyncio
import re
import threading

import customtkinter as ctk
from PIL import Image
from ctkdateentry import CTkDateEntry

import util.common_util as common_util
import util.file_util as file_util
from constant.Enum import TEXTSIZE, WIDGET, REGEX, STORAGE
from src.google_api_add_page import GoogleApiPage
from src.tooltip_toplevel import ToolTip
from util.git_util import GitUtil
from util.gui_util import GuiUtil
from util.jira_util import JiraUtil
from util.sheets_util import SheetsUtil


class WorkLog(ctk.CTkFrame):
    ROW_TOOLTIP = 0
    ROW_INPUT = 1
    ROW_ISSUE = 2
    ROW_TIME = 3
    ROW_DATE = 4
    ROW_OPTIONS = 5
    ROW_FOOTER = 6
    MAX_COL_SPAN = 3
    PLACEHOLDER_URL = "Jira Issue URL or Key"
    PLACEHOLDER_TIME = "Time spend e.g. 3h, 20m, 16s"
    PLACEHOLDER_DESCRIPTION = "Description"

    def __init__(self, parent):
        super().__init__(parent)
        self.jira_util = JiraUtil()
        self.gui_util = GuiUtil(self)
        self.api_credentials = file_util.find(STORAGE.STORAGE_PATH.value, STORAGE.GOOGLE_API_CREDENTIALS_FILE.value)
        self.toplevel_google_api = None
        self.tooltip_toplevel = None
        self.issue_name = ""
        self.current_issue_url = None
        self.key_var = ctk.StringVar(self)
        self.date_var = ctk.StringVar(self, value=common_util.get_currentdate_forentry())
        self.time_var = ctk.StringVar(self)
        self.description_var = ctk.StringVar(self)
        self.worklog_history = common_util.get_worklog_history()
        self._history_widgets_created = False
        self.header_frame()
        self.input_frame()
        self.body()
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure((1, 2, 3), weight=2)

    def run_in_background(self, coroutine, success_callback=None, error_callback=None):
        def thread_target():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(coroutine)
                if success_callback:
                    self.after(0, lambda: success_callback(result))
            except Exception as e:
                self.after(0, lambda: self.gui_util.show_dialog("Error", "cancel", str(e), options="OK"))
            finally:
                loop.close()
        threading.Thread(target=thread_target, daemon=True).start()

    # ── header ───────────────────────────────────────────────────────────────

    def header_frame(self):
        self._header_tooltip()
        self._header_history()

    def _header_tooltip(self):
        img_path = file_util.find(STORAGE.IMAGE_PATH.value, STORAGE.TOOLTIP_IMAGE.value)
        img = ctk.CTkImage(light_image=Image.open(img_path), dark_image=Image.open(img_path), size=(30, 30))
        label = ctk.CTkLabel(self, image=img, text="", cursor="hand2")
        label.image = img
        label.bind("<Button-1>", lambda e: self.open_tooltip_toplevel())
        label.grid(row=self.ROW_TOOLTIP, column=self.MAX_COL_SPAN, sticky="nesw", pady=WIDGET.PAD_Y.value)

    def _header_history(self):
        if len(self.worklog_history) == 0:
            return
        history_dropdown = [item["summary"] for item in self.worklog_history]
        if self._history_widgets_created:
            self._worklog_combobox.configure(values=history_dropdown)
            self._history_label.grid()
            self._worklog_combobox.grid()
            self._clear_history_btn.grid()
            return
        self._history_label = self.gui_util.create_normal_label(
            self, "Worklog History", TEXTSIZE.TEXT_X_SM, self.ROW_TOOLTIP, 0,
            grid_args={"padx": WIDGET.PAD_X.value, "pady": WIDGET.PAD_Y.value},
        )
        self._worklog_combobox = ctk.CTkComboBox(
            self, values=history_dropdown, width=300, height=WIDGET.HEIGHT.value,
            command=lambda e: self._open_worklog_from_history(self._worklog_combobox),
            font=self.gui_util.font(TEXTSIZE.TEXT_X_SM.value, underline=True),
        )
        self._worklog_combobox.grid(row=self.ROW_TOOLTIP, column=1, sticky="n", padx=10, pady=WIDGET.PAD_Y.value)
        self._worklog_combobox.configure(text_color="#75add8")
        self._clear_history_btn = ctk.CTkButton(
            self, text="Clear History", command=self.clear_history, height=WIDGET.HEIGHT.value
        )
        self._clear_history_btn.grid(row=self.ROW_TOOLTIP, column=2, sticky="w", pady=WIDGET.PAD_Y.value)
        self._history_widgets_created = True

    def clear_history(self):
        dialog = self.gui_util.show_dialog(
            "Confirm", "warning", "Clear worklog history?", option_1="Yes", option_2="No"
        )
        if dialog.get() == "Yes":
            try:
                file_util.delete_file(STORAGE.STORAGE_PATH.value, STORAGE.HISTORY_FILE.value)
            except Exception as e:
                self.gui_util.show_dialog("Error", "cancel", str(e), options="OK")
                return
            self._history_label.grid_remove()
            self._worklog_combobox.grid_remove()
            self._clear_history_btn.grid_remove()
            self.worklog_history = []

    def _open_worklog_from_history(self, combobox: ctk.CTkComboBox):
        for item in self.worklog_history:
            if item["summary"] == combobox.get():
                self._current_history_url = self.get_jira_url(item["key"])
                if not getattr(self, '_history_bound', False):
                    combobox.bind("<Button-1>", lambda e: common_util.open_url(self._current_history_url))
                    self._history_bound = True
                self.key_var.set(item["key"])
                self.fetch_command(item["key"])
                break

    # ── input row ────────────────────────────────────────────────────────────

    def input_frame(self):
        self.jira_url_entry = self.gui_util.create_entry_with_placeholder(
            self, self.PLACEHOLDER_URL, self.key_var, self.ROW_INPUT, 0,
            entry_args={"width": WIDGET.WIDTH.value, "height": WIDGET.HEIGHT.value},
            grid_args={"sticky": "ew", "padx": WIDGET.PAD_X.value, "pady": WIDGET.PAD_Y.value, "columnspan": self.MAX_COL_SPAN},
        )
        self.fetch_btn = ctk.CTkButton(
            self, text="fetch",
            command=lambda: self.fetch_command(self.jira_url_entry.get().strip()),
            height=WIDGET.HEIGHT.value,
        )
        self.fetch_btn.grid(row=self.ROW_INPUT, column=3, sticky='ew', padx=WIDGET.PAD_X.value, pady=WIDGET.PAD_Y.value)

    def fetch_command(self, key: str):
        key = key.strip()
        if not key:
            return
        self.fetch_btn.configure(state="disabled", text="fetching...")
        self.issue_label.configure(text="Fetching issue...", cursor="arrow")
        self.issue_name = ""
        self.current_issue_url = None

        def on_success(name):
            self.fetch_btn.configure(state="normal", text="fetch")
            self.issue_name = name
            self.issue_label.configure(text=f"Issue Name : {name}", cursor="hand2")
            self.current_issue_url = self.get_jira_url(key)

        def on_error(err):
            self.fetch_btn.configure(state="normal", text="fetch")
            self.issue_label.configure(text="", cursor="arrow")
            self.gui_util.show_dialog("Error", "cancel", str(err), options="OK")

        self.run_in_background(self.jira_util.fetch_issue(key), on_success, on_error)

    # ── body ─────────────────────────────────────────────────────────────────

    def body(self):
        self.issue_label = self.gui_util.create_normal_label(
            self, "", TEXTSIZE.TEXT_X_SM, self.ROW_ISSUE, 0,
            label_args={"text_color": "#75add8"},
            grid_args={"sticky": "nsew", "columnspan": self.MAX_COL_SPAN},
        )
        self.issue_label.bind(
            "<Button-1>",
            lambda e: common_util.open_url(self.current_issue_url) if self.current_issue_url else None,
        )

        self.gui_util.create_normal_label(
            self, "Date & Time", TEXTSIZE.TEXT_SM, self.ROW_TIME, 0,
            grid_args={"padx": WIDGET.PAD_X.value, "pady": WIDGET.PAD_Y.value},
        )
        CTkDateEntry(self, variable=self.date_var, height=WIDGET.HEIGHT.value).grid(
            row=self.ROW_TIME, column=1, sticky='ew', padx=WIDGET.PAD_X.value
        )
        self.time_spend_entry = self.gui_util.create_entry_with_placeholder(
            self, self.PLACEHOLDER_TIME, self.time_var, self.ROW_TIME, 2,
            entry_args={"height": WIDGET.HEIGHT.value},
            grid_args={"sticky": "ew", "padx": WIDGET.PAD_X.value, "pady": WIDGET.PAD_Y.value, "columnspan": self.MAX_COL_SPAN},
        )

        self.gui_util.create_normal_label(
            self, "Description", TEXTSIZE.TEXT_SM, self.ROW_DATE, 0,
            grid_args={"padx": WIDGET.PAD_X.value},
        )
        self.description_entry = self.gui_util.create_entry_with_placeholder(
            self, self.PLACEHOLDER_DESCRIPTION, self.description_var, self.ROW_DATE, 1,
            entry_args={"height": WIDGET.HEIGHT.value},
            grid_args={"sticky": "ew", "padx": WIDGET.PAD_X.value, "columnspan": self.MAX_COL_SPAN, "pady": WIDGET.PAD_Y.value},
        )

        self.gui_util.create_normal_label(
            self, "Automate Worklog", TEXTSIZE.TEXT_SM, self.ROW_OPTIONS, 0,
            grid_args={"padx": WIDGET.PAD_X.value, "pady": WIDGET.PAD_Y.value},
        )
        self.automate_options = ctk.CTkComboBox(
            self, values=["Manual", "Git"], command=self._automate_callback, height=WIDGET.HEIGHT.value
        )
        self.automate_options.grid(row=self.ROW_OPTIONS, column=1, padx=WIDGET.PAD_X.value, pady=WIDGET.PAD_Y.value)

        self.insert_sheet = ctk.CTkCheckBox(
            self, text="Insert to sheet",
            font=self.gui_util.font(TEXTSIZE.TEXT_X_SM.value),
            command=self._checkbox_callback,
        )
        self.insert_sheet.grid(row=self.ROW_OPTIONS, column=2, columnspan=2, padx=WIDGET.PAD_X.value, pady=WIDGET.PAD_Y.value)
        if self.api_credentials:
            self.insert_sheet.select()

        self.confirm_btn = ctk.CTkButton(
            self, text="Confirm & Log Work", height=WIDGET.HEIGHT.value, command=self.insert_worklog
        )
        self.confirm_btn.grid(row=self.ROW_FOOTER, column=0, columnspan=1, sticky='w', padx=WIDGET.PAD_X.value, pady=WIDGET.PAD_Y.value)

    # ── worklog submission ────────────────────────────────────────────────────

    def insert_worklog(self):
        time_spend = self.time_spend_entry.get()
        date = self.date_var.get()
        description = self.description_entry.get()
        issue_key = self.jira_url_entry.get().strip()
        is_insert_sheet = self.insert_sheet.get()

        if not issue_key:
            self.gui_util.show_dialog("Error", "cancel", "Issue Key is required", options="OK")
            return
        if not time_spend or not re.match(REGEX.DATE.value, date):
            self.gui_util.show_dialog("Error", "cancel", "Date and Time fields are required", options="OK")
            return

        date_iso = common_util.date_str_to_iso(date)
        self.confirm_btn.configure(state="disabled", text="Processing...")

        async def process_insert():
            if not self.issue_name:
                self.issue_name = await self.jira_util.fetch_issue(issue_key)
            await self.jira_util.post_insert_worklog(issue_key, time_spend, date_iso, description)
            return self.issue_name

        def on_success(name):
            self.issue_name = name
            self.confirm_btn.configure(state="normal", text="Confirm & Log Work")
            if is_insert_sheet:
                self._insert_to_sheet(issue_key, date, time_spend, description)
            self._save_history()
            dialog = self.gui_util.show_dialog(
                "Success", "check", "Worklog inserted!", option_1="OK", option_2="View in Jira"
            )
            if dialog.get() == "View in Jira":
                common_util.open_url(self.get_jira_url(issue_key))

        def on_error(err):
            self.confirm_btn.configure(state="normal", text="Confirm & Log Work")
            self.gui_util.show_dialog("Error", "cancel", str(err), options="OK")

        self.run_in_background(process_insert(), on_success, on_error)

    def _insert_to_sheet(self, issue_key: str, date: str, time_spend: str, description: str):
        if not self.api_credentials:
            dialog = self.gui_util.show_dialog(
                "Warning", "warning", "Google API credentials not found", option_1="Add", option_2="Exit"
            )
            if dialog.get() == "Add":
                self.open_googleapi_toplevel()
            return
        try:
            SheetsUtil().insert(key=issue_key, date=date, time=time_spend, description=description)
        except Exception as e:
            self.gui_util.show_dialog("Error", "cancel", str(e), options="OK")

    def _save_history(self):
        issue_key = self.key_var.get()
        if any(item["key"] == issue_key for item in self.worklog_history):
            return
        entry = {"key": issue_key, "name": self.issue_name, "summary": f"{issue_key} : {self.issue_name}"}
        self.worklog_history.append(entry)
        try:
            file_util.save_json(STORAGE.STORAGE_PATH.value, STORAGE.HISTORY_FILE.value, self.worklog_history)
        except Exception:
            pass
        self._header_history()

    # ── git autofill ──────────────────────────────────────────────────────────

    def _automate_callback(self, choice: str):
        if choice == "Git":
            self._git_insert_entry()

    def _git_insert_entry(self):
        self.automate_options.set("Processing...")
        git_util = GitUtil()

        async def process_git():
            key = git_util.get_issueName()
            await self.jira_util.fetch_issue(key)
            return key, git_util.get_git_detail()

        def on_success(result):
            self.automate_options.set("Git")
            key, obj = result
            self.key_var.set(key)
            self.date_var.set(obj["date"])
            self.description_var.set(obj["description"])
            self.fetch_command(key)

            time_spend_mins = obj.get("time_spend_minutes", 0)
            time_spend_str = obj.get("time_spend", "")
            if time_spend_mins < common_util.get_min_time_spend():
                dialog = self.gui_util.show_dialog(
                    "Confirm", "warning", f"Add {time_spend_str} to worklog?",
                    option_1="Yes", option_2="No",
                )
                if dialog.get() == "Yes":
                    self.time_var.set(time_spend_str)
                else:
                    d = ctk.CTkInputDialog(text="Enter time spent (e.g. 15m, 1h):", title="Time Spent")
                    user_input = d.get_input()
                    self.time_var.set(user_input if user_input else self.PLACEHOLDER_TIME)
            else:
                self.time_var.set(time_spend_str)

        def on_error(err):
            self.automate_options.set("Git")
            self.gui_util.show_dialog("Error", "cancel", str(err), options="OK")

        self.run_in_background(process_git(), on_success, on_error)

    # ── overlays / helpers ────────────────────────────────────────────────────

    def get_jira_url(self, key: str) -> str:
        return self.jira_util.full_url + "/browse/" + key

    def open_googleapi_toplevel(self):
        if self.toplevel_google_api is None or not self.toplevel_google_api.winfo_exists():
            self.toplevel_google_api = GoogleApiPage(self)
        else:
            self.toplevel_google_api.focus()

    def open_tooltip_toplevel(self):
        if self.tooltip_toplevel is None or not self.tooltip_toplevel.winfo_exists():
            self.tooltip_toplevel = ToolTip(self)
        else:
            self.tooltip_toplevel.focus()

    def _checkbox_callback(self):
        if self.insert_sheet.get() and self.toplevel_google_api is None and not self.api_credentials:
            dialog = self.gui_util.show_dialog(
                "Warning", "warning", "Google API credentials not found", option_1="Add", option_2="Exit"
            )
            if dialog.get() == "Add":
                self.open_googleapi_toplevel()
            else:
                self.insert_sheet.deselect()
