from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import os
import pygsheets
from google.auth import default
from scraper_main import collector
from aux_context import get_sheet
from pdf_document_compiler import compile_pdf

app = FastAPI()

@app.get("/")
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.get("/runner")
async def update_google_sheet():
    sh = get_sheet()
    # Update a cell in the spreadsheet
    sh[1].update_value('E10', "starting")

    print("Starting the process")
    # Run the scraper
    results = collector()
    print("Results collected")
    
    # Update the Google Sheet
    for i, result in enumerate(results):
        sh[3].update_value(f'A{i+2}', result['name'])
        sh[3].update_value(f'B{i+2}', result['description'])
        sh[3].update_value(f'C{i+2}', result['marca'])
        sh[3].update_value(f'D{i+2}', result['sku'])
        sh[3].update_value(f'E{i+2}', result['category'])
        sh[3].update_value(f'E{i+2}', result['pos'])
    # Compile the PDF
    compile_pdf()

    return {"message": "Google Sheet updated!", "sheet_title": sh.title, "results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
