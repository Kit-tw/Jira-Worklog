import requests
from requests.auth import HTTPBasicAuth
import util.common_util as common_util
from constant.Enum import (STORAGE, URL)
from requests import Response
import json
class JiraUtil:
    def __init__(self):
        
        self.jira_data = common_util.read_json_file(STORAGE.TOKEN_FILE.value, STORAGE.STORAGE_PATH.value)
        self.mail = self.jira_data["jira_email"]
        self.api_token  = self.jira_data["jira_api"]
        self.prefix_url = self.jira_data["jira_prefix"]
        self.full_url = self.get_jira_site()

    #TODO : validate if user pass input as URL | key
    def fetch_issue(self,key):
        json_path = common_util.find(STORAGE.STORAGE_PATH.value, STORAGE.TOKEN_FILE.value)
        if(not json_path):
            print("json api storage file is not exist")
            return
        response = self.get_jira_issue(URL.JIRA_ISSUE_PATH.value,key)
        if(response.status_code.__ne__(200)):
            print("response GET issue error : " + response.text)
        return json.loads(response.text)["fields"]["summary"]
        
        

    def get_jira_issue(self,
                    path: str,
                    key : str
                    ) -> Response:
        url = self.full_url + path + key
        auth = HTTPBasicAuth(self.mail,self.api_token)
        headers = {
        "Accept": "application/json",
        }
        return requests.request("GET",url,headers=headers,auth=auth)

    def get_jira_site(self) -> str:
        return "https://" + self.prefix_url + ".atlassian.net"