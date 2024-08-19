import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfWriter, PdfReader
import io
from PIL import Image

POPPLER_PATH = "/opt/homebrew/Cellar/poppler/24.04.0_1/bin"

def add_ocr_layer(input_pdf, output_pdf):
    # Convert PDF to list of images
    images = convert_from_path(input_pdf, poppler_path=POPPLER_PATH)

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

    # Save the result
    with open(output_pdf, 'wb') as f:
        pdf_writer.write(f)

if __name__ == "__main__":
    input_pdf = 'output/product_catalog.pdf'
    output_pdf = 'output/product_catalog_searchable.pdf'
    add_ocr_layer(input_pdf, output_pdf)
    print(f"Created searchable PDF: {output_pdf}")