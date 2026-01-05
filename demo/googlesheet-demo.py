
import pygsheets


client = pygsheets.authorize(service_account_file="token.json")

spreadsheet_url = ""

try:
    sh = client.open_by_url(spreadsheet_url)
    print("It's Work")
except Exception as e:
    print("not work")