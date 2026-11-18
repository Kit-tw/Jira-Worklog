"""Command-line flag parsing for the Jira worklog CLI."""
from dataclasses import dataclass

MODE_AUTO_GIT = "-ga"
MODE_GIT_MANUAL = "-gm"
MODE_MANUAL = "-m"


@dataclass(frozen=True)
class CliArgs:
    mode: str | None              # one of the MODE_* constants, or None if no known flag
    issue_key_arg: str | None = None  # optional issue key following -gm


def parse_args(args: list[str]) -> CliArgs:
    """Resolve the CLI mode. Precedence when several flags are given: -ga > -gm > -m."""
    if MODE_AUTO_GIT in args:
        return CliArgs(MODE_AUTO_GIT)
    if MODE_GIT_MANUAL in args:
        idx = args.index(MODE_GIT_MANUAL)
        issue_key_arg = args[idx + 1] if idx + 1 < len(args) else None
        if issue_key_arg and issue_key_arg.startswith("-"):
            issue_key_arg = None
        return CliArgs(MODE_GIT_MANUAL, issue_key_arg)
    if MODE_MANUAL in args:
        return CliArgs(MODE_MANUAL)
    return CliArgs(None)
