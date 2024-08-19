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

#load .env file
from dotenv import load_dotenv
load_dotenv()


def scrape(input_info):
    main_folder = os.getenv('OUTPUT_FOLDER')
    """Function to scrape the given URL and process data."""
    url = input_info[0]
    cleaned_url = url.replace('https://www.coppel.com', '').replace('/', '_').replace('?', '_').replace('=', '_').replace('&', '_').replace('%', '_').replace(':', '_')

    try:
        print(f"Scraping {url}", flush=True)
        response = requests.get(url=url, headers=headersX, proxies=get_proxy_new(), timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return None

    with open(f'{main_folder}/html/{cleaned_url}.html', 'w') as f:
        f.write(response.text)

    try:
        print(f"Parsing {url}", flush=True)
        soup = BeautifulSoup(response.text, 'lxml')
        json_data = json.loads(soup.find('script', {"id": "__NEXT_DATA__"}).text)
    except (AttributeError, json.JSONDecodeError):
        return None

    filenameraw = f'{main_folder}/raw/{input_info[1]}_{cleaned_url}.json'
    with open(filenameraw, 'w') as f:
        json.dump(json_data, f, indent=4)
        

    sku = json_data['props']['pageProps']['product']['sku']
    name = json_data['props']['pageProps']['product']['name']
    marca = json_data['props']['pageProps']['product']['brand']
    characteristics = json_data['props']['pageProps']['product']['characteristics']

    taxonomy = get_category(sku)
    category = input_info[1] if input_info[1] else taxonomy[0]
    sub_cat = taxonomy[1] if taxonomy[1] else ''
    description = clean_html(json_data['props']['pageProps']['product'].get('longDescription') or json_data['props']['pageProps']['product'].get('shortDescription'))
    image_links = json_data['props']['pageProps']['product']['media']
    descr_list_, modelo = procces_characteristics(characteristics)

    feature_to_create_pdf = {
        "name": name,
        "image_links": image_links,
        "description": description,
        "descr_list": descr_list_,
        "sub_cat": sub_cat.upper(),
        "marca": marca,
        "modelo": modelo,
        "sku": sku,
        "category": category,
        "pos": url
    }

    filenameclean = f'{main_folder}/clean/{input_info[1]}_{cleaned_url}.json'
    print(f"Data saved to {filenameclean}", flush=True)
    with open(filenameclean, 'w', encoding='utf-8') as f:
        json.dump(feature_to_create_pdf, f, indent=4, ensure_ascii=False)
    
    print(f"Scraping images for {sku}", flush=True)
    Imageslocations = get_images_from_image_list_concurrently(image_links[:4], sku)
    sh = get_sheet()
    i = input_info[3]
    sh[3].update_value(f'A{i+2}', feature_to_create_pdf['name'])
    sh[3].update_value(f'B{i+2}', feature_to_create_pdf['description'])
    sh[3].update_value(f'C{i+2}', feature_to_create_pdf['marca'])
    sh[3].update_value(f'D{i+2}', feature_to_create_pdf['sku'])
    sh[3].update_value(f'E{i+2}', feature_to_create_pdf['pos'])
    sh[3].update_value(f'F{i+2}', feature_to_create_pdf['category'])
    sh[3].update_value(f'G{i+2}', str(feature_to_create_pdf['image_links']))
    return feature_to_create_pdf


def collector():
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
    with ProcessPoolExecutor() as executor:
        results = executor.map(scrape, input_info_block)

    resolved_results = list(results)
    return resolved_results


if __name__ == '__main__':
    collector()
