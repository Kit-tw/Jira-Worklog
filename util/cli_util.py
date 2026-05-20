import os
import re
import json
import asyncio
from constant.Enum import STORAGE
import util.common_util as common_util
from util.git_util import GitUtil
from util.jira_util import JiraUtil

async def run_cli_git():
    print("\nInitializing Jira Worklog CLI...")
    
    # 1. Validate Jira credentials
    token_path = os.path.join(STORAGE.STORAGE_PATH.value, STORAGE.TOKEN_FILE.value)
    if not os.path.exists(token_path):
        print(f"Error: Jira API token file not found at '{token_path}'.")
        print("Please configure your Jira credentials using the GUI first.")
        return

    try:
        with open(token_path, 'r') as f:
            token_info = json.load(f)
    except Exception as e:
        print(f"Error reading Jira token file: {e}")
        return

    if common_util.now_greater_than_date(token_info["expire_date"], "%d/%m/%Y"):
        print("Error: Jira API token has expired. Please re-authenticate using the GUI.")
        return

    # 2. Extract info from git branch
    git_util = GitUtil()
    try:
        issue_key = git_util.get_issueName()
        print(f"Detected issue key from git branch: {issue_key}")
    except Exception as e:
        print(f"Error: Could not retrieve git branch name: {e}")
        return

    # 3. Fetch issue summary from Jira
    jira_util = JiraUtil()
    issue_name = ""
    try:
        print(f"Fetching Jira issue details for '{issue_key}'...")
        issue_name = await jira_util.fetch_issue(issue_key)
        print(f"Jira Issue Found: {issue_name}")
    except Exception as e:
        print(f"Warning: Could not fetch Jira issue details: {e}")

    # 4. Get git commit detail (dates, hours, etc.)
    default_date = common_util.get_currentdate_forentry()
    default_time = ""
    default_comment = ""
    
    try:
        git_details = git_util.get_git_detail()
        default_date = git_details.get("date", default_date)
        default_time = git_details.get("time_spend", default_time)
        default_comment = git_details.get("description", default_comment)
    except Exception as e:
        print(f"Note: Could not calculate git details from reflog ({e}). Using defaults.")

    print("\n==================================================")
    print("              JIRA WORKLOG EDITOR                 ")
    print("==================================================")
    print("Press [Enter] to accept the suggested value in brackets.")
    
    # 5. Interactive edit loop
    # Issue Key
    while True:
        user_key = input(f"Issue Key [{issue_key}]: ").strip()
        current_key = user_key if user_key else issue_key
        if not current_key:
            print("Error: Issue key cannot be empty.")
            continue
        
        # If user changed the key, let's try fetching the summary again
        if current_key != issue_key:
            print(f"Fetching details for new issue key '{current_key}'...")
            try:
                issue_name = await jira_util.fetch_issue(current_key)
                print(f"Jira Issue Found: {issue_name}")
                issue_key = current_key
                break
            except Exception as e:
                print(f"Error fetching issue '{current_key}': {e}")
                retry = input("Do you want to re-enter? (y/n) [y]: ").strip().lower()
                if retry == 'n':
                    issue_key = current_key
                    break
        else:
            break

    # Date
    while True:
        user_date = input(f"Date (dd/mm/yyyy) [{default_date}]: ").strip()
        date_val = user_date if user_date else default_date
        if re.match(r'^\d{2}/\d{2}/\d{4}$', date_val):
            break
        print("Error: Invalid date format. Please use dd/mm/yyyy.")

    # Time Spent
    while True:
        user_time = input(f"Time spent (e.g. 3h, 20m) [{default_time}]: ").strip()
        time_val = user_time if user_time else default_time
        if time_val:
            break
        print("Error: Time spent cannot be empty.")

    # Comment
    user_comment = input(f"Comment [{default_comment}]: ").strip()
    comment_val = user_comment if user_comment else default_comment

    # Check for Google Sheets availability
    credentials_path = os.path.join(STORAGE.STORAGE_PATH.value, STORAGE.GOOGLE_API_CREDENTIALS_FILE.value)
    has_sheets = os.path.exists(credentials_path)

    # 6. Confirmation and Auto Insert Worklog
    print("\n--- Summary ---")
    print(f"Issue Key  : {issue_key}")
    print(f"Issue Name : {issue_name or 'N/A'}")
    print(f"Date       : {date_val}")
    print(f"Time Spent : {time_val}")
    print(f"Comment    : {comment_val}")
    if has_sheets:
        print("Google Sheets integration is available.")
    else:
        print("Google Sheets integration is not configured.")

    confirm_insert = input("\nConfirm and Log Work to Jira? (y/n) [y]: ").strip().lower()
    if confirm_insert not in ('', 'y', 'yes'):
        print("Operation cancelled.")
        return

    # 7. Execution
    print("\nInserting worklog to Jira...")
    try:
        date_iso = common_util.date_str_to_iso(date_val)
        status, response_text = await jira_util.post_insert_worklog(issue_key, time_val, date_iso, comment_val)
        if 200 <= status < 300:
            print("Successfully logged work to Jira!")
            
            # Save history
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
                
            # Sheets integration
            if has_sheets:
                confirm_sheet = input("Insert to Google Sheets? (y/n) [y]: ").strip().lower()
                if confirm_sheet in ('', 'y', 'yes'):
                    print("Inserting to Google Sheets...")
                    try:
                        from util.sheets_util import SheetsUtil
                        # SheetsUtil constructor executes synchronously and does the work
                        SheetsUtil(key=issue_key, date=date_val, time=time_val, description=comment_val)
                        print("Successfully inserted to Google Sheets!")
                    except Exception as sheet_err:
                        print(f"Error inserting to Google Sheets: {sheet_err}")
        else:
            print(f"Error: Failed to log work to Jira (Status {status}).")
            print(f"Response: {response_text}")
    except Exception as err:
        print(f"Error: An unexpected error occurred: {err}")
