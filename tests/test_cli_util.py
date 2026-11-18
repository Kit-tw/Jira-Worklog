"""
Characterization tests for util/cli_util.py.

Each test drives JiraWorklogCLI.run() end to end with a scripted sequence of
input() answers and compares the full terminal transcript (prints, prompts,
answers and the calls made to Jira / Sheets) against a golden file in
tests/snapshots/cli/.

Everything external is faked:
  * GitUtil, JiraUtil and WorklogService are replaced inside util.cli_util.
  * STORAGE points to a pytest tmp dir holding a fake token file; the
    "credentials.json" there is an empty placeholder that only toggles the
    has_sheets existence check. No real credential file is ever read.

Goldens were recorded from the pre-refactor code. To re-record (only when a
behaviour change is intended):  CLI_SNAPSHOT_UPDATE=1 python -m pytest tests/test_cli_util.py
"""
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import util.cli_util as cli_util
from util.git_util import GitUtil
from util.worklog_service import WorklogResult

SNAP_DIR = Path(__file__).parent / "snapshots" / "cli"
UPDATE = os.environ.get("CLI_SNAPSHOT_UPDATE") == "1"
FIXED_DEFAULT_DATE = "01/02/2025"
PAST = datetime(2025, 3, 10)


def entry(dt: datetime, message: str) -> dict:
    """Shape of one item returned by GitUtil.get_reflog_entries()."""
    return {
        "datetime": dt,
        "date": f"{dt.day:02d}/{dt.month:02d}/{dt.year}",
        "time_str": f"{dt.hour:02d}:{dt.minute:02d}",
        "message": message,
    }


def at(day: datetime, hh: int, mm: int = 0) -> datetime:
    return day.replace(hour=hh, minute=mm, second=0, microsecond=0)


