

import os
import requests
from concurrent.futures import ThreadPoolExecutor

from aux_scraper import get_proxy_new, headersX


def get_images_from_image_list(image_url, sku):
    main_folder = os.getenv('OUTPUT_FOLDER')
    image_name = image_url.split('/')[-1]
    try:
        response = requests.get(url=image_url, headers=headersX, proxies=get_proxy_new(),timeout=int(os.getenv('IMAGESTIMEOUT')))
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return None
    
    # Create folder to save images
    os.makedirs(f'{main_folder}/images/{sku}', exist_ok=True)

    filename_image = f'{main_folder}/images/{sku}/{image_name}'
    
    # Save the image
    with open(filename_image, 'wb') as f:
        f.write(response.content)
    
    return filename_image

def get_images_from_image_list_concurrently(image_list, sku):
    with ThreadPoolExecutor(max_workers=10) as executor:  # Limit to 10 threads
        locations = executor.map(lambda url: get_images_from_image_list(url, sku), image_list)
        locations_list = list(locations)
    
    return locations_list

# Call the function
