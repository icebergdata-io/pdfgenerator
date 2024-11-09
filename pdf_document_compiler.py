import os
import re
import glob
import json
from PIL import Image
from retry import retry
from fpdf import FPDF
from pytz import timezone
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
from pdf_images_generator import render_page
from aux_gcloud import pdf_to_gcloud_bucket, generate_signed_url
from aux_pdf import load_product_data_and_images  # Fixed import statement
from aux_context import get_sheet
from pdf_ocr import add_ocr_layer
import shutil
from typing import Tuple, List, Optional
from dataclasses import dataclass
from PIL.Image import Image as PILImage


@dataclass
class PageResult:
    page_num: int
    image_path: str
    skus: List[str]  # Store SKUs for debugging

class PDFCompilationError(Exception):
    """Base exception for PDF compilation errors"""
    pass

class ImageProcessingError(PDFCompilationError):
    """Raised when there's an error processing or saving images"""
    pass

class JSONProcessingError(PDFCompilationError):
    """Raised when there's an error processing JSON files"""
    pass

def process_page(json_files: List[str], i: int, image_folder: str, template_path: str, layout: str = 'horizontal') -> PageResult:
    """
    Process a single page of the PDF, containing one or two products.
    
    Args:
        json_files: List of JSON file paths
        i: Current index in json_files
        image_folder: Path to folder containing product images
        template_path: Path to template image
        layout: 'horizontal' or 'vertical' layout
        
    Returns:
        PageResult containing page number, image path and SKUs
    
    Raises:
        JSONProcessingError: If JSON file cannot be loaded or is invalid
        ImageProcessingError: If image processing fails
    """
    
    # Load first product data
    try:
        product_data_1, image_files_1 = load_product_data_and_images(json_files[i], image_folder)
    except (json.JSONDecodeError, KeyError) as e:
        raise JSONProcessingError(f"Failed to load first product JSON at index {i}: {str(e)}")
    except FileNotFoundError as e:
        raise JSONProcessingError(f"Product JSON or image files not found at index {i}: {str(e)}")

    skus = [str(product_data_1['sku'])]
    product_data_2 = None
    image_files_2 = None

    # Load second product data if available
    if i + 1 < len(json_files):
        try:
            product_data_2, image_files_2 = load_product_data_and_images(json_files[i + 1], image_folder)
            skus.append(str(product_data_2['sku']))
        except (json.JSONDecodeError, KeyError) as e:
            raise JSONProcessingError(f"Failed to load second product JSON at index {i+1}: {str(e)}")
        except FileNotFoundError as e:
            raise JSONProcessingError(f"Second product JSON or image files not found at index {i+1}: {str(e)}")

    print(f"Processing page {i // 2 + 1} with SKUs: {', '.join(skus)}")

    try:
        combined_img = render_page(product_data_1, image_files_1, product_data_2, image_files_2, template_path, layout)
    except Exception as e:
        raise ImageProcessingError(f"Failed to render page {i // 2 + 1} with SKUs {skus}: {str(e)}")

    page_num = i // 2 + 1
    output_path = f'output/pages/page_{page_num:03d}.png'

    try:
        combined_img.save(output_path)
    except Exception as e:
        raise ImageProcessingError(f"Failed to save page {page_num} to {output_path}: {str(e)}")

    return PageResult(page_num=page_num, image_path=output_path, skus=skus)

def get_index_from_filename(filename: str) -> int:
    """Extract index from filename pattern '000_category_url.json'"""
    try:
        return int(os.path.basename(filename).split('_')[0])
    except (ValueError, IndexError) as e:
        raise JSONProcessingError(f"Invalid filename format for {filename}: {str(e)}")

def sanitize_filename(filename: str) -> str:
    """Remove invalid characters from filename"""
    return re.sub(r'[^\w\-_\.]', '_', filename)