class Harness:
    def __init__(self, tmp_path: Path, capsys):
        self.tmp_path = tmp_path
        self.capsys = capsys
        self.answers: list[str] = []
        self.token = json.dumps({"expire_date": "31/12/2099"})
        self.has_sheets = True

        self.git = MagicMock(name="git")
        self.git.get_issueName.return_value = "PROJ-1"
        self.git.get_git_detail.return_value = {
            "date": "10/03/2025",
            "time_spend": "45m",
            "time_spend_minutes": 45,
            "description": "commit: fix bug",
        }
        self.git.get_reflog_entries.return_value = []
        self.git.calc_range_entries.side_effect = (
            lambda e, a, b: GitUtil.calc_range_entries(None, e, a, b)
        )

        self.issues = {"PROJ-1": "Fix login", "PROJ-2": "Add export"}
        self.jira = MagicMock(name="jira")
        self.jira.fetch_issue = AsyncMock(side_effect=self._fetch)

        self.submit_error: Exception | None = None
        self.sheets_error: Exception | None = None
        self.service = MagicMock(name="service")
        self.service.submit = AsyncMock(side_effect=self._submit)
        self.service.submit_to_sheets = MagicMock(side_effect=self._sheets)

    # ---- fakes -----------------------------------------------------------
    async def _fetch(self, key):
        print(f"[[jira.fetch_issue {key!r}]]")
        if key not in self.issues:
            raise Exception(f"Fetch issue #{key} error: 404")
        return self.issues[key]

    async def _submit(self, request):
        print(f"[[service.submit {request!r}]]")
        if self.submit_error:
            raise self.submit_error
        return WorklogResult(
            issue_key=request.issue_key,
            issue_name=self.issues.get(request.issue_key, ""),
            date=request.date,
            time_spend=request.time_spend,
            description=request.description,
        )

    def _sheets(self, result):
        print(f"[[service.submit_to_sheets {result!r}]]")
        if self.sheets_error:
            raise self.sheets_error

    def _input(self, prompt=""):
        if not self.answers:
            raise AssertionError(f"Unexpected prompt with no scripted answer: {prompt!r}")
        ans = self.answers.pop(0)
        sys.stdout.write(f"{prompt}{ans}\n")
        return ans

    # ---- driver ----------------------------------------------------------
    async def run(self, argv: list[str], answers: list[str]):
        self.answers = list(answers)
        if self.token is not None:
            (self.tmp_path / "token.json").write_text(self.token, encoding="utf-8")
        if self.has_sheets:
            (self.tmp_path / "credentials.json").write_text("{}", encoding="utf-8")

        storage = SimpleNamespace(
            STORAGE_PATH=SimpleNamespace(value=str(self.tmp_path)),
            TOKEN_FILE=SimpleNamespace(value="token.json"),
            GOOGLE_API_CREDENTIALS_FILE=SimpleNamespace(value="credentials.json"),
        )
        git_cls = MagicMock(return_value=self.git)
        git_cls.clean_reflog_message = GitUtil.clean_reflog_message

        with patch.object(cli_util, "STORAGE", storage), \
             patch.object(cli_util, "GitUtil", git_cls), \
             patch.object(cli_util, "JiraUtil", MagicMock(return_value=self.jira)), \
             patch.object(cli_util, "WorklogService", MagicMock(return_value=self.service)), \
             patch("util.common_util.get_currentdate_forentry", return_value=FIXED_DEFAULT_DATE), \
             patch("util.common_util.get_min_time_spend", return_value=15), \
             patch("builtins.input", side_effect=self._input), \
             patch.object(sys, "argv", ["gui.py", *argv]):
            await cli_util.JiraWorklogCLI().run()

        assert not self.answers, f"Scripted answers were not consumed: {self.answers}"

    def transcript(self) -> str:
        out = self.capsys.readouterr().out
        out = out.replace(f"{self.tmp_path}{os.sep}", "<STORAGE>/").replace(str(self.tmp_path), "<STORAGE>")
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        out = out.replace(today.strftime("%d/%m/%Y"), "<TODAY>")
        out = out.replace(yesterday.strftime("%d/%m/%Y"), "<YESTERDAY>")
        return out

    def check(self, name: str):
        out = self.transcript()
        path = SNAP_DIR / f"{name}.txt"
        if UPDATE:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(out, encoding="utf-8", newline="\n")
            return
        assert path.exists(), f"Missing golden {path}"
        assert out == path.read_text(encoding="utf-8")


@pytest.fixture
def h(tmp_path, capsys):
    return Harness(tmp_path, capsys)


# =========================================================================
# Credential gate and flag dispatch
# =========================================================================

@pytest.mark.asyncio
async def test_cred_missing_token(h):
    h.token = None
    await h.run(["-m"], [])
    h.check("cred_missing_token")


@pytest.mark.asyncio
async def test_cred_corrupt_token(h):
    h.token = "{not json"
    await h.run(["-m"], [])
    h.check("cred_corrupt_token")


@pytest.mark.asyncio
async def test_cred_expired_token(h):
    h.token = json.dumps({"expire_date": "01/01/2000"})
    await h.run(["-m"], [])
    h.check("cred_expired_token")


@pytest.mark.asyncio
async def test_unknown_flag(h):
    await h.run(["-x"], [])
    h.check("unknown_flag")


@pytest.mark.asyncio
async def test_precedence_ga_over_m(h):
    h.git.get_issueName.side_effect = Exception("no repo")
    await h.run(["-m", "-ga"], [])
    h.check("precedence_ga_over_m")


@pytest.mark.asyncio
async def test_precedence_gm_over_m(h):
    await h.run(["-m", "-gm", "PROJ-1"], ["", "", "", "n"])
    h.check("precedence_gm_over_m")


