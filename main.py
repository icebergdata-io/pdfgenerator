import os
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from google.auth import default
from scraper_main import collector
from aux_context import get_sheet
from pdf_document_compiler import compile_pdf
from datetime import datetime
import pytz
import uvicorn
from aux_gcloud import load_dotenv_full

# Load environment variables
load_dotenv_full()

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

# Global state
generation_in_progress = False

@app.get("/", response_class=HTMLResponse)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.get("/runner", response_class=HTMLResponse)
async def show_loading_page(request: Request):
    """Show the loading page"""
    return templates.TemplateResponse("loading.html", {"request": request})

@app.get("/generate_pdf")
async def generate_pdf():
    """Generate PDFs and return URLs"""
    global generation_in_progress
    
    if generation_in_progress:
        return {"url": None}
    
    try:
        generation_in_progress = True
        sh = get_sheet()

        started_at_cdmx = datetime.now(pytz.timezone('America/Mexico_City')).strftime("%Y-%m-%d %H:%M:%S")
        sh[1].update_value('E9', "started at: " + started_at_cdmx)
        sh[1].update_value('E10', "Collecting data")
        
        sh[1].update_value('C16', "-------- generando pdf -----")
        sh[1].update_value('C17', "-------- generando pdf -----")

        print("Starting the process")
        results = collector()
        print("Results collected")
        
        sh[1].update_value('E10', "Compiling PDF")
        layout = sh[1].get_value('E13')
        layout = "horizontal" if "horizontal" in layout.lower() else "vertical"
        
        print(f"Layout: {layout}")
        
        non_ocr_url, ocr_url = compile_pdf(layout)
        
        sh[1].update_value('C16', non_ocr_url)
        sh[1].update_value('C17', ocr_url)
        sh[1].update_value('E10', "PDFs Uploaded")
        
        timezoneodmx = pytz.timezone('America/Mexico_City')
        date_string_now_cdmx = datetime.now(timezoneodmx).strftime("%Y-%m-%d %H:%M:%S")
        sh[1].update_value('E9', "completed at: " + date_string_now_cdmx)
        
        return {"url": non_ocr_url}
        
    except Exception as e:
        print(f"Error in PDF generation: {str(e)}")
        sh[1].update_value('E10', f"Error: {str(e)}")
        return {"url": None}
    finally:
        generation_in_progress = False

def start_server():
    """Starts the uvicorn server"""
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_server()