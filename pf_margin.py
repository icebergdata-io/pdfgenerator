import os
import sys
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def add_margins(input_path, output_path, margin=1*inch):
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        # Get the original page dimensions
        orig_width = float(page.mediabox.width)
        orig_height = float(page.mediabox.height)

        # Calculate new dimensions
        new_width = orig_width + 2*margin
        new_height = orig_height + 0.5*margin

        # Create a new blank page with the new dimensions
        c = canvas.Canvas('temp.pdf', pagesize=(new_width, new_height))
        c.showPage()
        c.save()

        # Read the blank page we just created
        new_page = PdfReader('temp.pdf').pages[0]

        # Merge the original page onto the new page (centered)
        new_page.merge_page(page)

        # Update the media box and crop box
        new_page.mediabox.lower_left = (0, 0)
        new_page.mediabox.upper_right = (new_width, new_height)
        new_page.cropbox.lower_left = (0, 0)
        new_page.cropbox.upper_right = (new_width, new_height)

        # Add the new page to the output PDF
        writer.add_page(new_page)

    # Write the output PDF
    with open(output_path, 'wb') as output_file:
        writer.write(output_file)

    # Remove the temporary file
    os.remove('temp.pdf')
if __name__ == "__main__":
    filename = 'DSA_2024-08-30_09-44-14__.pdf'
    add_margins(f'output/pdfs/{filename}', f"output/pdfs/2_{filename}",100)