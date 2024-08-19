import pygsheets
from google.auth import default
import os

credentials, project = default()
credentials = credentials.with_scopes(['https://www.googleapis.com/auth/spreadsheets'])
gc = pygsheets.authorize(custom_credentials=credentials)

gheet_id = os.getenv('GSHEET_ID')
sh = gc.open_by_key(gheet_id)

def get_sheet():
    return sh