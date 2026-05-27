import re
import customtkinter as ctk

import util.common_util as common_util
import util.file_util as file_util
from constant.Enum import TEXTSIZE, STORAGE, URL, WIDGET
from util.gui_util import GuiUtil


class ApiPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.gui_util = GuiUtil(self)
        self.show_title()
        self.body()
        self.submit_button()

    def show_title(self):
        ctk.CTkLabel(self, text="How to get API token", font=self.gui_util.font(TEXTSIZE.TEXT_LG.value)).grid(
            row=0, column=0, padx=WIDGET.PAD_X.value, pady=WIDGET.PAD_Y.value
        )

    def body(self):
        self.step_frame()
        self.input_frame()

    def step_frame(self):
        step_frame = ctk.CTkFrame(self, fg_color="transparent")
        step_frame.grid(row=1, column=0, padx=WIDGET.PAD_X.value, pady=WIDGET.PAD_Y.value)
        steps = [
            "1. Go to Atlassian Account",
            "2. Click create API token",
            "3. Enter name and expiration date then create",
            "4. Click copy and paste in input field",
        ]
        for idx, text in enumerate(steps):
            if idx == 0:
                label = self.gui_util.create_hyperlink_label(
                    step_frame, text, TEXTSIZE.TEXT_SM, idx, 0,
                    grid_args={"sticky": "w", "padx": WIDGET.PAD_X.value, "pady": 10},
                )
                label.bind("<Button-1>", lambda e: common_util.open_url(URL.JIRA_GET_API_URL.value))
            else:
                self.gui_util.create_normal_label(
                    step_frame, text, TEXTSIZE.TEXT_SM, idx, 0,
                    grid_args={"sticky": "w", "padx": WIDGET.PAD_X.value, "pady": 10},
                )

    def input_frame(self):
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.grid(row=1, column=1, padx=WIDGET.PAD_X.value, pady=WIDGET.PAD_Y.value)
        ctk.CTkLabel(input_frame, text="Jira Account Setup", font=self.gui_util.font(TEXTSIZE.TEXT_MD.value)).grid(
            row=0, column=0, pady=5
        )
        self.email_entry = ctk.CTkEntry(input_frame, placeholder_text="e.g. example@gmail.com", width=300, height=WIDGET.HEIGHT.value)
        self.email_entry.grid(row=1, column=0, pady=5)
        self.api_token_entry = ctk.CTkEntry(input_frame, placeholder_text="API token", width=300, height=WIDGET.HEIGHT.value, show="*")
        self.api_token_entry.grid(row=2, column=0, pady=5)
        self.jira_url_entry = ctk.CTkEntry(input_frame, placeholder_text="Jira Site e.g. company.atlassian.net", width=300, height=WIDGET.HEIGHT.value)
        self.jira_url_entry.grid(row=3, column=0, pady=5)
        self.expire_date_entry = ctk.CTkEntry(input_frame, placeholder_text="Expiry date: dd/mm/yyyy", width=300, height=WIDGET.HEIGHT.value)
        self.expire_date_entry.grid(row=4, column=0, pady=5)

    def submit_button(self):
        ctk.CTkButton(self, text="Confirm", command=self.store_api).grid(
            row=2, column=0, sticky="nsew", padx=100, pady=10
        )

    def store_api(self):
        email = self.email_entry.get()
        api = self.api_token_entry.get()
        url = self.jira_url_entry.get()
        expire_date = self.expire_date_entry.get()

        if not all([email, api, url, expire_date]):
            self.gui_util.show_dialog("Error", "cancel", "Please fill in all fields.", options="OK")
            return

        prefix = self._get_prefix(url)
        if not prefix:
            self.gui_util.show_dialog("Error", "cancel", "Invalid Jira site URL.", options="OK")
            return

        response = common_util.get_user(email, api, prefix)
        if response.status_code != 200:
            self.gui_util.show_dialog("Error", "cancel", "Cannot authenticate with the provided credentials.", options="OK")
            return

        data = {"jira_email": email, "jira_api": api, "jira_prefix": prefix, "expire_date": expire_date}
        try:
            file_util.save_json(STORAGE.STORAGE_PATH.value, STORAGE.TOKEN_FILE.value, data)
        except Exception as e:
            self.gui_util.show_dialog("Error", "cancel", f"Failed to save credentials: {e}", options="OK")
            return

        self.after(0, self.master.show_worklog_page)

    def _get_prefix(self, url: str) -> str | None:
        match = re.match(r'^(?:https?:\/?\/?)?([a-zA-Z0-9-]+)(?:\.atlassian\.net)?\/?$', url)
        return match.group(1) if match else None
