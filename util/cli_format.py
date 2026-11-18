"""
Text formatting for the Jira worklog CLI: worklog comments and the blocks the CLI prints.
Pure functions returning strings; callers do the printing.
"""
from util.git_util import GitUtil

YELLOW = "\033[1;33m"
RESET = "\033[0m"

EDITOR_BANNER = (
    "\n==================================================\n"
    "              JIRA WORKLOG EDITOR                 \n"
    "==================================================\n"
    "Press [Enter] to accept the suggested value in brackets."
)

REFLOG_MSG_MAX = 50


def clean_comment(description: str) -> str:
    """Default worklog comment from a reflog message (strips git action prefixes)."""
    return GitUtil.clean_reflog_message(description)


def format_commit_bullets(range_entries: list) -> str:
    """'Commits in range' block shown as context for a combined worklog entry."""
    lines = ["\nCommits in range:"]
    lines += [f"  • {clean_comment(e['description'])}" for e in range_entries]
    return "\n".join(lines)


def format_raw_duration(minutes: int) -> str:
    """e.g. 570 -> '9h 30m', 480 -> '8h'."""
    h, m = minutes // 60, minutes % 60
    return f"{h}h {m}m" if m else f"{h}h"


def format_cap_info(label: str, raw_minutes: int) -> str:
    """Notice shown when a duration is capped to 8h. label is 'time' or 'total'."""
    return f"{YELLOW}[INFO] Raw {label} was {format_raw_duration(raw_minutes)}, capped to 8h.{RESET}"


def format_summary(issue_key, issue_name, date_val, time_val, comment_val, has_sheets: bool | None = None) -> str:
    """Summary block before confirming. The Sheets line is omitted when has_sheets is None."""
    lines = [
        "\n--- Summary ---",
        f"Issue Key  : {issue_key}",
        f"Issue Name : {issue_name or 'N/A'}",
        f"Date       : {date_val}",
        f"Time Spent : {time_val}",
        f"Comment    : {comment_val}",
    ]
    if has_sheets is True:
        lines.append("Google Sheets integration is available.")
    elif has_sheets is False:
        lines.append("Google Sheets integration is not configured.")
    return "\n".join(lines)


def format_entry_line(issue_key, date_val, time_val, comment_val) -> str:
    """Compact per-commit summary used in separate-entry mode."""
    return f"\nIssue: {issue_key} | Date: {date_val} | Time: {time_val}\nComment: {comment_val}"


def format_reflog_header() -> str:
    return "\nReflog entries (1 = newest):\n" + f"  {'#':>3}  {'Date':10}  {'Time':5}  Message\n" + "  " + "-" * 62


def format_reflog_row(ui_num: int, entry: dict) -> str:
    msg = entry["message"]
    if len(msg) > REFLOG_MSG_MAX:
        msg = msg[:REFLOG_MSG_MAX - 3] + "..."
    return f"  {ui_num:>3}  {entry['date']:10}  {entry['time_str']:5}  {msg}"
