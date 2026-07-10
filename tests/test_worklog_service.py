import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from util.worklog_service import WorklogService, WorklogRequest


@pytest.fixture
def mock_jira():
    jira = MagicMock()
    jira.fetch_issue = AsyncMock(return_value="Test Issue Summary")
    jira.post_insert_worklog = AsyncMock(return_value=(201, '{"id":"1"}'))
    return jira


@pytest.fixture
def service(mock_jira):
    return WorklogService(jira_util=mock_jira)


def test_validate_missing_issue_key(service):
    req = WorklogRequest(issue_key="", time_spend="1h", date="01/06/2025")
    with pytest.raises(ValueError, match="Issue key"):
        service._validate(req)


def test_validate_whitespace_issue_key(service):
    req = WorklogRequest(issue_key="   ", time_spend="1h", date="01/06/2025")
    with pytest.raises(ValueError, match="Issue key"):
        service._validate(req)


def test_validate_missing_time(service):
    req = WorklogRequest(issue_key="PROJ-1", time_spend="", date="01/06/2025")
    with pytest.raises(ValueError, match="Time spent"):
        service._validate(req)


def test_validate_bad_date_format(service):
    req = WorklogRequest(issue_key="PROJ-1", time_spend="1h", date="2025-06-01")
    with pytest.raises(ValueError, match="dd/mm/yyyy"):
        service._validate(req)


def test_validate_passes_for_valid_request(service):
    req = WorklogRequest(issue_key="PROJ-1", time_spend="2h", date="01/06/2025")
    service._validate(req)  # should not raise


@pytest.mark.asyncio
async def test_submit_success(service, mock_jira):
    req = WorklogRequest(issue_key="PROJ-1", time_spend="2h", date="01/06/2025")
    with patch("util.worklog_service.common_util.get_worklog_history", return_value=[]), \
         patch("util.file_util.save_file"):
        result = await service.submit(req)
    assert result.issue_name == "Test Issue Summary"
    assert result.issue_key == "PROJ-1"
    assert result.time_spend == "2h"
    mock_jira.post_insert_worklog.assert_called_once()


@pytest.mark.asyncio
async def test_submit_calls_fetch_before_post(service, mock_jira):
    req = WorklogRequest(issue_key="PROJ-42", time_spend="1h", date="15/07/2025")
    with patch("util.worklog_service.common_util.get_worklog_history", return_value=[]), \
         patch("util.file_util.save_file"):
        await service.submit(req)
    mock_jira.fetch_issue.assert_called_once_with("PROJ-42")


@pytest.mark.asyncio
async def test_submit_jira_api_error_raises(service, mock_jira):
    mock_jira.post_insert_worklog = AsyncMock(return_value=(400, '{"error":"bad request"}'))
    req = WorklogRequest(issue_key="PROJ-1", time_spend="2h", date="01/06/2025")
    with patch("util.worklog_service.common_util.get_worklog_history", return_value=[]), \
         patch("util.file_util.save_file"):
        with pytest.raises(Exception, match="400"):
            await service.submit(req)


@pytest.mark.asyncio
async def test_submit_does_not_duplicate_history(service, mock_jira):
    existing_history = [{"key": "PROJ-1", "name": "Old Name", "summary": "PROJ-1 : Old Name"}]
    req = WorklogRequest(issue_key="PROJ-1", time_spend="2h", date="01/06/2025")
    with patch("util.worklog_service.common_util.get_worklog_history", return_value=existing_history), \
         patch("util.file_util.save_file") as mock_save:
        await service.submit(req)
    mock_save.assert_not_called()


def test_submit_to_sheets_raises_when_no_credentials(service):
    result = MagicMock()
    with patch("os.path.exists", return_value=False):
        with pytest.raises(FileNotFoundError):
            service.submit_to_sheets(result)
