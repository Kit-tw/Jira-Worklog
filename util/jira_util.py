import requests
from requests.auth import HTTPBasicAuth
import util.common_util as common_util
from constant.Enum import (STORAGE, URL)
from requests import Response
import json
from util.gui_util import GuiUtil
class JiraUtil:
    def __init__(self):
        # TODO: FIX ERROR DIALOG HANDLELING
        self.jira_data = common_util.read_json_file(STORAGE.STORAGE_PATH.value,STORAGE.TOKEN_FILE.value)
        self.mail = self.jira_data["jira_email"]
        self.api_token  = self.jira_data["jira_api"]
        self.prefix_url = self.jira_data["jira_prefix"]
        self.gui = GuiUtil()
        self.full_url = self.get_jira_site()

    #TODO : validate if user pass input as URL | key
    def fetch_issue(self,key):
        json_path = common_util.find(STORAGE.STORAGE_PATH.value, STORAGE.TOKEN_FILE.value)
        if(not json_path):
            self.gui.show_dialog("Error", "cancel", f"json api storage file at {json_path} is not exist", options="OK")
            return 
        response = self.get_jira_issue(key)
        if(response.status_code.__ne__(200)):
            #TODO : Test error dialog
            self.gui.show_dialog("Error", "cancel", f"Fetch issue error : {response.text}", options="OK")
            print("response GET issue error : " + response.text)
            return
        return json.loads(response.text)["fields"]["summary"]
        
        

    def get_jira_issue(self,
                    key : str
                    ) -> Response:
        path = URL.JIRA_ISSUE_PATH.value
        url = self.full_url + path + key
        auth = HTTPBasicAuth(self.mail,self.api_token)
        headers = {
        "Accept": "application/json",
        }
        return requests.request("GET",url,headers=headers,auth=auth)

    def post_insert_worklog(self,
                            issue_key : str,
                            time_spend :str,
                            date : str,
                            description : str | None
                            ):
        path = URL.JIRA_POST_INSERT_WORKLOG_PATH(issue_key)
        url = self.full_url + path
        auth = HTTPBasicAuth(self.mail,self.api_token)
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
        return requests.request("POST",url,data=payload,headers=headers,auth=auth)
    
    def get_jira_site(self) -> str:
        return "https://" + self.prefix_url + ".atlassian.net"
    