from PIL import Image
import pillow_avif

filepath = 'output/images/4326653/4326653-1.jpg'

try:
    with open(filepath, 'rb') as file:
        img = Image.open(file)
        img.load()  # Ensure image is fully loaded

        # Resize the image
        resized_img = img.resize((110, 110), Image.Resampling.LANCZOS)

        # Save the resized image
        resized_img.save('resized_image.jpg', format='JPEG')

    print("Image resized and saved successfully!")
except Exception as e:
    print(f"An error occurred: {e}")
