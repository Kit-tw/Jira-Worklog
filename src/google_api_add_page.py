import re
import customtkinter as ctk
from customtkinter import filedialog

import util.common_util as common_util
import util.file_util as file_util
from constant.Enum import STORAGE, TEXTSIZE, URL, WIDGET
from util.gui_util import GuiUtil


class GoogleApiPage(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.geometry("1000x500")
        self.title("API GOOGLE")
        self.transient(parent)
        self.resizable(width=False, height=False)
        self.gui_util = GuiUtil(self)
        self._header_ui()
        self.body()
        self.input_frame()
        self.grid_columnconfigure((0, 1), weight=1)

    def _header_ui(self):
        self.gui_util.create_normal_label(
            self, "How to get API token", TEXTSIZE.TEXT_MD, 0, 0,
            grid_args={"padx": WIDGET.PAD_X.value, "pady": WIDGET.PAD_Y.value},
        )
        hyperlink = self.gui_util.create_hyperlink_label(
            self, "Reference Documentation", TEXTSIZE.TEXT_SM, 0, 1,
            grid_args={"pady": WIDGET.PAD_Y.value},
        )
        hyperlink.bind("<Button-1>", lambda e: common_util.open_url(URL.GSPREAD_GOOGLE_API_DOC.value))

    def body(self):
        self.step_frame()

    def step_frame(self):
        step_frame = ctk.CTkFrame(self, fg_color="transparent")
        step_frame.grid(row=1, column=0, padx=WIDGET.PAD_X.value, pady=WIDGET.PAD_Y.value)
        steps = [
            "1. Go to Google Developer Console",
            "2. Create project and enable Google Sheets, Drive API, then create OAuth client ID credentials",
            "3. Add test user email in Audience when creating credential",
            "4. Download the credential and upload to this app",
        ]
        for idx, text in enumerate(steps):
            if idx == 0:
                label = self.gui_util.create_hyperlink_label(
                    step_frame, text, TEXTSIZE.TEXT_X_SM, idx, 0,
                    grid_args={"sticky": "w", "pady": 10},
                )
                label.bind("<Button-1>", lambda e: common_util.open_url(URL.GOOGLE_DEVELOPER_CONSOLE.value))
            else:
                self.gui_util.create_normal_label(
                    step_frame, text, TEXTSIZE.TEXT_X_SM, idx, 0,
                    grid_args={"sticky": "w", "pady": 10},
                )

    def input_frame(self):
        ctk.CTkButton(self, text="Choose File", command=self.select_file, width=200, height=WIDGET.HEIGHT.value).grid()

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.JSON")])
        if not file_path:
            return
        dest_path = STORAGE.GOOGLE_API_CREDENTIALS_PATH.value
        if self._validate_credential(file_path):
            try:
                file_util.copy_file(file_path, dest_path)
                self.destroy()
            except Exception as e:
                self.gui_util.show_dialog("Error", "cancel", f"Failed to copy file: {e}", options="OK")

    def _validate_credential(self, file_path: str) -> bool:
        try:
            data = file_util.read_json_by_path(file_path)
            if data is not None and re.search(r"(client_id).*(project_id)", str(data)):
                return True
            raise ValueError("Missing required fields")
        except Exception:
            self.gui_util.show_dialog(
                "Error", "cancel",
                "Invalid credential file. Please use a valid OAuth client ID JSON.",
                options="OK",
            )
            return False
