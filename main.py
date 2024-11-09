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

    started_at_cdmx = datetime.now(pytz.timezone('America/Mexico_City')).strftime("%Y-%m-%d %H:%M:%S")
    sh[1].update_value('E9', "started at: " + started_at_cdmx)
    sh[1].update_value('E10', "Collecting data")
    
    # Clear and update both URL cells
    sh[1].update_value('C16', "-------- generando pdf -----")
    sh[1].update_value('C17', "-------- generando pdf -----")

    print("Starting the process")
    results = collector()
    print("Results collected")
    
    sh[1].update_value('E10', "Compiling PDF")
    layout = sh[1].get_value('E13')
    if "horizontal" in layout.lower():
        layout = "horizontal"
    elif "vertical" in layout.lower():
        layout = "vertical"
        
    print(f"Layout: {layout}")
    
    # Compile PDF and get both URLs
    non_ocr_url, ocr_url = compile_pdf(layout)
    sh[1].update_value('E10', "PDFs Uploaded")
    
    sleep(1)
    
    timezoneodmx = pytz.timezone('America/Mexico_City')
    date_string_now_cdmx = datetime.now(timezoneodmx).strftime("%Y-%m-%d %H:%M:%S")
    sh[1].update_value('E9', "completed at: " + date_string_now_cdmx)
    
    return {
        "non_ocr_url": non_ocr_url,
        "ocr_url": ocr_url
    }

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8080))
    # Uncomment the following line to run the server directly
    uvicorn.run(app, host=host, port=port)
    
    # For development/testing, use this to run generate_pdf directly
    # import asyncio
    # asyncio.run(generate_pdf())