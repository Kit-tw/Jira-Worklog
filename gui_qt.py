import sys
import asyncio

help_flags = {"-h", "--help"}
cli_flags = {"-ga", "-gm", "-m"}
if any(flag in sys.argv for flag in help_flags | cli_flags):
    from util.cli_util import JiraWorklogCLI
    asyncio.run(JiraWorklogCLI().run())
    sys.exit(0)

from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PySide6.QtCore import QTimer

import util.file_util as file_util
import util.common_util as common_util
from constant.Enum import STORAGE
from styles.theme import DARK
from src.jira_add_account_page_qt import AccountPage
from src.worklog_page_qt import WorklogPage


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Worklog")
        self.setFixedSize(1000, 560)
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        days_left = self._check_token()
        if days_left is None or days_left < 0:
            self.show_account_page()
        else:
            self.show_worklog_page()
            if days_left <= 3:
                QTimer.singleShot(300, lambda: QMessageBox.warning(
                    self, "Token Expiry Warning",
                    f"Your Jira API token expires in {days_left} day(s).\nRe-authenticate soon."
                ))

    def show_account_page(self):
        self._set_page(AccountPage(self))

    def show_worklog_page(self):
        self._set_page(WorklogPage(self))

    def _set_page(self, page):
        while self.stack.count():
            w = self.stack.widget(0)
            self.stack.removeWidget(w)
            w.deleteLater()
        self.stack.addWidget(page)

    def _check_token(self) -> int | None:
        try:
            info = file_util.read_json(STORAGE.STORAGE_PATH.value, STORAGE.TOKEN_FILE.value)
            return common_util.days_until_date(info["expire_date"], "%d/%m/%Y")
        except Exception:
            return None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK)
    window = App()
    window.show()
    sys.exit(app.exec())
