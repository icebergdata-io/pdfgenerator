import os
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from google.auth import default
from google.api_core.exceptions import GoogleAPIError
from scraper_main import collector
from aux_context import get_sheet
from pdf_document_compiler import compile_pdf
from datetime import datetime
import pytz
import uvicorn
from aux_gcloud import load_dotenv_full
from googleapiclient.errors import HttpError
from requests.exceptions import RequestException

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
log_messages = []

def log_message(message: str):
    """Add a timestamped message to the log"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_messages.append(f"[{timestamp}] {message}")
    print(f"[{timestamp}] {message}")

@app.get("/", response_class=HTMLResponse)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.get("/runner", response_class=HTMLResponse)
async def show_loading_page(request: Request):
    """Show the loading page"""
    global log_messages
    log_messages = []
    return templates.TemplateResponse("loading.html", {"request": request})

@app.get("/logs")
async def get_logs():
    """Return all logged messages"""
    return JSONResponse({"logs": log_messages})

@app.get("/generate_pdf")
async def generate_pdf():
    """Generate PDFs and return URLs"""
    global generation_in_progress
    
    if generation_in_progress:
        return {"url": None}
    
    generation_in_progress = True
    sh = None
    
    try:
        # Initialize Google Sheet connection
        try:
            sh = get_sheet()
            log_message("Successfully connected to Google Sheets")
        except GoogleAPIError as e:
            log_message(f"Failed to connect to Google Sheets: {str(e)}")
            raise HTTPException(status_code=503, detail="Google Sheets connection failed")

        # Start process and update timestamp
        started_at_cdmx = datetime.now(pytz.timezone('America/Mexico_City')).strftime("%Y-%m-%d %H:%M:%S")
        log_message(f"Process started at {started_at_cdmx}")
        
        try:
            sh[1].update_value('E9', "started at: " + started_at_cdmx)
            sh[1].update_value('E10', "Collecting data")
            sh[1].update_value('C16', "-------- generando pdf -----")
            sh[1].update_value('C17', "-------- generando pdf -----")
            log_message("Sheet values initialized")
        except Exception as e:
            log_message(f"Failed to update sheet values: {str(e)}")
            raise HTTPException(status_code=503, detail="Failed to update Google Sheet")

        # Collect data
        try:
            log_message("Starting data collection process")
            results = collector()
            log_message("Data collection completed successfully")
        except RequestException as e:
            log_message(f"Network error during data collection: {str(e)}")
            raise HTTPException(status_code=503, detail="Data collection failed - network error")
        except Exception as e:
            log_message(f"Error during data collection: {str(e)}")
            raise HTTPException(status_code=500, detail="Data collection failed")

        # Get layout and compile PDF
        try:
            log_message("Starting PDF compilation")
            sh[1].update_value('E10', "Compiling PDF")
            layout = sh[1].get_value('E13')
            layout = "horizontal" if "horizontal" in layout.lower() else "vertical"
            log_message(f"Using {layout} layout for PDF")
        except Exception as e:
            log_message(f"Failed to get layout configuration: {str(e)}")
            raise HTTPException(status_code=503, detail="Failed to get layout configuration")

        # Generate PDFs
        try:
            log_message("Generating PDFs...")
            non_ocr_url, ocr_url = compile_pdf(layout)
            log_message("PDFs generated successfully")
        except Exception as e:
            log_message(f"PDF compilation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"PDF compilation failed: {str(e)}")

        # Update final status
        try:
            sh[1].update_value('C16', non_ocr_url)
            sh[1].update_value('C17', ocr_url)
            sh[1].update_value('E10', "PDFs Uploaded")
            log_message("PDFs uploaded to storage")
            
            timezoneodmx = pytz.timezone('America/Mexico_City')
            date_string_now_cdmx = datetime.now(timezoneodmx).strftime("%Y-%m-%d %H:%M:%S")
            sh[1].update_value('E9', "completed at: " + date_string_now_cdmx)
            log_message(f"Process completed at {date_string_now_cdmx}")
        except Exception as e:
            log_message(f"Warning: Failed to update final sheet values: {str(e)}")
            # Don't raise here as PDFs are already generated
            
        return {"url": non_ocr_url}
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        # Log unexpected errors with their type
        error_type = type(e).__name__
        error_message = f"Unexpected error ({error_type}): {str(e)}"
        log_message(error_message)
        if sh:
            try:
                sh[1].update_value('E10', error_message)
            except:
                log_message("Failed to update error message in sheet")
        raise HTTPException(status_code=500, detail=error_message)
        
    finally:
        generation_in_progress = False

def start_server():
    """Starts the uvicorn server"""
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_server()