def test_has_sheets_reflects_credentials_file(tmp_path):
    storage = SimpleNamespace(
        STORAGE_PATH=SimpleNamespace(value=str(tmp_path)),
        TOKEN_FILE=SimpleNamespace(value="token.json"),
        GOOGLE_API_CREDENTIALS_FILE=SimpleNamespace(value="credentials.json"),
    )
    with patch.object(cli_util, "STORAGE", storage), \
         patch.object(cli_util, "GitUtil"), \
         patch.object(cli_util, "JiraUtil"), \
         patch.object(cli_util, "WorklogService"):
        assert cli_util.JiraWorklogCLI().has_sheets is False
        (tmp_path / "credentials.json").write_text("{}")
        assert cli_util.JiraWorklogCLI().has_sheets is True


# =========================================================================
# -m  (manual all)
# =========================================================================

@pytest.mark.asyncio
async def test_m_happy_path_with_validation_errors(h):
    await h.run(["-m"], [
        "",            # empty key -> error
        "PROJ-1",
        "2025-01-01",  # bad date
        "",            # default date
        "",            # empty time -> error
        "1h 30m",
        "worked on it",
        "",            # confirm
        "",            # sheets yes
    ])
    h.check("m_happy_path_with_validation_errors")


@pytest.mark.asyncio
async def test_m_fetch_fails_then_reenter(h):
    await h.run(["-m"], ["BAD-1", "", "PROJ-2", "", "1h", "", "y", "n"])
    h.check("m_fetch_fails_then_reenter")


@pytest.mark.asyncio
async def test_m_fetch_fails_give_up_no_sheets(h):
    h.has_sheets = False
    await h.run(["-m"], ["BAD-1", "n", "", "1h", "", ""])
    h.check("m_fetch_fails_give_up_no_sheets")


@pytest.mark.asyncio
async def test_m_cancel(h):
    await h.run(["-m"], ["PROJ-1", "", "1h", "", "no"])
    h.check("m_cancel")


@pytest.mark.asyncio
async def test_m_submit_error(h):
    h.submit_error = Exception("Jira API error (status 400): bad")
    await h.run(["-m"], ["PROJ-1", "", "1h", "c", ""])
    h.check("m_submit_error")


@pytest.mark.asyncio
async def test_m_sheets_error(h):
    h.sheets_error = Exception("quota exceeded")
    await h.run(["-m"], ["PROJ-1", "", "1h", "c", "", "yes"])
    h.check("m_sheets_error")


# =========================================================================
# -gm  (git manual issue)
# =========================================================================

@pytest.mark.asyncio
async def test_gm_with_key_arg(h):
    await h.run(["-gm", "PROJ-2"], ["", "", "", "", ""])
    h.check("gm_with_key_arg")


@pytest.mark.asyncio
async def test_gm_key_arg_is_flag(h):
    await h.run(["-gm", "-v"], ["", "", "", "my comment", "", "n"])
    h.check("gm_key_arg_is_flag")


@pytest.mark.asyncio
async def test_gm_bad_key_arg_falls_back_to_branch(h):
    await h.run(["-gm", "BAD-9"], ["", "", "", "", "n"])
    h.check("gm_bad_key_arg_falls_back_to_branch")


@pytest.mark.asyncio
async def test_gm_no_git(h):
    h.has_sheets = False
    h.git.get_issueName.side_effect = Exception("no repo")
    h.git.get_git_detail.side_effect = Exception("Could not get git details: boom")
    await h.run(["-gm"], ["PROJ-1", "", "", "3h", "", ""])
    h.check("gm_no_git")


@pytest.mark.asyncio
async def test_gm_below_threshold_keep(h):
    h.git.get_git_detail.return_value = {
        "date": "10/03/2025", "time_spend": "5m", "time_spend_minutes": 5,
        "description": "merge feature-x: Fast-forward",
    }
    await h.run(["-gm", "PROJ-1"], ["", "", "", "", "n"])
    h.check("gm_below_threshold_keep")


@pytest.mark.asyncio
async def test_gm_below_threshold_override(h):
    h.git.get_git_detail.return_value = {
        "date": "10/03/2025", "time_spend": "5m", "time_spend_minutes": 5,
        "description": "commit (amend): tweak",
    }
    await h.run(["-gm", "PROJ-1"], ["n", "", "2h", "", "", "", "n"])
    h.check("gm_below_threshold_override")


