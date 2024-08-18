from fastapi import FastAPI
import os
import pygsheets
from google.auth import default

app = FastAPI()

@app.get("/")
async def update_google_sheet():
    # Automatically load the credentials and project info from ADC
    credentials, project = default()

    # Ensure the credentials have the correct scopes
    credentials = credentials.with_scopes(['https://www.googleapis.com/auth/spreadsheets'])

    # Authorize pygsheets using the loaded credentials
    gc = pygsheets.authorize(custom_credentials=credentials)

    # Use the Google Sheets API
    gheet_id = os.getenv('GSHEET_ID')
    sh = gc.open_by_key(gheet_id)

    # Update a cell in the spreadsheet
    sh[1].update_value('E10', "Conectado2")

    return {"message": "Google Sheet updated!", "sheet_title": sh.title}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
