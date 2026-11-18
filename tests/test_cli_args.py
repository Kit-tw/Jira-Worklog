import pytest
from util.cli_args import parse_args, CliArgs, MODE_AUTO_GIT, MODE_GIT_MANUAL, MODE_MANUAL


@pytest.mark.parametrize("args, expected", [
    (["-ga"], CliArgs(MODE_AUTO_GIT)),
    (["-m"], CliArgs(MODE_MANUAL)),
    (["-gm"], CliArgs(MODE_GIT_MANUAL, None)),
    (["-gm", "PROJ-1"], CliArgs(MODE_GIT_MANUAL, "PROJ-1")),
    (["-gm", "-v"], CliArgs(MODE_GIT_MANUAL, None)),
    (["-gm", ""], CliArgs(MODE_GIT_MANUAL, "")),
    (["-m", "-gm", "PROJ-2"], CliArgs(MODE_GIT_MANUAL, "PROJ-2")),
    (["-gm", "PROJ-1", "-ga"], CliArgs(MODE_AUTO_GIT)),
    (["-m", "-ga"], CliArgs(MODE_AUTO_GIT)),
    ([], CliArgs(None)),
    (["-x"], CliArgs(None)),
])
def test_parse_args(args, expected):
    assert parse_args(args) == expected