def compile_pdf(layout: str = 'horizontal') -> Tuple[str, str]:
    """
    Compile PDF from product data and images.
    
    Args:
        layout: 'horizontal' or 'vertical' layout
        
    Returns:
        Tuple of (non_ocr_url, ocr_url)
        
    Raises:
        PDFCompilationError: If PDF compilation fails
        Various specific exceptions for different failure modes
    """
    
    print("Starting PDF compilation...")
    json_folder = 'output/clean'
    image_folder = 'output/images'
    template_path = 'Template 2 colors.png' if 'horizontal' in layout.lower() else 'Template 2_2.png'

    # Create output directories
    os.makedirs('output/pages', exist_ok=True)
    os.makedirs('output/pdfs', exist_ok=True)

    # Load and sort JSON files
    json_files = glob.glob(f'{json_folder}/*.json')
    if not json_files:
        raise JSONProcessingError("No JSON files found in output/clean directory")
        
    try:
        json_files.sort(key=get_index_from_filename)
    except JSONProcessingError as e:
        raise PDFCompilationError(f"Failed to sort JSON files: {str(e)}")

    print(f"Processing {len(json_files)} JSON files")

    # Generate PDF pages
    page_results: List[PageResult] = []
    with ProcessPoolExecutor() as executor:
        futures = []
        for i in range(0, len(json_files), 2):
            futures.append(executor.submit(process_page, json_files, i, image_folder, template_path, layout))

        for future in as_completed(futures):
            try:
                result = future.result()
                page_results.append(result)
            except (JSONProcessingError, ImageProcessingError) as e:
                print(f"Error processing page: {str(e)}")
                # Continue processing other pages despite errors
            
    if not page_results:
        raise PDFCompilationError("No pages were successfully generated")

    # Sort by page number
    page_results.sort(key=lambda x: x.page_num)
    
    # Print order verification
    print("\nVerifying page order:")
    for result in page_results:
        print(f"Page {result.page_num}: SKUs {result.skus}")

    # Generate PDF
    pdf = FPDF('L', 'pt', (720, 1280))
    for result in page_results:
        if not os.path.exists(result.image_path):
            print(f"Warning: Missing image for page {result.page_num}")
            continue
            
        pdf.add_page()
        pdf.image(result.image_path, x=0, y=0, w=1280, h=720)
        print(f"Added page {result.page_num} to PDF")

    # Generate filenames
    timezoneodmx = timezone('America/Mexico_City')
    date_string_now_cdmx = datetime.now(timezoneodmx).strftime("%Y-%m-%d_%H-%M-%S")
    base_filename = f"{os.getenv('FILENAMETOSAVE')}_{date_string_now_cdmx}_{os.getenv('USER')}"
    base_filename = sanitize_filename(base_filename)

    # Save non-OCR version
    non_ocr_filename = f"{base_filename}_non_ocr.pdf"
    non_ocr_path = os.path.join('output', 'pdfs', non_ocr_filename)
    
    try:
        pdf.output(non_ocr_path)
    except Exception as e:
        raise PDFCompilationError(f"Failed to save non-OCR PDF: {str(e)}")

    # Upload and get URL
    print("Uploading non-OCR version...")
    try:
        pdf_to_gcloud_bucket(non_ocr_path)
        bucket_name = 'pdfgeneratorcoppel'
        non_ocr_url = generate_signed_url(bucket_name, non_ocr_filename, 90*24)
    except Exception as e:
        raise PDFCompilationError(f"Failed to upload non-OCR PDF: {str(e)}")

    # Update sheet
    sh = get_sheet()
    sh[1].update_value('C16', non_ocr_url)
    print("Non-OCR PDF URL updated in sheet")

    # Process OCR version
    print("Starting OCR process...")
    ocr_filename = f"{base_filename}_ocr.pdf"
    ocr_path = os.path.join('output', 'pdfs', ocr_filename)
    
    try:
        shutil.copy2(non_ocr_path, ocr_path)
        sh[1].update_value('C17', "-------- procesando OCR -----")
        
        ocr_path = add_ocr_layer(ocr_path)
        pdf_to_gcloud_bucket(ocr_path)
        ocr_url = generate_signed_url(bucket_name, ocr_filename, 90*24)
        
        sh[1].update_value('C17', ocr_url)
        print("OCR PDF URL updated in sheet")
    except Exception as e:
        raise PDFCompilationError(f"Failed to process OCR version: {str(e)}")

    return non_ocr_url, ocr_url

if __name__ == "__main__":
    try:
        non_ocr_url, ocr_url = compile_pdf("vertical")
        print("PDF compilation completed successfully")
        print(f"Non-OCR URL: {non_ocr_url}")
        print(f"OCR URL: {ocr_url}")
    except PDFCompilationError as e:
        print(f"PDF compilation failed: {str(e)}")
        raise