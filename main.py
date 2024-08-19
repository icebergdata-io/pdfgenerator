import os
from aux_gcloud import load_dotenv_full
load_dotenv_full()
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from google.auth import default
from scraper_main import collector
from aux_context import get_sheet
from pdf_document_compiler import compile_pdf
from time import sleep
from datetime import datetime
import pytz

app = FastAPI()

@app.get("/")
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.get("/runner")
async def update_google_sheet():
    sh = get_sheet()
    # Update a cell in the spreadsheet

    started_at_cdmx = datetime.now(pytz.timezone('America/Mexico_City')).strftime("%Y-%m-%d %H:%M:%S")
    sh[1].update_value('E9', "started at: " + started_at_cdmx)
    sh[1].update_value('E10', "Collecting data")
    sh[1].update_value('C16', "---")

    print("Starting the process")
    # Run the scraper
    results = collector()
    # results = []
    print("Results collected")
    sh[1].update_value('E10', "Compiling PDf")

    # Compile the PDF
    compile_pdf()
    sh[1].update_value('E10', "Uploading PDf")
    
    sleep(1)
    # Upload the PDF to Google Cloud Storage
    sh[1].update_value('E10', "Uploaded")


    timezoneodmx = pytz.timezone('America/Mexico_City')
    date_string_now_cdmx = datetime.now(timezoneodmx).strftime("%Y-%m-%d_%H:%M:%S")

    sh[1].update_value('E9', "completed at: " + date_string_now_cdmx)
    return {"message": "Google Sheet updated!", "sheet_title": sh.title, "results": results}
    
if __name__ == "__main__":
    # import uvicorn
    import asyncio
    # uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    asyncio.run(update_google_sheet())