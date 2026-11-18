import util.cli_format as fmt


def test_commit_bullets_clean_reflog_prefixes():
    entries = [
        {"description": "commit: add form"},
        {"description": "commit (amend): add validation"},
        {"description": "merge feature-x: Fast-forward"},
    ]
    assert fmt.format_commit_bullets(entries) == (
        "\nCommits in range:\n"
        "  • add form\n"
        "  • add validation\n"
        "  • feature-x (from merge)"
    )


def test_raw_duration():
    assert fmt.format_raw_duration(570) == "9h 30m"
    assert fmt.format_raw_duration(480) == "8h"
    assert fmt.format_raw_duration(1020) == "17h"


def test_cap_info():
    assert fmt.format_cap_info("total", 560) == "\033[1;33m[INFO] Raw total was 9h 20m, capped to 8h.\033[0m"


def test_summary_sheets_line_variants():
    base = fmt.format_summary("PROJ-1", "", "01/01/2025", "1h", "c")
    assert base.endswith("Comment    : c")
    assert "Issue Name : N/A" in base
    assert fmt.format_summary("PROJ-1", "n", "d", "t", "c", has_sheets=True).endswith(
        "Google Sheets integration is available.")
    assert fmt.format_summary("PROJ-1", "n", "d", "t", "c", has_sheets=False).endswith(
        "Google Sheets integration is not configured.")


def test_reflog_row_truncates_long_messages():
    e = {"date": "10/03/2025", "time_str": "09:40", "message": "x" * 60}
    assert fmt.format_reflog_row(3, e) == "    3  10/03/2025  09:40  " + "x" * 47 + "..."
    e["message"] = "y" * 50
    assert fmt.format_reflog_row(3, e).endswith("y" * 50)
