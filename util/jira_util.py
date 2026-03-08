import aiohttp
import util.common_util as common_util
from constant.Enum import (STORAGE, URL)
import json

class JiraUtil:
    def __init__(self):
        self.jira_data = common_util.read_json_file(STORAGE.STORAGE_PATH.value,STORAGE.TOKEN_FILE.value)
        self.mail = self.jira_data["jira_email"]
        self.api_token  = self.jira_data["jira_api"]
        self.prefix_url = self.jira_data["jira_prefix"]
        self.full_url = self.get_jira_site(self.prefix_url)

    async def fetch_issue(self,key):
        json_path = common_util.find(STORAGE.STORAGE_PATH.value, STORAGE.TOKEN_FILE.value)
        if not json_path:
            raise Exception(f"JSON api storage file at {json_path} does not exist.")
        
        status, text = await self.get_jira_issue(key)
        if status != 200:
            raise Exception(f"Fetch issue #{key} error: {text}")
        return json.loads(text)["fields"]["summary"]
        

    async def get_jira_issue(self, key: str) -> tuple[int, str]:
        path = URL.JIRA_ISSUE_PATH.value
        url = self.full_url + path + key
        auth = aiohttp.BasicAuth(self.mail, self.api_token)
        headers = {
            "Accept": "application/json",
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, auth=auth) as response:
                text = await response.text()
                return response.status, text

    async def post_insert_worklog(self,
                            issue_key : str,
                            time_spend :str,
                            date : str,
                            description : str | None
                            ) -> tuple[int, str]:
        path = URL.JIRA_POST_INSERT_WORKLOG_PATH(issue_key)
        url = self.full_url + path
        auth = aiohttp.BasicAuth(self.mail, self.api_token)
        headers = {
            "Accept" : "application/json",
            "Content-Type": "application/json"
        }
        payload = json.dumps({
            "comment" : {
                "content":[
                    {
                    "content":[{
                            "text":description,
                            "type":"text"
                            }],
                    "type":"paragraph"
                    }
                    ],
                    "type":"doc",
                    "version":1
            },
            "started":date,
            "timeSpent":time_spend
        })
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload, headers=headers, auth=auth) as response:
                text = await response.text()
                return response.status, text
    
    def get_jira_site(self,prefix) -> str:
        return "https://" + prefix + ".atlassian.net"