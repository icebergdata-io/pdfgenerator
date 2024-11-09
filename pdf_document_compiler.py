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
import shutil  # Añadido el import de shutil

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
    json_folder = 'output/clean'
    image_folder = 'output/images'
    template_path = 'Template 2 colors.png' if 'horizontal' in layout.lower() else 'Template 2_2.png'
    
    os.makedirs('output/pages', exist_ok=True)
    os.makedirs('output/pdfs', exist_ok=True)

    # Load and sort JSON files
    json_files = sorted(glob.glob(f'{json_folder}/*.json'))
    print(f"Found {len(json_files)} JSON files")

    # Generate PDF pages
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

    saved_images.sort()
    print(f"Generated {len(saved_images)} images")

    # Generate base PDF
    pdf = FPDF('L', 'pt', (720, 1280))
    for image_path in saved_images:
        if os.path.exists(image_path):
            pdf.add_page()
            pdf.image(image_path, x=0, y=0, w=1280, h=720)
            print(f"Added image to PDF: {image_path}")
        else:
            print(f"Warning: Image not found: {image_path}")

    # Generate filenames
    timezoneodmx = timezone('America/Mexico_City')
    date_string_now_cdmx = datetime.now(timezoneodmx).strftime("%Y-%m-%d_%H-%M-%S")
    base_filename = f"{os.getenv('FILENAMETOSAVE')}_{date_string_now_cdmx}_{os.getenv('USER')}"
    base_filename = sanitize_filename(base_filename)
    
    # Save and process non-OCR version first
    non_ocr_filename = f"{base_filename}_non_ocr.pdf"
    non_ocr_path = os.path.join('output', 'pdfs', non_ocr_filename)
    pdf.output(non_ocr_path)
    
    # Upload non-OCR version and get URL immediately
    print("Uploading non-OCR version...")
    pdf_to_gcloud_bucket(non_ocr_path)
    bucket_name = 'pdfgeneratorcoppel'
    expiration_time = 90*24
    non_ocr_url = generate_signed_url(bucket_name, non_ocr_filename, expiration_time)
    
    # Update sheet with non-OCR URL immediately
    sh = get_sheet()
    sh[1].update_value('C16', non_ocr_url)
    print("Non-OCR PDF URL updated in sheet")

    # Start OCR process
    print("Starting OCR process...")
    ocr_filename = f"{base_filename}_ocr.pdf"
    ocr_path = os.path.join('output', 'pdfs', ocr_filename)
    shutil.copy2(non_ocr_path, ocr_path)
    
    # Update sheet to show OCR is in progress
    sh[1].update_value('C17', "-------- procesando OCR -----")
    
    # Process OCR
    ocr_path = add_ocr_layer(ocr_path)
    pdf_to_gcloud_bucket(ocr_path)
    ocr_url = generate_signed_url(bucket_name, ocr_filename, expiration_time)
    
    # Update sheet with OCR URL
    sh[1].update_value('C17', ocr_url)
    print("OCR PDF URL updated in sheet")

    return non_ocr_url, ocr_url

if __name__ == "__main__":
    compile_pdf("vertical")