import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfWriter, PdfReader
import io
from PIL import Image
import os 
import subprocess
from pf_margin import add_margins

def add_ocr_layer(input_pdf):
    print(f"Current working directory: {os.getcwd()}")
    print(f"Contents of current directory: {os.listdir('.')}")
    print(f"PATH: {os.environ.get('PATH')}")
    
    subprocess.run(["pdftoppm", "-v"], check=True, capture_output=True)
    print("Poppler is installed and accessible")

    images = convert_from_path(input_pdf)
    print(f"Successfully converted PDF to {len(images)} images")


    pdf_writer = PdfWriter()

    for image in images:
        # Get original image size
        orig_width, orig_height = image.size
        
        # Create a new image with padding
        padding = 50  # Adjust this value as needed
        new_img = Image.new('RGB', (orig_width, orig_height + padding * 2), (255, 255, 255))
        new_img.paste(image, (0, padding))

        # Perform OCR on the padded image
        ocr_text = pytesseract.image_to_pdf_or_hocr(new_img, extension='pdf')

        # Create a PDF page from the padded image
        img_byte_arr = io.BytesIO()
        new_img.save(img_byte_arr, format='PDF')
        img_byte_arr = img_byte_arr.getvalue()

        # Merge the image PDF and the OCR PDF
        image_pdf = PdfReader(io.BytesIO(img_byte_arr))
        ocr_pdf = PdfReader(io.BytesIO(ocr_text))

        page = image_pdf.pages[0]
        page.merge_page(ocr_pdf.pages[0])

        pdf_writer.add_page(page)

    #rename old file
    input_pdf_new_name = input_pdf.replace(".pdf", "_non_ocr.pdf")
    os.rename(input_pdf, input_pdf_new_name)

    # Save the result
    with open(input_pdf, 'wb') as f:
        pdf_writer.write(f)

    #add margin
    add_margins(input_pdf, input_pdf, 100)

    return input_pdf


if __name__ == "__main__":
    input_pdf = 'output/pdfs/DSA_2024-08-30_09-27-40___non_ocr.pdf'
    output_pdf = add_ocr_layer(input_pdf)
    print(f"Created searchable PDF: {output_pdf}")