# =========================================================================
# -ga  (auto git)
# =========================================================================

@pytest.mark.asyncio
async def test_ga_branch_error(h):
    h.git.get_issueName.side_effect = Exception("Current directory does not have a valid .git repository.")
    await h.run(["-ga"], [])
    h.check("ga_branch_error")


@pytest.mark.asyncio
async def test_ga_reflog_error(h):
    h.git.get_reflog_entries.side_effect = Exception("Could not read reflog: boom")
    await h.run(["-ga"], [])
    h.check("ga_reflog_error")


@pytest.mark.asyncio
async def test_ga_single_fallback(h):
    h.git.get_reflog_entries.return_value = [entry(at(PAST, 9), "commit: only one")]
    h.git.get_git_detail.return_value = {
        "date": "10/03/2025", "time_spend": "5m", "time_spend_minutes": 5,
        "description": "commit: quick",
    }
    await h.run(["-ga"], ["", "", "", "", "", "", "n"])
    h.check("ga_single_fallback")


@pytest.mark.asyncio
async def test_ga_single_fallback_no_detail(h):
    h.git.get_git_detail.side_effect = Exception("Could not get git details: boom")
    await h.run(["-ga"], ["", "", "", "1h", "c", "", ""])
    h.check("ga_single_fallback_no_detail")


@pytest.mark.asyncio
async def test_ga_branch_issue_not_found(h):
    h.git.get_issueName.return_value = "PROJ-404"
    h.git.get_git_detail.side_effect = Exception("Could not get git details: boom")
    await h.run(["-ga"], ["", "", "PROJ-1", "", "2h", "", "n"])
    h.check("ga_branch_issue_not_found")


def _combined_entries():
    return [
        entry(at(PAST, 9, 0), "checkout: moving from main to PROJ-1-login"),
        entry(at(PAST, 9, 40), "commit: add login form"),
        entry(at(PAST, 10, 30), "commit (amend): add login form validation"),
        entry(at(PAST, 11, 15), "merge feature-x: Fast-forward"),
    ]


@pytest.mark.asyncio
async def test_ga_combined(h):
    h.git.get_reflog_entries.return_value = _combined_entries()
    await h.run(["-ga"], ["", "", "", "", "", "", "", "", ""])
    h.check("ga_combined")


@pytest.mark.asyncio
async def test_ga_combined_capped_accept(h):
    h.git.get_reflog_entries.return_value = [
        entry(at(PAST, 8), "checkout: start"),
        entry(at(PAST, 17, 30), "commit: long day"),
    ]
    await h.run(["-ga"], ["", "", "1", "", "", "", "", "summary", "", "n"])
    h.check("ga_combined_capped_accept")


@pytest.mark.asyncio
async def test_ga_combined_capped_custom(h):
    h.git.get_reflog_entries.return_value = [
        entry(at(PAST, 8), "checkout: start"),
        entry(at(PAST, 16), "commit: exactly eight"),
    ]
    await h.run(["-ga"], ["", "", "", "", "7h", "", "", "", "n"])
    h.check("ga_combined_capped_custom")


@pytest.mark.asyncio
async def test_ga_combined_below_threshold(h):
    h.git.get_reflog_entries.return_value = [
        entry(at(PAST, 9), "checkout: start"),
        entry(at(PAST, 9, 5), "commit: typo"),
    ]
    await h.run(["-ga"], ["", "", "", "", "n", "", "10m", "", "", "", ""])
    h.check("ga_combined_below_threshold")


