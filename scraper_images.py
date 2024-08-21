import os
import requests
from concurrent.futures import ThreadPoolExecutor
from aux_scraper import get_proxy_new, headersX
from retry import retry
#load .env file
from dotenv import load_dotenv
load_dotenv()

@retry(tries=2, delay=1)
def request_image(url, timeout):
    return requests.get(url=url, headers=headersX, proxies=get_proxy_new(), timeout=timeout)


def get_images_from_image_list(image_url, sku):
    main_folder = os.getenv('OUTPUT_FOLDER')
    image_name = os.path.basename(image_url)
    timeout = int(os.getenv('IMAGESTIMEOUT', 10))  # Default timeout if not set

    try:
        response = request_image(image_url, timeout)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {image_url}: {e}")
        return None
    
    # Create folder to save images
    image_folder = os.path.join(main_folder, 'images', sku)
    os.makedirs(image_folder, exist_ok=True)

    filename_image = os.path.join(image_folder, image_name)
    
    # Save the image
    try:
        with open(filename_image, 'wb') as file:
            file.write(response.content)
    except IOError as e:
        print(f"Failed to save {filename_image}: {e}")
        return None
    
    return filename_image

#create get_images_from_image_list and return empty white image in case 
def safe_get_images_from_image_list(image_url, sku):
    try:
        return get_images_from_image_list(image_url, sku)
    except Exception as e:
        print(f"Error scraping {image_url}: {e}")
        #create blank image in case of error
        main_folder = os.getenv('OUTPUT_FOLDER')
        image_folder = os.path.join(main_folder, 'images', sku)
        os.makedirs(image_folder, exist_ok=True)
        filename_image = os.path.join(image_folder, 'blank.jpg')
        with open(filename_image, 'wb') as file:
            file.write(b'')
        return filename_image


def get_images_from_image_list_concurrently(image_list, sku):
    with ThreadPoolExecutor(max_workers=4) as executor:
        locations = executor.map(lambda url: get_images_from_image_list(url, sku), image_list)
        locations_list = list(filter(None, locations))  # Filter out None values
    
    return locations_list


# Example call to the function
# locations = get_images_from_image_list_concurrently(image_urls, sku)
