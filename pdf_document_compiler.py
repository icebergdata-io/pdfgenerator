#%%
import os
import re
import glob
import json
from PIL import Image
from retry import retry
from fpdf import FPDF
from pytz import timezone
from datetime import datetime
from google.oauth2 import service_account
from concurrent.futures import ProcessPoolExecutor, as_completed
from pdf_images_generator import render_page
from aux_gcloud import pdf_to_gcloud_bucket
from aux_pdf import load_product_data_and_images
from dotenv import load_dotenv
from aux_context import get_sheet
from google.cloud import storage
from datetime import timedelta
from aux_gcloud import generate_signed_url
from pdf_ocr import add_ocr_layer

# Load environment variables
load_dotenv()


def process_page(json_files, i, image_folder, template_path, layout='horizontal'):
    # Load data for the first product
    product_data_1, image_files_1 = load_product_data_and_images(json_files[i], image_folder)

    # Check if there's a second product for this page
    if i + 1 < len(json_files):
        product_data_2, image_files_2 = load_product_data_and_images(json_files[i + 1], image_folder)
    else:
        product_data_2, image_files_2 = None, None  # No second product for this page

    # ... Debugging code ...

    # Add debugging information
    print(f"Processing page {i // 2 + 1}")
    print(f"Product 1: {product_data_1['sku']}")
    if product_data_2:
        print(f"Product 2: {product_data_2['sku']}")
    else:
        print("No second product")

    # ... Debugging code ...

    # Render the products on the page
    combined_img = render_page(product_data_1, image_files_1, product_data_2, image_files_2, template_path, layout)

    # Save the combined image temporarily
    output_path = f'output/pages/page_{i // 2 + 1}.png'
    combined_img.save(output_path)
    return output_path

def sanitize_filename(filename):
    return re.sub(r'[^\w\-_\.]', '_', filename)

def compile_pdf(layout='horizontal'):
    print("Compiling PDF...")
    # Define paths
    json_folder = 'output/clean'
    image_folder = 'output/images'
    template_path = 'Template 2 colors.png' if 'horizontal' in layout.lower() else 'Template 2_2.png'
    
    # Create output folders if they don't exist
    os.makedirs('output/pages', exist_ok=True)
    os.makedirs('output/pdfs', exist_ok=True)

    # Load all product JSON files
    json_files = sorted(glob.glob(f'{json_folder}/*.json'))
    
    # ... Debugging code ...

    print(f"Found {len(json_files)} JSON files")

    # ... Debugging code ...

    # Use ProcessPoolExecutor to parallelize image rendering
    with ProcessPoolExecutor() as executor:
        futures = []
        for i in range(0, len(json_files), 2):
            futures.append(executor.submit(process_page, json_files, i, image_folder, template_path, layout))

        saved_images = []
        for future in as_completed(futures):
            result = future.result()
            if result:
                saved_images.append(result)
            else:
                print("Warning: Empty result from process_page")

    # Sort the saved images to ensure correct order
    saved_images.sort()
    print(f"Generated {len(saved_images)} images")

    # Combine the saved images into a PDF
    pdf = FPDF('L', 'pt', (720, 1280))  # Correct dimensions for landscape mode
    for image_path in saved_images:
        if os.path.exists(image_path):
            pdf.add_page()
            pdf.image(image_path, x=0, y=0, w=1280, h=720)
            print(f"Added image to PDF: {image_path}")
        else:
            print(f"Warning: Image not found: {image_path}")

    timezoneodmx = timezone('America/Mexico_City')
    date_string_now_cdmx = datetime.now(timezoneodmx).strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{os.getenv('FILENAMETOSAVE')}_{date_string_now_cdmx}_{os.getenv('USER')}.pdf"
    filename = sanitize_filename(filename)
    pdf_path = os.path.join('output', 'pdfs', filename)

    # Before saving, check if the PDF has any pages
    if pdf.page_no() == 0:
        print("Error: PDF has no pages")
    else:
        print(f"PDF has {pdf.page_no()} pages")

    # Save the final PDF
    pdf.output(pdf_path)
    print(f"PDF saved: {pdf_path}")

    # Verify the saved PDF
    if os.path.exists(pdf_path):
        pdf_size = os.path.getsize(pdf_path)
        print(f"PDF size: {pdf_size} bytes")
        if pdf_size == 0:
            print("Error: Saved PDF is empty")
    else:
        print(f"Error: Failed to save PDF {pdf_path}")

    # ... Debugging code end ...

    # Upload the PDF to Google Cloud Storage

    pdf_path_OCR = add_ocr_layer(pdf_path)
    pdf_to_gcloud_bucket(pdf_path_OCR)

    # Example usage
    bucket_name = 'pdfgeneratorcoppel'
    blob_name = filename
    expiration_time = 90*24  # URL valid for 1 hour

    signed_url = generate_signed_url(bucket_name, blob_name, expiration_time)
    print(f"Downloadable link: {signed_url}")
    sh=get_sheet()
    sh[1].update_value('C16', signed_url)

    return signed_url

if __name__ == "__main__":
    compile_pdf("vertical")
# %%