@pytest.mark.asyncio
async def test_ga_separate(h):
    h.git.get_reflog_entries.return_value = [
        entry(at(PAST, 8, 0), "checkout: moving from main to PROJ-1"),
        entry(at(PAST, 8, 10), "commit: tiny fix"),
        entry(at(PAST, 17, 30), "commit: big feature"),
        entry(at(PAST, 18, 15), "commit: docs"),
    ]
    await h.run(["-ga"], [
        "", "",       # range defaults
        "2",          # separate
        "PROJ-2",     # override issue key
        "",           # sheets for all: yes
        # [1/3] 10m, below threshold
        "", "", "", "", "",
        # [2/3] capped
        "7h", "", "", "custom comment", "",
        # [3/3] skip
        "", "", "", "n",
    ])
    h.check("ga_separate")


@pytest.mark.asyncio
async def test_ga_separate_sheets_declined(h):
    h.git.get_reflog_entries.return_value = [
        entry(at(PAST, 9), "checkout: start"),
        entry(at(PAST, 10), "commit: one"),
    ]
    await h.run(["-ga"], ["", "", "2", "", "no", "11/03/2025", "", "", ""])
    h.check("ga_separate_sheets_declined")


@pytest.mark.asyncio
async def test_ga_separate_no_sheets_configured(h):
    h.has_sheets = False
    h.git.get_reflog_entries.return_value = [
        entry(at(PAST, 9), "checkout: start"),
        entry(at(PAST, 10), "commit: one"),
    ]
    await h.run(["-ga"], ["", "", "2", "", "bad", "", "", "", ""])
    h.check("ga_separate_no_sheets_configured")


@pytest.mark.asyncio
async def test_ga_range_paging_and_input_errors(h):
    long_msg = "commit: " + "a very long commit message that will be truncated " * 2
    entries = [entry(at(PAST, 6) + timedelta(minutes=10 * i), f"commit: step {i}") for i in range(25)]
    entries[22] = entry(entries[22]["datetime"], long_msg.strip())
    h.git.get_reflog_entries.return_value = entries
    await h.run(["-ga"], [
        "y",            # show more
        "abc",          # start not a number
        "0", "",        # start out of range
        "3", "5",       # end not newer than start
        "26", "1",      # start out of range (high)
        "5", "0",       # end out of range
        "5", "2",       # valid
        "",             # combined
        "",             # key
        "", "", "x", "n",
    ])
    h.check("ga_range_paging_and_input_errors")


@pytest.mark.asyncio
async def test_ga_range_paging_declined(h):
    entries = [entry(at(PAST, 6) + timedelta(minutes=10 * i), f"commit: step {i}") for i in range(22)]
    h.git.get_reflog_entries.return_value = entries
    await h.run(["-ga"], ["", "", "", "", "", "", "", "", "n"])
    h.check("ga_range_paging_declined")


@pytest.mark.asyncio
async def test_ga_range_default_anchor_before_today(h):
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    h.git.get_reflog_entries.return_value = [
        entry(at(yesterday, 16), "commit: y1"),
        entry(at(yesterday, 17), "commit: y2"),
        entry(at(today, 9), "commit: t1"),
        entry(at(today, 10), "commit: t2"),
    ]
    await h.run(["-ga"], ["", "", "", "", "", "", "", "", "n"])
    h.check("ga_range_default_anchor_before_today")


@pytest.mark.asyncio
async def test_ga_range_default_all_today(h):
    today = datetime.now()
    h.git.get_reflog_entries.return_value = [
        entry(at(today, 9), "commit: t1"),
        entry(at(today, 9, 30), "commit: t2"),
    ]
    await h.run(["-ga"], ["", "", "", "", "", "", "", "n"])
    h.check("ga_range_default_all_today")


@pytest.mark.asyncio
async def test_ga_no_loggable_commits(h):
    h.git.get_reflog_entries.return_value = [
        entry(at(PAST, 9), "checkout: start"),
        entry(at(PAST, 10), "commit: one"),
    ]
    h.git.calc_range_entries.side_effect = None
    h.git.calc_range_entries.return_value = []
    await h.run(["-ga"], ["", ""])
    h.check("ga_no_loggable_commits")
