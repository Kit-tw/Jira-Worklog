import gspread

spreadsheet_id = "" #soruce with view permission and allow copy script
spreadsheet_title = "" #custom title
gc = gspread.oauth(
    credentials_filename='./credentials.json',
    authorized_user_filename='./authorized_user.json'
)
new_spreadsheet = gc.copy(spreadsheet_id,title=spreadsheet_title)
print(new_spreadsheet.id)
worksheet = gc.open_by_key(new_spreadsheet.id)
