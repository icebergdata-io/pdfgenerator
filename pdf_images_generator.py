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
    draw_features(drawer, product_data.get('descr_list', [])[:8], left_margin + x_offset, 430, font_regular, 20, x_offset)

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
    if product_data_2 and image_files_2:
        render_product_vertical(drawer, combined_img, product_data_2, image_files_2, y_offset=300)

    return combined_img

def render_product_vertical(drawer, combined_img, product_data, image_files, y_offset):
    # Constants
    left_margin = 20
    top_margin = 100
    image_width = 350
    right_column_start = left_margin + image_width + 20
    
    # Extracting data from product JSON
    product_name = product_data.get('name', 'No Name')
    product_description = product_data.get('description', 'No Description')
    subcategory = product_data.get('sub_cat', 'No Subcategory')
    model = product_data.get('modelo', 'No Model')
    brand = product_data.get('marca', 'No Brand').title()
    sku = str(product_data.get("sku", "No SKU"))
    category = str(product_data.get('category', 'No Category'))

    # Prepare text and descriptions for rendering
    brand_model = f'Marca: {brand} | Modelo: {model}'
    category_subcategory = f'{category} - {subcategory}'

    # Define fonts for rendering text
    font_bold_large = ImageFont.truetype('Calibri Bold.ttf', 24)
    font_bold_medium = ImageFont.truetype('Calibri Bold.ttf', 20)
    font_bold_small = ImageFont.truetype('Calibri Bold.ttf', 16)
    font_regular = ImageFont.truetype('Calibri Regular.ttf', 14)

    # Define colors
    color_blue = (0, 114, 188)  # RGB for blue
    color_gray = (100, 100, 100)  # RGB for gray
    color_light_gray = (230, 230, 230)  # RGB for light gray (SKU background)

    current_y = y_offset + top_margin

    # Draw category and subcategory
    drawer.text((left_margin, current_y), category_subcategory, font=font_bold_large, fill=color_blue)
    current_y += 30

    # Draw brand and model
    drawer.text((left_margin, current_y), brand_model, font=font_bold_medium, fill=color_gray)
    current_y += 30

    # Draw product images
    draw_product_images_vertical(combined_img, image_files, current_y, left_margin)

    # Draw product name
    drawer.text((right_column_start, current_y), product_name, font=font_bold_medium, fill=color_blue)
    current_y += 30

    # Draw product description
    description_lines = wrap(product_description, 70)
    description_text = '\n'.join(description_lines[:6])  # Limit to 3 lines
    drawer.text((right_column_start, current_y), description_text, font=font_regular, fill=color_gray)
    current_y -= 30
    
    # Draw specifications
    spec_y = current_y
    for feature in product_data.get('descr_list', [])[:8]:  # Limit to 8 features
        feature_text = f"- {feature.get('name', '')}: {feature.get('value', '')}"
        wrapped_lines = wrap(feature_text, width=60) 
        for line in wrapped_lines:
            drawer.text((right_column_start + 485, spec_y), line, font=font_regular, fill=color_gray)
            spec_y += 20 
            
    # Draw SKU above the gray block
    sku_y = y_offset + 333  # Adjust this value as needed
    if y_offset > 0:
        sku_y += 15
    sku_x = right_column_start + 500
    drawer.text((sku_x, sku_y), f"SKU: {sku}", font=font_bold_small, fill=color_gray)

    # Draw gray block (now empty)
    # block_y = sku_y + 25
    # drawer.rectangle([(right_column_start, block_y), (right_column_start + 120, block_y + 30)], 
    #                  fill=color_light_gray, outline=color_light_gray)

def draw_product_images_vertical(combined_img, image_files, y_offset, x_offset):
    max_width = 240  # Maximum width for the 2x2 grid
    max_height = 240  # Maximum height for the 2x2 grid
    individual_size = (max_width // 2 - 5, max_height // 2 - 5)  # Size for each image

    for i, img_path in enumerate(image_files[:4]):  # Limit to 4 images
        try:
            with Image.open(img_path) as img:
                img.thumbnail(individual_size)
                x = x_offset + (i % 2) * (max_width // 2 + 5)
                y = y_offset + (i // 2) * (max_height // 2 + 5)
                combined_img.paste(img, (x, y))
        except Exception as e:
            print(f"Error processing image {img_path}: {str(e)}")


def render_page(product_data_1, image_files_1, product_data_2=None, image_files_2=None, template_image=None, layout='horizontal'):
    sku_name = product_data_1['sku'] + "_" + product_data_1['name']
    print(f"Rendering page for product {sku_name}")
    
    if isinstance(template_image, str):
        combined_img = Image.open(template_image).resize((1280, 720), Image.Resampling.LANCZOS)
    else:
        print("Template image is not a string")
        combined_img = template_image.resize((1280, 720), Image.Resampling.LANCZOS)
        
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