import os
import io
import logging
import subprocess
from typing import List
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfWriter, PdfReader
from pf_margin import add_margins

# Configure logging - only show INFO and above, with a clean format
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

def check_pdftoppm_installation() -> None:
    """Check if pdftoppm is installed and accessible."""
    try:
        subprocess.run(
            ["pdftoppm", "-v"], 
            check=True, 
            capture_output=True,
            text=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise RuntimeError(
            "pdftoppm not found. Please install poppler-utils package:\n"
            "Ubuntu/Debian: sudo apt-get install poppler-utils\n"
            "MacOS: brew install poppler\n"
            "Windows: Download from http://blog.alivate.com.au/poppler-windows/"
        )

def add_ocr_layer(input_pdf: str) -> str:
    """
    Add OCR layer to PDF file and adjust margins.
    
    Args:
        input_pdf: Path to input PDF file
    Returns:
        Path to the processed PDF file
    """
    logger.info(f"Processing PDF: {os.path.basename(input_pdf)}")
    
    try:
        # Verify poppler installation
        check_pdftoppm_installation()
        
        # Convert PDF to images
        images = convert_from_path(input_pdf)
        logger.info(f"Converting {len(images)} pages")
        
        # Create new PDF with OCR layer
        pdf_writer = PdfWriter()
        
        for i, image in enumerate(images, 1):
            # Process each image
            processed_img = Image.new(
                'RGB',
                (image.width, image.height + 100),
                (255, 255, 255)
            )
            processed_img.paste(image, (0, 50))
            
            # Create searchable PDF page
            img_byte_arr = io.BytesIO()
            processed_img.save(img_byte_arr, format='PDF')
            img_pdf_bytes = img_byte_arr.getvalue()
            ocr_pdf_bytes = pytesseract.image_to_pdf_or_hocr(processed_img, extension='pdf')
            
            # Merge image and OCR layers
            image_pdf = PdfReader(io.BytesIO(img_pdf_bytes))
            ocr_pdf = PdfReader(io.BytesIO(ocr_pdf_bytes))
            
            page = image_pdf.pages[0]
            page.merge_page(ocr_pdf.pages[0])
            pdf_writer.add_page(page)
            
            if i % 5 == 0:  # Log progress every 5 pages
                logger.info(f"Processed {i}/{len(images)} pages")
        
        # Backup original file
        input_pdf_backup = input_pdf.replace(".pdf", "_non_ocr.pdf")
        os.rename(input_pdf, input_pdf_backup)
        
        # Save new PDF with OCR
        with open(input_pdf, 'wb') as output_file:
            pdf_writer.write(output_file)
        
        # Add margins
        add_margins(input_pdf, input_pdf, 100)
        logger.info("PDF processing completed successfully")
        
        return input_pdf
        
    except Exception as e:
        logger.error(f"PDF processing failed: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        test_pdf = 'output/pdfs/DSA_2024-08-30_09-27-40___non_ocr.pdf'
        output_pdf = add_ocr_layer(test_pdf)
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")