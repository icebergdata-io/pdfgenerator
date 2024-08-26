import os
import glob
import json
from PIL import Image, ImageDraw, ImageFont
import pillow_avif  # Import for AVIF image support
from textwrap import wrap
from fpdf import FPDF
from aux_pdf import draw_text, draw_features, draw_product_images,left_margin


# Function to render a single product on the template
def render_page_single(combined_img, product_data, image_files, x_offset_input):
    drawer = ImageDraw.Draw(combined_img)

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

    # Define fonts for rendering text
    font_bold = ImageFont.truetype('Calibri Bold.ttf', 27)
    font_bold_small = ImageFont.truetype('Calibri Bold.ttf', 20)
    font_bold_medium = ImageFont.truetype('Calibri Bold.ttf', 23)
    font_regular = ImageFont.truetype('Calibri Regular.ttf', 18)
    font_bold_large = ImageFont.truetype('Calibri Bold.ttf', 36)

    # New: Define smaller font for long descriptions
    font_regular_small = ImageFont.truetype('Calibri Regular.ttf', 14)

    x_offset = x_offset_input

    # Draw product information on the image
    draw_text(drawer, f'{category}', (left_margin + x_offset, 120), font_bold_large, (33, 90, 168))
    draw_text(drawer, f'{subcategory}', (left_margin + x_offset, 172), font_bold_medium, (33, 90, 168))
    draw_text(drawer, sku, (420 + x_offset, 172), font_bold_small, (33, 90, 168))
    draw_text(drawer, brand_model, (left_margin + x_offset, 200), font_bold_small, (100, 100, 100))
    draw_text(drawer, product_name, (left_margin + x_offset, 220), font_bold_medium, (100, 100, 100))

    # Paste product images on the template
    draw_product_images(combined_img, image_files, 270, x_offset)

    # Draw features
    draw_text(drawer, 'Características del producto', (left_margin + x_offset, 400), font_bold_medium, (104, 166, 225))
    draw_features(drawer, product_data['descr_list'][:10], left_margin + x_offset, 430, font_regular, 5, x_offset)

    # New: Handle description with dynamic font size
    draw_text(drawer, 'Descripción de producto', (left_margin + x_offset, 550), font_bold_medium, (104, 166, 225))
    
    # Wrap description text and choose font size
    description_lines = wrap(product_description, 75)
    if len(description_lines) > 5:
        description_font = font_regular_small
        max_lines = 5  # Allow more lines with smaller font
    else:
        description_font = font_regular
        max_lines = 3

    # Truncate description if it's too long
    if len(description_lines) > max_lines:
        description_lines = description_lines[:max_lines]
        description_lines[-1] += '...'

    description_text = '\n'.join(description_lines)
    draw_text(drawer, description_text, (left_margin + x_offset, 580), description_font, (51, 51, 51))

    return combined_img

def render_page_vertical(combined_img, product_data_1, image_files_1, product_data_2=None, image_files_2=None):
    drawer = ImageDraw.Draw(combined_img)

    # Render the first product on the top half
    render_product_vertical(drawer, combined_img, product_data_1, image_files_1, y_offset=0)

    # If a second product exists, render it on the bottom half
    if product_data_2:
        render_product_vertical(drawer, combined_img, product_data_2, image_files_2, y_offset=640)

    return combined_img

def render_product_vertical(drawer, combined_img, product_data, image_files, y_offset):
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
    product_name = wrap(product_name, 40)[0]  # Adjust wrap width for vertical layout

    # Define fonts for rendering text
    font_bold = ImageFont.truetype('Calibri Bold.ttf', 22)
    font_bold_small = ImageFont.truetype('Calibri Bold.ttf', 16)
    font_bold_medium = ImageFont.truetype('Calibri Bold.ttf', 18)
    font_regular = ImageFont.truetype('Calibri Regular.ttf', 14)
    font_bold_large = ImageFont.truetype('Calibri Bold.ttf', 26)
    font_regular_small = ImageFont.truetype('Calibri Regular.ttf', 12)

    # Draw product information on the image
    draw_text(drawer, f'{category}', (left_margin, 20 + y_offset), font_bold_large, (33, 90, 168))
    draw_text(drawer, f'{subcategory}', (left_margin, 50 + y_offset), font_bold_medium, (33, 90, 168))
    draw_text(drawer, sku, (left_margin, 75 + y_offset), font_bold_small, (33, 90, 168))
    draw_text(drawer, brand_model, (left_margin, 100 + y_offset), font_bold_small, (100, 100, 100))
    draw_text(drawer, product_name, (left_margin, 125 + y_offset), font_bold_medium, (100, 100, 100))

    # Paste product images on the template
    draw_product_images_vertical(combined_img, image_files, 160 + y_offset, left_margin)

    # Draw features
    draw_text(drawer, 'Características del producto', (left_margin, 400 + y_offset), font_bold_medium, (104, 166, 225))
    draw_features(drawer, product_data['descr_list'][:4], left_margin, 425 + y_offset, font_regular, 3, 0)

    # Handle description with dynamic font size
    draw_text(drawer, 'Descripción de producto', (left_margin, 510 + y_offset), font_bold_medium, (104, 166, 225))
    
    # Wrap description text and choose font size
    description_lines = wrap(product_description, 50)  # Adjust wrap width for vertical layout
    if len(description_lines) > 3:
        description_font = font_regular_small
        max_lines = 3
    else:
        description_font = font_regular
        max_lines = 2

    # Truncate description if it's too long
    if len(description_lines) > max_lines:
        description_lines = description_lines[:max_lines]
        description_lines[-1] += '...'

    description_text = '\n'.join(description_lines)
    draw_text(drawer, description_text, (left_margin, 535 + y_offset), description_font, (51, 51, 51))

def draw_product_images_vertical(combined_img, image_files, y_offset, x_offset):
    max_width = 680  # Maximum width for the images
    max_height = 220  # Maximum height for the images
    spacing = 10  # Spacing between images

    for i, img_path in enumerate(image_files[:4]):  # Limit to 4 images
        with Image.open(img_path) as img:
            img.thumbnail((max_width // 2 - spacing, max_height))
            x = x_offset + (i % 2) * (max_width // 2 + spacing)
            y = y_offset + (i // 2) * (max_height // 2 + spacing)
            combined_img.paste(img, (x, y))

def render_page(product_data_1, image_files_1, product_data_2=None, image_files_2=None, template_image=None, layout='horizontal'):
    sku_name = product_data_1['sku'] + "_" + product_data_1['name']
    print(f"Rendering page for product {sku_name}")
    
    if isinstance(template_image, str):
        if layout == 'horizontal':
            combined_img = Image.open(template_image).resize((1280, 720), Image.Resampling.LANCZOS)
        else:
            combined_img = Image.open(template_image).resize((720, 1280), Image.Resampling.LANCZOS)
    else:
        print("Template image is not a string")
        if layout == 'horizontal':
            combined_img = template_image.resize((1280, 720), Image.Resampling.LANCZOS)
        else:
            combined_img = template_image.resize((720, 1280), Image.Resampling.LANCZOS)

    if layout == 'vertical':
        return render_page_vertical(combined_img, product_data_1, image_files_1, product_data_2, image_files_2)
    else:
        # Existing horizontal layout logic
        combined_img = render_page_single(combined_img, product_data_1, image_files_1, x_offset_input=0)
        if product_data_2:
            sku_name2 = product_data_2['sku'] + "_" + product_data_2['name']
            print(f"Rendering page for product {sku_name2}")
            combined_img = render_page_single(combined_img, product_data_2, image_files_2, x_offset_input=640)

    return combined_img