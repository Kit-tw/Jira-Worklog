import os
import re
import json
import sys
import asyncio
from constant.Enum import STORAGE
import util.common_util as common_util
from util.git_util import GitUtil
from util.jira_util import JiraUtil
from util.worklog_service import WorklogService, WorklogRequest
from util.cli_args import parse_args, MODE_AUTO_GIT, MODE_GIT_MANUAL, MODE_MANUAL
import util.cli_git_context as git_context
import util.cli_format as fmt

class JiraWorklogCLI:
    def __init__(self):
        self.git_util = GitUtil()
        self.jira_util = JiraUtil()
        self._worklog_service = WorklogService(self.jira_util)
        self.credentials_path = os.path.join(STORAGE.STORAGE_PATH.value, STORAGE.GOOGLE_API_CREDENTIALS_FILE.value)
        self.has_sheets = os.path.exists(self.credentials_path)

    async def run(self):
        print("\nInitializing Jira Worklog CLI...")
        if not self._validate_credentials():
            return

        cli_args = parse_args(sys.argv[1:])

        if cli_args.mode == MODE_AUTO_GIT:
            await self.handle_auto_git()
        elif cli_args.mode == MODE_GIT_MANUAL:
            await self.handle_git_manual_issue(cli_args.issue_key_arg)
        elif cli_args.mode == MODE_MANUAL:
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

    async def execute_worklog_submission(self, issue_key, issue_name, date_val, time_val, comment_val, sheets_override=None):
        print("\nInserting worklog to Jira...")
        try:
            request = WorklogRequest(
                issue_key=issue_key,
                time_spend=time_val,
                date=date_val,
                description=comment_val or None,
            )
            result = await self._worklog_service.submit(request)
            print("Successfully logged work to Jira!")

            if self.has_sheets:
                if sheets_override is None:
                    confirm_sheet = input("Insert to Google Sheets? (y/n) [y]: ").strip().lower()
                    do_sheets = confirm_sheet in ('', 'y', 'yes')
                else:
                    do_sheets = sheets_override
                if do_sheets:
                    print("Inserting to Google Sheets...")
                    try:
                        self._worklog_service.submit_to_sheets(result)
                        print("Successfully inserted to Google Sheets!")
                    except Exception as sheet_err:
                        print(f"Error inserting to Google Sheets: {sheet_err}")
        except Exception as err:
            print(f"Error: An unexpected error occurred: {err}")



    def _prompt_range(self, entries: list) -> tuple:
        """Display reflog list, prompt for anchor and end, return (anchor_idx, end_idx) in array coords."""
        n = len(entries)
        PAGE_SIZE = 20
        shown = min(PAGE_SIZE, n)

        while True:
            print(fmt.format_reflog_header())
            for ui_num in range(1, shown + 1):
                print(fmt.format_reflog_row(ui_num, entries[n - ui_num]))

            if shown < n:
                print(f"  ... ({n - shown} more older entries, valid range 1-{n})")
                expand = input("Show more? (y/n) [n]: ").strip().lower()
                if expand in ('y', 'yes'):
                    shown = n
                    continue
            break

        # Smart default: anchor = entry just before today's first commit
        default_start_num, default_end_num = git_context.default_range_numbers(entries, git_context.today_str())

        while True:
            try:
                s = input(f"\nStart anchor (older, not logged) [{default_start_num}]: ").strip()
                start_num = int(s) if s else default_start_num
                e = input(f"End (newer, included) [{default_end_num}]: ").strip()
                end_num = int(e) if e else default_end_num
            except ValueError:
                print("Error: Please enter a valid number.")
                continue

            if not (1 <= start_num <= n):
                print(f"Error: Start must be between 1 and {n}.")
                continue
            if not (1 <= end_num <= n):
                print(f"Error: End must be between 1 and {n}.")
                continue
            if end_num >= start_num:
                print(f"Error: End ({end_num}) must be newer (smaller #) than Start ({start_num}).")
                continue

            anchor_arr_idx = n - start_num
            end_arr_idx = n - end_num
            return anchor_arr_idx, end_arr_idx

    async def handle_git_manual_issue(self, issue_key_arg=None):
        print("\n--- Running Git Manual Issue Mode (-gm) ---")

        fallback_key = git_context.fallback_issue_key(self.git_util)

        defaults = git_context.GitDefaults(date=common_util.get_currentdate_forentry())
        try:
            defaults = git_context.load_git_defaults(self.git_util, defaults.date)
        except Exception as e:
            print(f"Note: Could not calculate git details from reflog ({e}). Using defaults.")
        default_date = defaults.date
        default_time = defaults.time_spend
        default_comment = defaults.comment

        issue_key, issue_name = await self.get_and_validate_issue_key(issue_key_arg, default_key=fallback_key)

        if default_time:
            default_time = self.prompt_time_threshold_check(default_time, defaults.time_spend_minutes)

        print(fmt.EDITOR_BANNER)

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

        print(fmt.format_summary(issue_key, issue_name, date_val, time_val, comment_val, has_sheets=bool(self.has_sheets)))

        confirm_insert = input("\nConfirm and Log Work to Jira? (y/n) [y]: ").strip().lower()
        if confirm_insert not in ('', 'y', 'yes'):
            print("Operation cancelled.")
            return

        await self.execute_worklog_submission(issue_key, issue_name, date_val, time_val, comment_val)

    async def handle_manual_all(self):
        print("\n--- Running Manual All Mode (-m) ---")

        issue_key, issue_name = await self.prompt_and_fetch_issue_key()

        default_date = common_util.get_currentdate_forentry()

        print(fmt.EDITOR_BANNER)

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

        print(fmt.format_summary(issue_key, issue_name, date_val, time_val, comment_val, has_sheets=bool(self.has_sheets)))

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

        # Load reflog entries for range selection
        try:
            entries = self.git_util.get_reflog_entries()
        except Exception as e:
            print(f"Error reading reflog: {e}")
            return

        if len(entries) < 2:
            print("Note: Not enough reflog entries for range selection. Using latest commit only.")
            await self._handle_auto_git_single(issue_key, issue_name)
            return

        # Pick range
        anchor_idx, end_idx = self._prompt_range(entries)
        range_entries = self.git_util.calc_range_entries(entries, anchor_idx, end_idx)
        if not range_entries:
            print("Error: No loggable commits in the selected range.")
            return

        count = len(range_entries)
        print(f"\nFound {count} commit(s) in range.")
        mode_input = input("Post as (1) combined entry or (2) separate per commit? [1]: ").strip()
        use_separate = mode_input == "2"

        issue_key, issue_name = await self.prompt_and_fetch_issue_key(default_key=issue_key)

        if use_separate:
            sheets_override = None
            if self.has_sheets:
                confirm_sheet = input("\nInsert all entries to Google Sheets? (y/n) [y]: ").strip().lower()
                sheets_override = confirm_sheet not in ('n', 'no')

            for i, entry in enumerate(range_entries):
                print(f"\n[{i + 1}/{count}] ------------------------------------------------")
                default_date = entry["date"]
                default_time = entry["time_spend"]
                default_comment = fmt.clean_comment(entry["description"])
                time_spend_mins = entry["time_spend_minutes"]

                if entry["capped"]:
                    print(fmt.format_cap_info("time", entry["raw_minutes"]))
                    ack = input("\033[1;33mAccept 8h or enter a custom time (Enter = accept): \033[0m").strip()
                    if ack:
                        default_time = ack
                else:
                    default_time = self.prompt_time_threshold_check(default_time, time_spend_mins)

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

                print(fmt.format_entry_line(issue_key, date_val, time_val, comment_val))
                confirm = input("Confirm and Log Work to Jira? (y/n) [y]: ").strip().lower()
                if confirm not in ('', 'y', 'yes'):
                    print("Skipped.")
                    continue

                await self.execute_worklog_submission(issue_key, issue_name, date_val, time_val, comment_val, sheets_override=sheets_override)

        else:
            # Combined: total time = end.datetime - anchor.datetime
            range_time = git_context.combined_range_time(entries[anchor_idx]["datetime"], entries[end_idx]["datetime"])
            combined_time = range_time.time_spend
            combined_minutes = range_time.time_spend_minutes

            if range_time.capped:
                print(fmt.format_cap_info("total", range_time.raw_minutes))
                ack = input("\033[1;33mAccept 8h or enter a custom time (Enter = accept): \033[0m").strip()
                if ack:
                    combined_time = ack
            else:
                combined_time = self.prompt_time_threshold_check(combined_time, combined_minutes)

            combined_date = entries[end_idx]["date"]

            print(fmt.EDITOR_BANNER)

            print(fmt.format_commit_bullets(range_entries))

            while True:
                user_date = input(f"\nDate (dd/mm/yyyy) [{combined_date}]: ").strip()
                date_val = user_date if user_date else combined_date
                if re.match(r'^\d{2}/\d{2}/\d{4}$', date_val):
                    break
                print("Error: Invalid date format. Please use dd/mm/yyyy.")

            while True:
                user_time = input(f"Time spent (e.g. 3h, 20m) [{combined_time}]: ").strip()
                time_val = user_time if user_time else combined_time
                if time_val:
                    break
                print("Error: Time spent cannot be empty.")

            comment_val = input("Comment (Enter to skip): ").strip()

            print(fmt.format_summary(issue_key, issue_name, date_val, time_val, comment_val))

            confirm_insert = input("\nConfirm and Log Work to Jira? (y/n) [y]: ").strip().lower()
            if confirm_insert not in ('', 'y', 'yes'):
                print("Operation cancelled.")
                return

            await self.execute_worklog_submission(issue_key, issue_name, date_val, time_val, comment_val)

    async def _handle_auto_git_single(self, issue_key: str, issue_name: str):
        """Fallback single-commit flow used when reflog has fewer than 2 entries."""
        defaults = git_context.GitDefaults(date=common_util.get_currentdate_forentry())
        try:
            defaults = git_context.load_git_defaults(self.git_util, defaults.date)
            if defaults.time_spend:
                defaults.time_spend = self.prompt_time_threshold_check(defaults.time_spend, defaults.time_spend_minutes)
        except Exception as e:
            print(f"Note: Could not calculate git details ({e}). Using defaults.")
        default_date = defaults.date
        default_time = defaults.time_spend
        default_comment = defaults.comment

        issue_key, issue_name = await self.prompt_and_fetch_issue_key(default_key=issue_key)

        print(fmt.EDITOR_BANNER)

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

        print(fmt.format_summary(issue_key, issue_name, date_val, time_val, comment_val))

        confirm_insert = input("\nConfirm and Log Work to Jira? (y/n) [y]: ").strip().lower()
        if confirm_insert not in ('', 'y', 'yes'):
            print("Operation cancelled.")
            return

        await self.execute_worklog_submission(issue_key, issue_name, date_val, time_val, comment_val)
