
import os
import glob
import json
from PIL import Image, ImageDraw, ImageFont
import pillow_avif  # Import for AVIF image support
from textwrap import wrap
from fpdf import FPDF

left_margin = 30

# Function to draw text on the image
def draw_text(drawer, text, position, font, fill):
    drawer.text(position, text, font=font, fill=fill)

def load_product_data_and_images(json_file, image_folder):
    # Load the JSON data
    with open(json_file, 'r') as f:
        product_data = json.load(f)
    
    # Extract the SKU to find the associated images
    sku = product_data['sku']
    images_path = os.path.join(image_folder, str(sku))
    
    # Get all image files for this SKU, handling .jpg and .avif formats
    image_files = sorted(glob.glob(os.path.join(images_path, "*.jpg")) + glob.glob(os.path.join(images_path, "*.avif")))
    
    return product_data, image_files

# Function to draw product features
def draw_features(drawer, features, x_position, y_position, font, max_features_per_column, x_offset):
    for idx, feature in enumerate(features):
        feature_name = feature.get('name', '')
        feature_value = feature.get('value', '')
        feature_text = f"{feature_name}: {feature_value}"
        
        if idx == max_features_per_column:
            x_position += 300  # Move to the second column
            y_position = 430   # Reset y position for the second column

        draw_text(drawer, feature_text, (x_position, y_position), font, (51, 51, 51))
        y_position += 20

# Function to draw product images on the image
def draw_product_images(img, image_files, y_offset, x_offset, is_vertical=False):
    if is_vertical:
        for idx, image_file in enumerate(image_files[:4]):
            product_image = Image.open(image_file).resize((110, 110), Image.Resampling.LANCZOS)
            img_x_offset = left_margin + (idx * 160) + x_offset
            img.paste(product_image, (img_x_offset, y_offset))
    else:
        for idx, image_file in enumerate(image_files[:4]):
            product_image = Image.open(image_file).resize((110, 110), Image.Resampling.LANCZOS)
            img_x_offset = left_margin + (idx * 160) + x_offset
            img.paste(product_image, (img_x_offset, y_offset))
    
