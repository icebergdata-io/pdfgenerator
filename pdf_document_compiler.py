import os
import glob
from concurrent.futures import ProcessPoolExecutor, as_completed
from PIL import Image
from fpdf import FPDF
from datetime import datetime
from pytz import timezone
from google.cloud import storage 
from google.auth import default

from pdf_images_generator import render_page
from aux_pdf import load_product_data_and_images

def pdf_to_gcloud_bucket(pdf_file):
    credentials, project = default()

    # Set up credentials based on GOOGLE_APPLICATION_CREDENTIALS
    storage_client = storage.Client(credentials=credentials, project=credentials.project_id)

    # Set up bucket
    bucket_name = 'pdfgeneratorcoppel'
    bucket = storage_client.bucket(bucket_name)

    # Upload the PDF
    blob = bucket.blob(pdf_file)
    blob.upload_from_filename(pdf_file)
    print(f"PDF uploaded to Google Cloud Storage: {pdf_file}")

def process_page(json_files, i, image_folder, template_path):
    # Load data for the first product
    product_data_1, image_files_1 = load_product_data_and_images(json_files[i], image_folder)

    # Check if there's a second product for this page
    if i + 1 < len(json_files):
        product_data_2, image_files_2 = load_product_data_and_images(json_files[i + 1], image_folder)
    else:
        product_data_2, image_files_2 = None, None  # No second product for this page

    # Render the products on the page
    combined_img = render_page(product_data_1, image_files_1, product_data_2, image_files_2, template_path)

    # Save the combined image temporarily
    output_path = f'output/pages/page_{i // 2 + 1}.png'
    combined_img.save(output_path)
    return output_path

def compile_pdf():
    print("Compiling PDF...")
    # Define paths
    json_folder = 'output/clean'
    image_folder = 'output/images'
    template_path = 'Template 2 colors.png'
    
    # Create output folders if they don't exist
    os.makedirs('output/pages', exist_ok=True)
    os.makedirs('output/pdfs', exist_ok=True)

    # Load all product JSON files
    json_files = sorted(glob.glob(f'{json_folder}/*.json'))

    # Use ProcessPoolExecutor to parallelize image rendering
    with ProcessPoolExecutor() as executor:
        futures = []
        for i in range(0, len(json_files), 2):
            futures.append(executor.submit(process_page, json_files, i, image_folder, template_path))

        saved_images = []
        for future in as_completed(futures):
            saved_images.append(future.result())

    # Sort the saved images to ensure correct order
    saved_images.sort()

    # Combine the saved images into a PDF
    pdf = FPDF('L', 'pt', (720, 1280))  # Correct dimensions for landscape mode
    for image_path in saved_images:
        pdf.add_page()
        pdf.image(image_path, x=0, y=0, w=1280, h=720)

    timezoneodmx = timezone('America/Mexico_City')
    date_string_now_cdmx = datetime.now(timezoneodmx).strftime("%Y-%m-%d_%H:%M:%S")
    filename = f"product_catalog_{date_string_now_cdmx}.pdf"
    pdf_path = f"output/pdfs/{filename}"
    # Save the final PDF
    pdf.output(pdf_path)
    print(f"PDF saved: {pdf_path}")

    # Upload the PDF to Google Cloud Storage
    pdf_to_gcloud_bucket(pdf_path)

if __name__ == "__main__":
    compile_pdf()