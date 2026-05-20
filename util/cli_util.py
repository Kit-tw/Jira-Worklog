import os
import re
import json
import sys
import asyncio
from constant.Enum import STORAGE
import util.common_util as common_util
from util.git_util import GitUtil
from util.jira_util import JiraUtil

class JiraWorklogCLI:
    def __init__(self):
        self.git_util = GitUtil()
        self.jira_util = JiraUtil()
        self.credentials_path = os.path.join(STORAGE.STORAGE_PATH.value, STORAGE.GOOGLE_API_CREDENTIALS_FILE.value)
        self.has_sheets = os.path.exists(self.credentials_path)

    async def run(self):
        print("\nInitializing Jira Worklog CLI...")
        if not self._validate_credentials():
            return

        args = sys.argv[1:]
        
        if "-ga" in args:
            await self.handle_auto_git()
        elif "-gm" in args:
            idx = args.index("-gm")
            issue_key_arg = args[idx + 1] if idx + 1 < len(args) else None
            if issue_key_arg and issue_key_arg.startswith("-"):
                issue_key_arg = None
            await self.handle_git_manual_issue(issue_key_arg)
        elif "-m" in args:
            await self.handle_manual_all()
        else:
            print("Error: Unknown CLI flag.")

    def _validate_credentials(self) -> bool:
        token_path = os.path.join(STORAGE.STORAGE_PATH.value, STORAGE.TOKEN_FILE.value)
        if not os.path.exists(token_path):
            print(f"Error: Jira API token file not found at '{token_path}'.")
            print("Please configure your Jira credentials using the GUI first.")
            return False

        try:
            with open(token_path, 'r') as f:
                token_info = json.load(f)
        except Exception as e:
            print(f"Error reading Jira token file: {e}")
            return False

        if common_util.now_greater_than_date(token_info["expire_date"], "%d/%m/%Y"):
            print("Error: Jira API token has expired. Please re-authenticate using the GUI.")
            return False
            
        return True

    async def prompt_and_fetch_issue_key(self, default_key=None) -> tuple[str, str]:
        issue_key = default_key
        issue_name = ""
        while True:
            prompt = f"Issue Key [{issue_key}]: " if issue_key else "Issue Key: "
            user_key = input(prompt).strip()
            current_key = user_key if user_key else issue_key
            if not current_key:
                print("Error: Issue key cannot be empty.")
                continue

            try:
                print(f"Fetching Jira issue details for '{current_key}'...")
                issue_name = await self.jira_util.fetch_issue(current_key)
                print(f"Jira Issue Found: {issue_name}")
                return current_key, issue_name
            except Exception as e:
                print(f"Error fetching issue '{current_key}': {e}")
                retry = input("Do you want to re-enter? (y/n) [y]: ").strip().lower()
                if retry == 'n':
                    return current_key, ""

    async def get_and_validate_issue_key(self, issue_key_arg=None, default_key=None) -> tuple[str, str]:
        if issue_key_arg:
            try:
                print(f"Fetching Jira issue details for '{issue_key_arg}'...")
                issue_name = await self.jira_util.fetch_issue(issue_key_arg)
                print(f"Jira Issue Found: {issue_name}")
                return issue_key_arg, issue_name
            except Exception as e:
                print(f"Warning: Could not fetch Jira issue details for '{issue_key_arg}': {e}")
        return await self.prompt_and_fetch_issue_key(default_key)

    def prompt_time_threshold_check(self, default_time, time_spend_mins) -> str:
        min_time = common_util.get_min_time_spend()
        if time_spend_mins < min_time:
            warning_msg = (
                "\033[1;33m"
                "================================================================================\n"
                "[WARNING] Calculated time spent from git is less than the minimum threshold.\n"
                "================================================================================\033[0m"
            )
            print(warning_msg)
            confirm_time = input(f"\033[1;33mAre you sure to add {default_time} to worklog? (y/n) [y]: \033[0m").strip().lower()
            if confirm_time in ('n', 'no'):
                while True:
                    user_inserted_time = input("Enter time spent (e.g. 3h, 20m): ").strip()
                    if user_inserted_time:
                        return user_inserted_time
                    print("Error: Time spent cannot be empty.")
        return default_time

    async def execute_worklog_submission(self, issue_key, issue_name, date_val, time_val, comment_val):
        print("\nInserting worklog to Jira...")
        try:
            date_iso = common_util.date_str_to_iso(date_val)
            status, response_text = await self.jira_util.post_insert_worklog(issue_key, time_val, date_iso, comment_val)
            if 200 <= status < 300:
                print("Successfully logged work to Jira!")
                self._save_local_history(issue_key, issue_name)
                
                if self.has_sheets:
                    confirm_sheet = input("Insert to Google Sheets? (y/n) [y]: ").strip().lower()
                    if confirm_sheet in ('', 'y', 'yes'):
                        print("Inserting to Google Sheets...")
                        try:
                            from util.sheets_util import SheetsUtil
                            SheetsUtil(key=issue_key, date=date_val, time=time_val, description=comment_val)
                            print("Successfully inserted to Google Sheets!")
                        except Exception as sheet_err:
                            print(f"Error inserting to Google Sheets: {sheet_err}")
            else:
                print(f"Error: Failed to log work to Jira (Status {status}).")
                print(f"Response: {response_text}")
        except Exception as err:
            print(f"Error: An unexpected error occurred: {err}")

    def _save_local_history(self, issue_key, issue_name):
        try:
            history_path = os.path.join(STORAGE.STORAGE_PATH.value, STORAGE.HISTORY_FILE.value)
            history = []
            if os.path.isfile(history_path):
                with open(history_path, 'r') as f:
                    history = json.load(f)
            
            if not any(item.get("key") == issue_key for item in history):
                history.append({
                    "key": issue_key,
                    "name": issue_name,
                    "summary": f"{issue_key} : {issue_name}"
                })
                os.makedirs(STORAGE.STORAGE_PATH.value, exist_ok=True)
                with open(history_path, 'w') as f:
                    json.dump(history, f)
                print("Updated local history.")
        except Exception as hist_err:
            print(f"Note: Failed to update local history file: {hist_err}")



    async def handle_git_manual_issue(self, issue_key_arg=None):
        print("\n--- Running Git Manual Issue Mode (-gm) ---")

        default_date = common_util.get_currentdate_forentry()
        default_time = ""
        default_comment = ""
        time_spend_mins = 0

        fallback_key = None
        try:
            fallback_key = self.git_util.get_issueName()
        except Exception:
            pass

        try:
            git_details = self.git_util.get_git_detail()
            default_date = git_details.get("date", default_date)
            default_time = git_details.get("time_spend", default_time)
            default_comment = git_details.get("description", default_comment)
            time_spend_mins = git_details.get("time_spend_minutes", 0)
        except Exception as e:
            print(f"Note: Could not calculate git details from reflog ({e}). Using defaults.")

        issue_key, issue_name = await self.get_and_validate_issue_key(issue_key_arg, default_key=fallback_key)

        if default_time:
            default_time = self.prompt_time_threshold_check(default_time, time_spend_mins)

        print("\n==================================================")
        print("              JIRA WORKLOG EDITOR                 ")
        print("==================================================")
        print("Press [Enter] to accept the suggested value in brackets.")

        while True:
            user_date = input(f"Date (dd/mm/yyyy) [{default_date}]: ").strip()
            date_val = user_date if user_date else default_date
            if re.match(r'^\d{2}/\d{2}/\d{4}$', date_val):
                break
            print("Error: Invalid date format. Please use dd/mm/yyyy.")

        while True:
            user_time = input(f"Time spent (e.g. 3h, 20m) [{default_time}]: ").strip()
            time_val = user_time if user_time else default_time
            if time_val:
                break
            print("Error: Time spent cannot be empty.")

        user_comment = input(f"Comment [{default_comment}]: ").strip()
        comment_val = user_comment if user_comment else default_comment

        print("\n--- Summary ---")
        print(f"Issue Key  : {issue_key}")
        print(f"Issue Name : {issue_name or 'N/A'}")
        print(f"Date       : {date_val}")
        print(f"Time Spent : {time_val}")
        print(f"Comment    : {comment_val}")
        if self.has_sheets:
            print("Google Sheets integration is available.")
        else:
            print("Google Sheets integration is not configured.")

        confirm_insert = input("\nConfirm and Log Work to Jira? (y/n) [y]: ").strip().lower()
        if confirm_insert not in ('', 'y', 'yes'):
            print("Operation cancelled.")
            return

        await self.execute_worklog_submission(issue_key, issue_name, date_val, time_val, comment_val)

    async def handle_manual_all(self):
        print("\n--- Running Manual All Mode (-m) ---")

        issue_key, issue_name = await self.prompt_and_fetch_issue_key()

        default_date = common_util.get_currentdate_forentry()

        print("\n==================================================")
        print("              JIRA WORKLOG EDITOR                 ")
        print("==================================================")
        print("Press [Enter] to accept the suggested value in brackets.")

        while True:
            user_date = input(f"Date (dd/mm/yyyy) [{default_date}]: ").strip()
            date_val = user_date if user_date else default_date
            if re.match(r'^\d{2}/\d{2}/\d{4}$', date_val):
                break
            print("Error: Invalid date format. Please use dd/mm/yyyy.")

        while True:
            user_time = input("Time spent (e.g. 3h, 20m): ").strip()
            time_val = user_time
            if time_val:
                break
            print("Error: Time spent cannot be empty.")

        user_comment = input("Comment: ").strip()
        comment_val = user_comment

        print("\n--- Summary ---")
        print(f"Issue Key  : {issue_key}")
        print(f"Issue Name : {issue_name or 'N/A'}")
        print(f"Date       : {date_val}")
        print(f"Time Spent : {time_val}")
        print(f"Comment    : {comment_val}")
        if self.has_sheets:
            print("Google Sheets integration is available.")
        else:
            print("Google Sheets integration is not configured.")

        confirm_insert = input("\nConfirm and Log Work to Jira? (y/n) [y]: ").strip().lower()
        if confirm_insert not in ('', 'y', 'yes'):
            print("Operation cancelled.")
            return

        await self.execute_worklog_submission(issue_key, issue_name, date_val, time_val, comment_val)

    async def handle_auto_git(self):
        print("\n--- Running Auto Git Mode (-ga) ---")

        try:
            issue_key = self.git_util.get_issueName()
            print(f"Detected issue key from git branch: {issue_key}")
        except Exception as e:
            print(f"Error: Could not retrieve git branch name: {e}")
            return

        issue_name = ""
        try:
            print(f"Fetching Jira issue details for '{issue_key}'...")
            issue_name = await self.jira_util.fetch_issue(issue_key)
            print(f"Jira Issue Found: {issue_name}")
        except Exception as e:
            print(f"Warning: Could not fetch Jira issue details: {e}")

        default_date = common_util.get_currentdate_forentry()
        default_time = ""
        default_comment = ""
        
        try:
            git_details = self.git_util.get_git_detail()
            default_date = git_details.get("date", default_date)
            default_time = git_details.get("time_spend", default_time)
            default_comment = git_details.get("description", default_comment)
            
            time_spend_mins = git_details.get("time_spend_minutes", 0)
            default_time = self.prompt_time_threshold_check(default_time, time_spend_mins)
        except Exception as e:
            print(f"Note: Could not calculate git details from reflog ({e}). Using defaults.")

        issue_key, issue_name = await self.prompt_and_fetch_issue_key(default_key=issue_key)

        while True:
            user_date = input(f"Date (dd/mm/yyyy) [{default_date}]: ").strip()
            date_val = user_date if user_date else default_date
            if re.match(r'^\d{2}/\d{2}/\d{4}$', date_val):
                break
            print("Error: Invalid date format. Please use dd/mm/yyyy.")

        while True:
            user_time = input(f"Time spent (e.g. 3h, 20m) [{default_time}]: ").strip()
            time_val = user_time if user_time else default_time
            if time_val:
                break
            print("Error: Time spent cannot be empty.")

        user_comment = input(f"Comment [{default_comment}]: ").strip()
        comment_val = user_comment if user_comment else default_comment

        print("\n--- Summary ---")
        print(f"Issue Key  : {issue_key}")
        print(f"Issue Name : {issue_name or 'N/A'}")
        print(f"Date       : {date_val}")
        print(f"Time Spent : {time_val}")
        print(f"Comment    : {comment_val}")
        if self.has_sheets:
            print("Google Sheets integration is available.")
        else:
            print("Google Sheets integration is not configured.")

        confirm_insert = input("\nConfirm and Log Work to Jira? (y/n) [y]: ").strip().lower()
        if confirm_insert not in ('', 'y', 'yes'):
            print("Operation cancelled.")
            return

        await self.execute_worklog_submission(issue_key, issue_name, date_val, time_val, comment_val)
