import os
import glob
import json
from PIL import Image, ImageDraw, ImageFont
import pillow_avif  # Import for AVIF image support
from textwrap import wrap
from fpdf import FPDF

# Function to draw text on the image
def draw_text(drawer, text, position, font, fill):
    drawer.text(position, text, font=font, fill=fill)

# Function to draw product features
def draw_features(drawer, features, x_position, y_position, font, max_features_per_column, x_offset):
    for idx, feature in enumerate(features):
        feature_text = f"{feature['name']}: {feature['value']}"
        
        if idx == max_features_per_column:
            x_position += 300  # Move to the second column
            y_position = 430   # Reset y position for the second column

        draw_text(drawer, feature_text, (x_position, y_position), font, (51, 51, 51))
        y_position += 20

# Function to draw product images on the image
def draw_product_images(img, image_files, y_offset, x_offset):
    for idx, image_file in enumerate(image_files[:4]):
        product_image = Image.open(image_file).resize((110, 110), Image.Resampling.LANCZOS)
        img_x_offset = 30 + (idx * 160) + x_offset
        img.paste(product_image, (img_x_offset, y_offset))

# Function to render the page for a single product
def render_page(product_data, image_files, template_image, x_offset_input):
    # Extracting data from product JSON
    product_name = product_data['name']
    product_description = product_data['description']
    subcategory = product_data['sub_cat']
    model = product_data['modelo']
    brand = product_data['marca'].title()
    sku = f'SKU: {str(product_data["sku"])}'
    category = str(product_data['category']) if str(product_data['category']) != 'nan' else 'Category'

    # Prepare text and descriptions for rendering
    brand_model = f'Marca: {brand} | Modelo: {model}' if model and brand else f'Modelo: {model}' if model else f'Marca: {brand}'
    product_name = wrap(product_name, 100)[0]
    description_text = '\n'.join(wrap(product_description, 75))

    # Load and resize the background image
    background_image = Image.open(template_image).resize((1280, 720), Image.Resampling.LANCZOS)
    img = background_image
    drawer = ImageDraw.Draw(img)

    # Define fonts for rendering text
    font_bold = ImageFont.truetype('Calibri Bold.ttf', 27) 
    font_bold_small = ImageFont.truetype('Calibri Bold.ttf', 20) 
    font_bold_medium = ImageFont.truetype('Calibri Bold.ttf', 23) 
    font_regular = ImageFont.truetype('Calibri Regular.ttf', 18)
    font_bold_large = ImageFont.truetype('Calibri Bold.ttf', 36)

    x_offset = x_offset_input

    # Draw product information on the image
    draw_text(drawer, f'{category}', (30 + x_offset, 120), font_bold_large, (33, 90, 168))
    draw_text(drawer, f'{subcategory}', (30 + x_offset, 172), font_bold_medium, (33, 90, 168))
    draw_text(drawer, sku, (420 + x_offset, 172), font_bold_small, (33, 90, 168))
    draw_text(drawer, brand_model, (30 + x_offset, 200), font_bold_small, (100, 100, 100))
    draw_text(drawer, product_name, (30 + x_offset, 220), font_bold_medium, (100, 100, 100))

    # Paste product images on the template
    draw_product_images(img, image_files, 270, x_offset)

    # Draw features and product description
    draw_text(drawer, 'Características del producto', (30 + x_offset, 400), font_bold_medium, (104, 166, 225))
    draw_features(drawer, product_data['descr_list'], 30 + x_offset, 430, font_regular, 5, x_offset)
    draw_text(drawer, 'Descripción de producto', (30 + x_offset, 550), font_bold_medium, (104, 166, 225))
    draw_text(drawer, description_text, (30 + x_offset, 580), font_regular, (51, 51, 51))

    return img

# Function to create a PDF with two products on one page
def create_pdf_with_two_products(product_data_1, image_files_1, product_data_2, image_files_2, template_image):
    # Render the first product and save it as a temporary image
    img_left = render_page(product_data_1, image_files_1, template_image, x_offset_input=0)
    img_left.save('output/temp_image_left.png')

    # Render the second product on the same image, adjusting the offset
    img_right = render_page(product_data_2, image_files_2, 'output/temp_image_left.png', x_offset_input=630)
    img_right.save('output/temp_image_right.png')

    # Create a PDF with the combined image
    pdf = FPDF('L', 'pt', (720, 1280))
    pdf.add_page()
    pdf.image('output/temp_image_right.png', x=0, y=0, w=1280, h=720)

    # Save the PDF
    pdf_path = f'output/{product_data_1["sku"]}_{product_data_2["sku"]}.pdf'
    pdf.output(pdf_path)
    print(f"PDF created: {pdf_path}")

# Function to load product data and images
def load_product_data_and_images(json_file, image_folder):
    with open(json_file, 'r') as f:
        product_data = json.load(f)
    
    sku = product_data['sku']
    images_path = os.path.join(f'{image_folder}/{sku}')
    image_files = sorted(glob.glob(os.path.join(images_path, "*.jpg")) + glob.glob(os.path.join(images_path, "*.avif")))
    
    return product_data, image_files

# Main execution
def main():
    # Define paths
    json_folder = 'output/clean'
    image_folder = 'output/images'
    template = 'Template 2 colors.png'

    # Load product data and images for the first two products
    json_files = glob.glob(f'{json_folder}/*.json')
    product_data_1, image_files_1 = load_product_data_and_images(json_files[0], image_folder)
    product_data_2, image_files_2 = load_product_data_and_images(json_files[1], image_folder)

    # Create the PDF with both products
    create_pdf_with_two_products(product_data_1, image_files_1, product_data_2, image_files_2, template)

if __name__ == "__main__":
    main()
