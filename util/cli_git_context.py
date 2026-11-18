"""
Builds worklog defaults from git state for the CLI.
No terminal I/O here: functions either return values or raise.
"""
from dataclasses import dataclass
from datetime import datetime
from util.git_util import GitUtil

CAP_MINUTES = 480  # 8h


@dataclass
class GitDefaults:
    date: str
    time_spend: str = ""
    comment: str = ""
    time_spend_minutes: int = 0


@dataclass
class RangeTime:
    time_spend: str
    time_spend_minutes: int
    raw_minutes: int
    capped: bool


def fallback_issue_key(git_util) -> str | None:
    """Issue key derived from the current branch, or None if it can't be read."""
    try:
        return git_util.get_issueName()
    except Exception:
        return None


def load_git_defaults(git_util, default_date: str) -> GitDefaults:
    """Defaults from the last two reflog entries. Raises if git details are unavailable."""
    details = git_util.get_git_detail()
    return GitDefaults(
        date=details.get("date", default_date),
        time_spend=details.get("time_spend", ""),
        comment=GitUtil.clean_reflog_message(details.get("description", "")),
        time_spend_minutes=details.get("time_spend_minutes", 0),
    )


def combined_range_time(anchor_dt: datetime, end_dt: datetime) -> RangeTime:
    """Total time from anchor to end, minimum 1m, capped at 8h."""
    total_seconds = (end_dt - anchor_dt).total_seconds()
    total_minutes = max(1, int(total_seconds // 60))
    hours = total_minutes // 60
    mins = total_minutes % 60
    if hours >= 8:
        return RangeTime("8h", CAP_MINUTES, total_minutes, True)
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if mins > 0:
        parts.append(f"{mins}m")
    return RangeTime(" ".join(parts) if parts else "1m", total_minutes, total_minutes, False)


def default_range_numbers(entries: list, today_str: str) -> tuple[int, int]:
    """
    Default (start_num, end_num) in UI numbering (1 = newest).
    Start anchor defaults to the entry just before today's first entry,
    or the oldest entry if there is none (or today's first entry is the oldest).
    """
    n = len(entries)
    first_today_arr_idx = next((i for i in range(n) if entries[i]["date"] == today_str), None)
    if first_today_arr_idx is None or first_today_arr_idx == 0:
        default_start_num = n
    else:
        default_start_num = n - (first_today_arr_idx - 1)
    return default_start_num, 1


def today_str() -> str:
    return datetime.now().strftime("%d/%m/%Y")
