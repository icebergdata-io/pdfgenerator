
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
def draw_features(drawer, features, x_position, y_position, font, line_height, x_offset):
    max_lines_per_column = 6  # Define el máximo de líneas por columna
    max_columns = 2  # Limitar a 2 columnas
    lines_in_current_column = 0  # Cuenta las líneas en la columna actual
    current_column = 1  # Inicia en la primera columna

    for feature in features:
        feature_name = feature.get('name', '')
        feature_value = feature.get('value', '')
        feature_text = f"- {feature_name}: {feature_value}"
        
        # Wrap text to fit within a certain width
        wrapped_lines = wrap(feature_text, width=30)
        
        # If the number of lines exceeds the max per column and there is room for a new column
        if lines_in_current_column + len(wrapped_lines) > max_lines_per_column:
            if current_column < max_columns:  # Move to the next column if there is room
                x_position += 300  # Move to the next column
                y_position = 430   # Reset y position for the new column
                lines_in_current_column = 0  # Reset line count for the new column
                current_column += 1
            else:
                break  # Stop if max columns are reached

        # Draw each line of wrapped text
        for line in wrapped_lines:
            draw_text(drawer, line, (x_position, y_position), font, (51, 51, 51))
            y_position += line_height  # Move down for the next line
            lines_in_current_column += 1  # Increment the line count
        
        # Add extra space between features
        if len(wrapped_lines) > 1:
            y_position += 10  # Additional space after wrapped lines
            lines_in_current_column += 1  # Count the extra space as a line

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
    
