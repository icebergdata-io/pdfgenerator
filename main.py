import os
from aux_gcloud import load_dotenv_full
load_dotenv_full()
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from google.auth import default
from scraper_main import collector
from aux_context import get_sheet
from pdf_document_compiler import compile_pdf
from time import sleep
from datetime import datetime
import pytz
import uvicorn

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Jinja2 templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.get("/runner", response_class=HTMLResponse)
async def update_google_sheet(request: Request):
    return templates.TemplateResponse("loading.html", {"request": request})

@app.get("/generate_pdf")
async def generate_pdf():
    sh = get_sheet()
    # Update a cell in the spreadsheet

    started_at_cdmx = datetime.now(pytz.timezone('America/Mexico_City')).strftime("%Y-%m-%d %H:%M:%S")
    sh[1].update_value('E9', "started at: " + started_at_cdmx)
    sh[1].update_value('E10', "Collecting data")
    sh[1].update_value('C16', "---")

    print("Starting the process")
    # Run the scraper
    results = collector()
    print("Results collected")
    sh[1].update_value('E10', "Compiling PDF")
    layout = sh[1].get_value('E13')
    if "horizontal" in layout.lower():
        layout = "horizontal"
    elif "vertical" in layout.lower():
        layout = "vertical"
        
    print(f"Layout: {layout}")
    # Compile the PDF
    compile_pdf(layout)
    sh[1].update_value('E10', "Uploading PDF")
    
    sleep(1)
    # Upload the PDF to Google Cloud Storage
    sh[1].update_value('E10', "Uploaded")

    timezoneodmx = pytz.timezone('America/Mexico_City')
    date_string_now_cdmx = datetime.now(timezoneodmx).strftime("%Y-%m-%d %H:%M:%S")

    sh[1].update_value('E9', "completed at: " + date_string_now_cdmx)
    
    # Get the signed URL from the Google Sheet
    signed_url = sh[1].get_value('C16')

    
    return {"url": signed_url}

if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host=host, port=port)