import json
import aiohttp

import util.file_util as file_util
from constant.Enum import STORAGE, URL


class JiraUtil:
    def __init__(self):
        data = file_util.read_json(STORAGE.STORAGE_PATH.value, STORAGE.TOKEN_FILE.value)
        self.mail = data["jira_email"]
        self.api_token = data["jira_api"]
        self.prefix_url = data["jira_prefix"]
        self.full_url = f"https://{self.prefix_url}.atlassian.net"

    def _auth(self) -> aiohttp.BasicAuth:
        return aiohttp.BasicAuth(self.mail, self.api_token)

    async def fetch_issue(self, key: str) -> str:
        status, text = await self._get(URL.JIRA_ISSUE_PATH.value + key)
        if status != 200:
            raise Exception(f"Fetch issue '{key}' failed (HTTP {status}): {text}")
        return json.loads(text)["fields"]["summary"]

    async def post_insert_worklog(self,
                                  issue_key: str,
                                  time_spend: str,
                                  date: str,
                                  description: str | None) -> tuple[int, str]:
        payload = json.dumps({
            "comment": {
                "content": [{"content": [{"text": description, "type": "text"}], "type": "paragraph"}],
                "type": "doc",
                "version": 1,
            },
            "started": date,
            "timeSpent": time_spend,
        })
        return await self._post(URL.jira_worklog_path(issue_key), payload)

    async def _get(self, path: str) -> tuple[int, str]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.full_url + path,
                headers={"Accept": "application/json"},
                auth=self._auth(),
            ) as resp:
                return resp.status, await resp.text()

    async def _post(self, path: str, payload: str) -> tuple[int, str]:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.full_url + path,
                data=payload,
                headers={"Accept": "application/json", "Content-Type": "application/json"},
                auth=self._auth(),
            ) as resp:
                return resp.status, await resp.text()
