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

#load .env file
from dotenv import load_dotenv
load_dotenv()

from retry import retry

@retry(3)
def scrape(input_info):
    main_folder = os.getenv('OUTPUT_FOLDER')
    """Function to scrape the given URL and process data."""
    url = input_info[0]
    cleaned_url = url.replace('https://www.coppel.com', '').replace('/', '_').replace('?', '_').replace('=', '_').replace('&', '_').replace('%', '_').replace(':', '_')

    try:
        print(f"Scraping {url}", flush=True)
        response = requests.get(url=url, headers=headersX, proxies=get_proxy_new(), timeout=30)
        response.raise_for_status()
        print(f"Successfully retrieved content from {url}", flush=True)
    except requests.exceptions.RequestException as e:
        print(f"Error scraping {url}: {e}", flush=True)
        return None

    try:
        with open(f'{main_folder}/html/{cleaned_url}.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"HTML content saved to {main_folder}/html/{cleaned_url}.html", flush=True)
    except IOError as e:
        print(f"Error saving HTML content: {e}", flush=True)

    try:
        print(f"Parsing {url}", flush=True)
        soup = BeautifulSoup(response.text, 'lxml')
        json_data = json.loads(soup.find('script', {"id": "__NEXT_DATA__"}).text)
        print(f"Successfully parsed JSON data from {url}", flush=True)
    except (AttributeError, json.JSONDecodeError) as e:
        print(f"Error parsing JSON data from {url}: {e}", flush=True)
        return None

    filenameraw = f'{main_folder}/raw/{input_info[1]}_{cleaned_url}.json'
    try:
        with open(filenameraw, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)
        print(f"Raw JSON data saved to {filenameraw}", flush=True)
    except IOError as e:
        print(f"Error saving raw JSON data to {filenameraw}: {e}", flush=True)

    try:
        sku = json_data['props']['pageProps']['product']['sku']
        name = json_data['props']['pageProps']['product']['name']
        marca = json_data['props']['pageProps']['product']['brand']
        characteristics = json_data['props']['pageProps']['product']['characteristics']

        taxonomy = get_category(sku)
        if input_info[1]:
            category = input_info[1]
            sub_cat = taxonomy[0]
        else:
            category = taxonomy[0]
            sub_cat = taxonomy[1]
        description = clean_html(json_data['props']['pageProps']['product'].get('longDescription') or json_data['props']['pageProps']['product'].get('shortDescription'))
        image_links = json_data['props']['pageProps']['product']['media']
        descr_list_, modelo = procces_characteristics(characteristics)

        feature_to_create_pdf = {
            "name": name,
            "image_links": image_links,
            "description": description,
            "descr_list": descr_list_,
            "sub_cat": sub_cat.upper() if sub_cat else "OTROS",
            "marca": marca,
            "modelo": modelo,
            "sku": sku,
            "category": category,
            "pos": url
        }

        filenameclean = f'{main_folder}/clean/{input_info[1]}_{cleaned_url}.json'
        print(f"Saving cleaned data to {filenameclean}", flush=True)
        with open(filenameclean, 'w', encoding='utf-8') as f:
            json.dump(feature_to_create_pdf, f, indent=4, ensure_ascii=False)
        print(f"Cleaned data saved to {filenameclean}", flush=True)

    except KeyError as e:
        print(f"PARSING ALERT: {e} - at {url}")
        return None

    print(f"Scraping images for {sku}", flush=True)
    Imageslocations = get_images_from_image_list_concurrently(image_links[:4], sku)
    print(f"Images scraped and saved: {Imageslocations}", flush=True)

    sh = get_sheet()
    i = input_info[3]
    values_to_update = [
        feature_to_create_pdf['name'],
        feature_to_create_pdf['description'],
        feature_to_create_pdf['marca'],
        feature_to_create_pdf['sku'],
        feature_to_create_pdf['pos'],
        feature_to_create_pdf['category'],
        str(feature_to_create_pdf['image_links'])
    ]

    # Update the entire row at once
    sh[3].update_row(i+2, values_to_update)
    print(f"Google Sheet updated for {sku}", flush=True)

    return feature_to_create_pdf

def safe_scrape(input_info):
    try:
        return scrape(input_info)
    except Exception as e:
        print(f"Error scraping {input_info[0]}: {e}")

        sh = get_sheet()
        i = input_info[3]
        values_to_update = [
        "error",
        "error",
        "error",
        "error",
        input_info[0],
        "error",
        "error",
        ]
        sh = get_sheet()
        # Update the entire row at once
        sh[3].update_row(i+2, values_to_update)
        return None

def collector():
    create_output_folders()
    # Setup folders
    setup_folders()

    # Get the Google Sheet Data
    sh = get_sheet()

    #delete content below headers
    sh[3].clear(start='A2', end='G1000')

    input_info_block = read_inputs(sh)
    #add index to input_info_block
    for i, item in enumerate(input_info_block):
        item.append(i)

    # Use multiprocessing to scrape data
    with ProcessPoolExecutor(max_workers=5) as executor:
        results = executor.map(safe_scrape, input_info_block)

    resolved_results = list(results)
    return resolved_results


if __name__ == '__main__':
    collector()
