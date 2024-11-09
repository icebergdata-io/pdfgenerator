import os
import json
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ProcessPoolExecutor
from aux_context import get_sheet, setup_folders
from aux_input import read_inputs
from scraper_category import get_category
from scraper_images import get_images_from_image_list_concurrently
from aux_scraper import headersX, get_proxy_new
from aux_parse import clean_html, procces_characteristics
from utils import create_output_folders
from dotenv import load_dotenv
from retry import retry
from typing import Optional, Dict, Any, List

load_dotenv()

def extract_product_data(json_data: Dict, original_index: int) -> Dict[str, Any]:
    """Extract relevant product data from JSON response, including original order index."""
    product = json_data['props']['pageProps']['product']
    
    # Extract basic product information
    sku = product['sku']
    name = product['name']
    marca = product['brand']
    characteristics = product['characteristics']
    
    # Get product description
    description = clean_html(
        product.get('longDescription') or 
        product.get('shortDescription', '')
    )
    
    # Process characteristics and get model
    descr_list, modelo = procces_characteristics(characteristics)
    
    # Get image links
    image_links = product['media']
    
    return {
        "sku": sku,
        "name": name,
        "marca": marca,
        "description": description,
        "image_links": image_links,
        "descr_list": descr_list,
        "modelo": modelo,
        "original_index": original_index  # Add original index to preserve order
    }

@retry(tries=3)
def scrape(input_info: tuple) -> Optional[Dict]:
    """
    Scrape product information from a given URL.
    
    Args:
        input_info: Tuple containing (url, category, subcategory, index)
    
    Returns:
        Dictionary containing product information or None if scraping fails
    """
    url, category, subcategory, index = input_info
    main_folder = os.getenv('OUTPUT_FOLDER')
    cleaned_url = url.replace('https://www.coppel.com', '').replace('/', '_').strip('_')
    
    response = requests.get(
        url=url,
        headers=headersX,
        proxies=get_proxy_new(),
        timeout=30
    )
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'lxml')
    json_data = json.loads(soup.find('script', {"id": "__NEXT_DATA__"}).text)
    
    # Extract product data with original index
    product_data = extract_product_data(json_data, index)
    sku = str(product_data['sku'])
    
    taxonomy = get_category(sku) or ["ERROR", "OTROS"]
    
    if category:
        final_category = category
        final_subcategory = taxonomy[0]
    else:
        final_category = taxonomy[0]
        final_subcategory = taxonomy[1]
    
    feature_to_create_pdf = {
        **product_data,
        "sub_cat": final_subcategory.upper() if final_subcategory else "OTROS",
        "category": final_category,
        "pos": url
    }
    
    # Save the data with index in filename
    clean_json_path = f'{main_folder}/clean/{index:03d}_{category}_{cleaned_url}.json'
    with open(clean_json_path, 'w', encoding='utf-8') as f:
        json.dump(feature_to_create_pdf, f, indent=4, ensure_ascii=False)
    
    # Download images
    image_locations = get_images_from_image_list_concurrently(
        product_data['image_links'][:4], 
        sku
    )
    
    # Update Google Sheet
    sh = get_sheet()
    sheet_values = [
        feature_to_create_pdf['name'],
        feature_to_create_pdf['description'],
        feature_to_create_pdf['marca'],
        feature_to_create_pdf['sku'],
        feature_to_create_pdf['pos'],
        feature_to_create_pdf['category'],
        str(feature_to_create_pdf['image_links'])
    ]
    sh[3].update_row(index + 2, sheet_values)
    
    return feature_to_create_pdf

def safe_scrape(input_info: tuple) -> Optional[Dict]:
    """
    Wrapper function to handle scraping errors safely.
    
    Args:
        input_info: Tuple containing (url, category, subcategory, index)
    
    Returns:
        Dictionary containing product information or None if scraping fails
    """
    try:
        return scrape(input_info)
    except Exception as e:
        print(f"Error scraping {input_info[0]}: {e}")
        sh = get_sheet()
        error_values = ["error"] * 6 + [input_info[0]]
        update_sheet_row(sh, input_info[3], error_values)
        return None

def update_sheet_row(sh, index: int, values: list) -> None:
    """Update a row in the Google Sheet."""
    sh[3].update_row(index + 2, values)

def collector() -> List[Dict]:
    """Main function to coordinate the scraping process."""
    create_output_folders()
    setup_folders()
    
    sh = get_sheet()
    sh[3].clear(start='A2', end='G1000')
    
    input_info_block = [(*item, i) for i, item in enumerate(read_inputs(sh))]
    
    with ProcessPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(safe_scrape, input_info_block))
    
    # Filter out None values and sort by original_index
    valid_results = [r for r in results if r is not None]
    sorted_results = sorted(valid_results, key=lambda x: x['original_index'])
    
    return sorted_results

if __name__ == '__main__':
    collector()