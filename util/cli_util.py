import os
import re
import json
import sys

import util.file_util as file_util
import util.common_util as common_util
from constant.Enum import STORAGE
from util.git_util import GitUtil
from util.jira_util import JiraUtil


class JiraWorklogCLI:
    def __init__(self):
        self.git_util = GitUtil()
        self.jira_util = JiraUtil()
        self.has_sheets = os.path.exists(STORAGE.GOOGLE_API_CREDENTIALS_PATH.value)

    async def run(self):
        print("\nInitializing Jira Worklog CLI...")
        args = sys.argv[1:]

        if "-h" in args or "--help" in args:
            self._print_help()
            return

        if not self._validate_credentials():
            return

        if "-ga" in args:
            await self.handle_auto_git()
        elif "-gm" in args:
            await self.handle_git_manual_issue(self._extract_gm_key(args))
        elif "-m" in args:
            await self.handle_manual_all()
        else:
            print("Error: Unknown flag. Use -ga, -gm [KEY], or -m")
            print("Run with -h or --help for usage.")

    # ── credential validation ────────────────────────────────────────────────

    def _validate_credentials(self) -> bool:
        token_path = os.path.join(STORAGE.STORAGE_PATH.value, STORAGE.TOKEN_FILE.value)
        if not os.path.exists(token_path):
            print(f"Error: Jira token not found at '{token_path}'. Configure via the GUI first.")
            return False
        try:
            token_info = file_util.read_json_by_path(token_path)
        except Exception as e:
            print(f"Error reading token file: {e}")
            return False
        days_left = common_util.days_until_date(token_info["expire_date"], "%d/%m/%Y")
        if days_left < 0:
            print("Error: Jira API token has expired. Re-authenticate via the GUI.")
            return False
        if days_left <= 3:
            print(
                "\033[1;33m"
                f"[WARNING] Jira API token expires in {days_left} day(s). Re-authenticate via the GUI soon."
                "\033[0m"
            )
        return True

    def _print_help(self) -> None:
        print(
            "\nUsage: gui.py [FLAG] [OPTIONS]\n"
            "\nFlags:\n"
            "  -ga            Auto Git     — reads issue key and time from current branch\n"
            "  -gm [KEY]      Git Manual   — uses git time, you provide the issue key\n"
            "  -m             Manual       — enter all fields manually\n"
            "  -h, --help     Show this help message\n"
            "\nExamples:\n"
            "  python gui.py -ga\n"
            "  python gui.py -gm PROJECT-123\n"
            "  python gui.py -m\n"
            "\nNo flag: launches the GUI."
        )

    # ── arg parsing ──────────────────────────────────────────────────────────

    def _extract_gm_key(self, args: list) -> str | None:
        idx = args.index("-gm")
        candidate = args[idx + 1] if idx + 1 < len(args) else None
        return candidate if candidate and not candidate.startswith("-") else None

    # ── issue resolution ─────────────────────────────────────────────────────

    async def _prompt_and_fetch_issue(self, default_key: str = None) -> tuple[str, str]:
        """Interactive loop: prompt for issue key, fetch from Jira, return (key, name)."""
        while True:
            prompt = f"Issue Key [{default_key}]: " if default_key else "Issue Key: "
            user_key = input(prompt).strip()
            current_key = user_key if user_key else default_key
            if not current_key:
                print("Error: Issue key cannot be empty.")
                continue
            try:
                print(f"Fetching '{current_key}'...")
                issue_name = await self.jira_util.fetch_issue(current_key)
                print(f"Jira Issue Found: {issue_name}")
                return current_key, issue_name
            except Exception as e:
                print(f"Error: {e}")
                if input("Re-enter issue key? (y/n) [y]: ").strip().lower() == 'n':
                    return current_key, ""

    async def _resolve_issue_from_arg(self, arg_key: str, fallback_key: str = None) -> tuple[str, str]:
        """Try arg_key first; fall back to interactive prompt with fallback_key as default."""
        if arg_key:
            try:
                print(f"Fetching '{arg_key}'...")
                name = await self.jira_util.fetch_issue(arg_key)
                print(f"Jira Issue Found: {name}")
                return arg_key, name
            except Exception as e:
                print(f"Warning: {e}")
        return await self._prompt_and_fetch_issue(fallback_key)

    # ── shared field prompts ─────────────────────────────────────────────────

    def _check_time_threshold(self, default_time: str, time_spend_mins: int) -> str:
        min_time = common_util.get_min_time_spend()
        if time_spend_mins < min_time:
            print(
                "\033[1;33m"
                "================================================================================\n"
                "[WARNING] Calculated time is below the minimum threshold.\n"
                "================================================================================\033[0m"
            )
            confirm = input(f"\033[1;33mAdd {default_time} to worklog? (y/n) [y]: \033[0m").strip().lower()
            if confirm in ('n', 'no'):
                while True:
                    t = input("Enter time spent (e.g. 3h, 20m): ").strip()
                    if t:
                        return t
                    print("Error: Time spent cannot be empty.")
        return default_time

    def _prompt_fields(self,
                       default_date: str,
                       default_time: str,
                       default_comment: str,
                       time_spend_mins: int = 0) -> tuple[str, str, str]:
        """Prompt user to confirm or edit date, time, and comment. Returns final values."""
        print("\n==================================================")
        print("              JIRA WORKLOG EDITOR                 ")
        print("==================================================")
        print("Press [Enter] to accept the value in brackets.\n")

        if default_time and time_spend_mins:
            default_time = self._check_time_threshold(default_time, time_spend_mins)

        while True:
            user_date = input(f"Date (dd/mm/yyyy) [{default_date}]: ").strip()
            date_val = user_date if user_date else default_date
            if re.match(r'^\d{2}/\d{2}/\d{4}$', date_val):
                break
            print("Error: Use dd/mm/yyyy format.")

        while True:
            time_hint = f" [{default_time}]" if default_time else ""
            user_time = input(f"Time spent (e.g. 3h, 20m){time_hint}: ").strip()
            time_val = user_time if user_time else default_time
            if time_val:
                break
            print("Error: Time spent cannot be empty.")

        comment_hint = f" [{default_comment}]" if default_comment else ""
        user_comment = input(f"Comment{comment_hint}: ").strip()
        comment_val = user_comment if user_comment else default_comment

        return date_val, time_val, comment_val

    def _print_summary(self, issue_key: str, issue_name: str, date_val: str, time_val: str, comment_val: str) -> None:
        print("\n--- Summary ---")
        print(f"Issue Key  : {issue_key}")
        print(f"Issue Name : {issue_name or 'N/A'}")
        print(f"Date       : {date_val}")
        print(f"Time Spent : {time_val}")
        print(f"Comment    : {comment_val}")
        sheets_status = "configured" if self.has_sheets else "not configured"
        print(f"Sheets     : {sheets_status}")

    # ── submission ───────────────────────────────────────────────────────────

    async def _submit(self, issue_key: str, issue_name: str, date_val: str, time_val: str, comment_val: str) -> None:
        self._print_summary(issue_key, issue_name, date_val, time_val, comment_val)
        if input("\nConfirm and Log Work to Jira? (y/n) [y]: ").strip().lower() in ('n', 'no'):
            print("Operation cancelled.")
            return

        print("\nInserting worklog to Jira...")
        try:
            date_iso = common_util.date_str_to_iso(date_val)
            status, response_text = await self.jira_util.post_insert_worklog(
                issue_key, time_val, date_iso, comment_val
            )
            if 200 <= status < 300:
                print("Successfully logged work to Jira!")
                self._save_history(issue_key, issue_name)
                await self._offer_sheets(issue_key, date_val, time_val, comment_val)
            else:
                print(f"Error: Jira returned HTTP {status}.\n{response_text}")
        except Exception as e:
            print(f"Error: {e}")

    async def _offer_sheets(self, issue_key: str, date: str, time: str, description: str) -> None:
        if not self.has_sheets:
            return
        if input("Insert to Google Sheets? (y/n) [y]: ").strip().lower() in ('n', 'no'):
            return
        print("Inserting to Google Sheets...")
        try:
            from util.sheets_util import SheetsUtil
            SheetsUtil().insert(key=issue_key, date=date, time=time, description=description)
            print("Successfully inserted to Google Sheets!")
        except Exception as e:
            print(f"Error inserting to Google Sheets: {e}")

    def _save_history(self, issue_key: str, issue_name: str) -> None:
        try:
            history_path = os.path.join(STORAGE.STORAGE_PATH.value, STORAGE.HISTORY_FILE.value)
            history = []
            if os.path.isfile(history_path):
                history = file_util.read_json_by_path(history_path)
            if not any(item.get("key") == issue_key for item in history):
                history.append({"key": issue_key, "name": issue_name, "summary": f"{issue_key} : {issue_name}"})
                file_util.save_json(STORAGE.STORAGE_PATH.value, STORAGE.HISTORY_FILE.value, history)
        except Exception as e:
            print(f"Note: Could not update history: {e}")

    # ── mode handlers ────────────────────────────────────────────────────────

    async def handle_auto_git(self) -> None:
        print("\n--- Auto Git Mode (-ga) ---")
        try:
            auto_key = self.git_util.get_issueName()
            print(f"Detected issue key: {auto_key}")
        except Exception as e:
            print(f"Error: {e}")
            return

        # Single fetch via prompt — user confirms or changes the key
        issue_key, issue_name = await self._prompt_and_fetch_issue(default_key=auto_key)

        default_date = common_util.get_currentdate_forentry()
        default_time = ""
        default_comment = ""
        time_spend_mins = 0
        try:
            git_details = self.git_util.get_git_detail()
            default_date = git_details.get("date", default_date)
            default_time = git_details.get("time_spend", default_time)
            default_comment = git_details.get("description", default_comment)
            time_spend_mins = git_details.get("time_spend_minutes", 0)
        except Exception as e:
            print(f"Note: Could not get git details ({e}). Using defaults.")

        date_val, time_val, comment_val = self._prompt_fields(
            default_date, default_time, default_comment, time_spend_mins
        )
        await self._submit(issue_key, issue_name, date_val, time_val, comment_val)

    async def handle_git_manual_issue(self, issue_key_arg: str = None) -> None:
        print("\n--- Git Manual Issue Mode (-gm) ---")

        fallback_key = None
        try:
            fallback_key = self.git_util.get_issueName()
        except Exception:
            pass

        issue_key, issue_name = await self._resolve_issue_from_arg(issue_key_arg, fallback_key)

        default_date = common_util.get_currentdate_forentry()
        default_time = ""
        default_comment = ""
        time_spend_mins = 0
        try:
            git_details = self.git_util.get_git_detail()
            default_date = git_details.get("date", default_date)
            default_time = git_details.get("time_spend", default_time)
            default_comment = git_details.get("description", default_comment)
            time_spend_mins = git_details.get("time_spend_minutes", 0)
        except Exception as e:
            print(f"Note: Could not get git details ({e}). Using defaults.")

        date_val, time_val, comment_val = self._prompt_fields(
            default_date, default_time, default_comment, time_spend_mins
        )
        await self._submit(issue_key, issue_name, date_val, time_val, comment_val)

    async def handle_manual_all(self) -> None:
        print("\n--- Manual Mode (-m) ---")
        issue_key, issue_name = await self._prompt_and_fetch_issue()
        date_val, time_val, comment_val = self._prompt_fields(
            common_util.get_currentdate_forentry(), "", "", 0
        )
        await self._submit(issue_key, issue_name, date_val, time_val, comment_val)
