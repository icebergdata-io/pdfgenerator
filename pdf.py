import img2pdf
from PIL import Image, ImageFont, ImageDraw 
import pandas as pd
import os
import pytz
from datetime import datetime
from textwrap import wrap
import glob

import pillow_avif



def render_page(product_data, image_files, template_image, x_offset_input=630):
    # Extracting data
    product_name = product_data['name']
    product_description = product_data['description']
    subcategory = product_data['sub_cat']
    model = product_data['modelo']
    brand = product_data['marca'].title()
    sku = f'SKU: {str(product_data["sku"])}'
    position = product_data['pos']
    category = str(product_data['category'])
    
    # Setting default category if not available
    if category == 'nan':
        category = 'Category'

    # Prepare text and descriptions for rendering
    brand_model = ''
    if model and brand:
        brand_model = f'Marca: {brand} | ModelO: {model}'
    elif model:
        brand_model = f'Modelo: {model}'
    elif brand:
        brand_model = f'Marca: {brand}'

    # Wrap text to fit in the image
    wrapped_name = wrap(product_name, 100)
    product_name = wrapped_name[0]

    description_text = wrap(product_description, 80)
    description_text = '\n'.join(description_text)

    features_df = pd.DataFrame(product_data['descr_list'])

    # Load the background image template
    try:
        background_image = Image.open(template_image)
    except:
        background_image = template_image

    background_image = background_image.resize((1280, 720), Image.Resampling.LANCZOS)
    img = background_image      

    # Drawing text on the image
    drawer = ImageDraw.Draw(background_image)
    
    # Fonts
    font_bold = ImageFont.truetype('Calibri Bold.ttf', 27) 
    font_bold_small = ImageFont.truetype('Calibri Bold.ttf', 20) 
    font_bold_medium = ImageFont.truetype('Calibri Bold.ttf', 23) 
    font_regular = ImageFont.truetype('Calibri Regular.ttf', 18)
    font_bold_large = ImageFont.truetype('Calibri Bold.ttf', 36)

    # Apply horizontal offset to all elements
    x_offset = x_offset_input

    # Draw category
    drawer.text((30 + x_offset, 120), f'{category}', font=font_bold_large, fill=(33, 90, 168))

    # Draw subcategory
    drawer.text((30 + x_offset, 172), f'{subcategory}', font=font_bold_medium, fill=(33, 90, 168))

    # Draw SKU
    drawer.text((420 + x_offset, 172), sku, font=font_bold_small, fill=(33, 90, 168))

    # Draw brand and model information
    drawer.text((30 + x_offset, 200), brand_model, font=font_bold_small, fill=(100, 100, 100))

    # Draw product name in grey
    drawer.text((30 + x_offset, 220), product_name, font=font_bold_medium, fill=(100, 100, 100))

    # Paste product images onto the template
    y_offset = 270
    for idx, image_file in enumerate(image_files[:4]):
        # Open and resize the product image
        product_image = Image.open(image_file).resize((110, 110), Image.Resampling.LANCZOS)
        
        # Calculate x and y position to paste the image in a row
        img_x_offset = 30 + (idx * 160) + x_offset  # Horizontal spacing of 150 pixels between images

        # Paste the image at the calculated position
        img.paste(product_image, (img_x_offset, y_offset))

    # Label for product features
    LABLE1 = 'Características del producto'
    drawer.text((30 + x_offset, 400), LABLE1, font=font_bold_medium, fill=(104, 166, 225))

    # Render features
    y_position = 430
    x_position = 30 + x_offset  # Initial x position for the first column
    max_features_per_column = 5

    for idx, feature in enumerate(product_data['descr_list']):
        feature_text = f"{feature['name']}: {feature['value']}"
        
        # Check if we've reached the maximum number of features for the first column
        if idx == max_features_per_column:
            # Move to the second column
            x_position = 300 + x_offset  # Adjust the x position for the second column
            y_position = 430  # Reset y position for the second column

        # Draw the feature text
        drawer.text((x_position, y_position), feature_text, font=font_regular, fill=(51, 51, 51))
        y_position += 20

    # Label for product description
    LABLE2 = 'Descripción de producto'
    drawer.text((30 + x_offset, 550), LABLE2, font=font_bold_medium, fill=(104, 166, 225))

    # Draw product description
    drawer.text((30 + x_offset, 580), description_text, font=font_regular, fill=(51, 51, 51))

    # Save the rendered image
    img_name = f"{position}_{datetime.now(pytz.timezone('America/Bogota')).strftime('%Y%m%d%H%M%S')}.png"
    # img.save(f"output/{img_name}")
    img.save(f"output/z.png")

    return img, img_name

def generate_pdfs_from_folders(images_folder, json_folder):
    # Function to loop through folders, render images, and generate PDFs.
    output_folder_name = datetime.now(pytz.timezone('America/Bogota')).strftime('%Y%m%d%H%M%S')
    os.mkdir(f'output')

    for sku_folder in os.listdir(images_folder):
        images_path = os.path.join(images_folder, sku_folder)
        json_path = os.path.join(json_folder, f"{sku_folder}.json")

        if os.path.isdir(images_path) and os.path.exists(json_path):
            with open(json_path, 'r') as f:
                product_data = json.load(f)

            image_files = sorted(glob.glob(os.path.join(images_path, "*.jpg")))

            # Render each page and save images
            rendered_img, img_name = render_page(product_data, image_files, os.path.join(images_folder, "Template.png"))
    
    # Combine images into a single PDF
    image_files = sorted(glob.glob(f'output/*.png'))
    with open(f"{output_folder_name}.pdf", "wb") as f:
        f.write(img2pdf.convert(image_files))

    print(f"PDF generated: {output_folder_name}.pdf")


#load product data from first file in output/clean

import json
#list of json files
json_files = glob.glob('output/clean/*.json')

#load first file
with open(json_files[1], 'r') as f:
    product_data = json.load(f)

#get sku 
sku = product_data['sku']

#load images
images_path = os.path.join(f'output/images/{sku}')

#get all files in this folder
image_files = sorted(glob.glob(os.path.join(images_path, "*.jpg")))

template = 'Template 2 colors.png'

render_page(product_data, image_files, template)

