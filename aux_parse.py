import re
from bs4 import BeautifulSoup
from html import unescape
import pandas as pd



def clean_html(raw_html):
    """
    Clean all HTML from a product description and return a plain text string.

    :param raw_html: The HTML string to clean.
    :return: A plain text string with HTML tags removed, special characters cleaned, and <br> tags replaced by newline characters.
    """
    
    # Parse HTML and replace <br> tags with newline characters
    soup = BeautifulSoup(raw_html, "lxml")
    for br in soup.find_all("br"):
        br.replace_with("\n")

    cleantext = soup.get_text(separator=' ', strip=True)

    # Decode HTML entities
    cleantext = unescape(cleantext)

    # Remove all special characters except commas, periods, and whitespace
    cleantext = re.sub(r'[^\w\s,.\n]', '', cleantext)

    # Normalize whitespace (remove extra spaces and tabs, but keep newlines)
    cleantext = re.sub(r'[ \t]+', ' ', cleantext).strip()

    return cleantext

def procces_characteristics(characteristics):

        # Normalize the JSON data into a DataFrame
    df_characteristics = pd.json_normalize(characteristics)

    # Explode the 'values' column so that each dictionary in the list gets its own row
    df_characteristics_exploded = df_characteristics.explode('values')

    # Expand the 'values' dictionaries into separate columns
    charcteristic_values_df = pd.json_normalize(df_characteristics_exploded['values'])

    # Extract the 'value' column from the expanded DataFrame
    charcteristic_values = charcteristic_values_df['value']

    # Get the 'name' column from the original DataFrame (before exploding)
    charcteristic_keys = df_characteristics_exploded['name']

    # Reset the index of both Series to match the length of the other
    charcteristic_keys = charcteristic_keys.reset_index(drop=True)
    charcteristic_values = charcteristic_values.reset_index(drop=True)
    
    # Concatenate 'name' and 'value' into a single DataFrame and convert to list of dictionaries
    descr_list_ = pd.concat([charcteristic_keys, charcteristic_values], axis=1).to_dict('records')

    modelo = (df_characteristics['values'][df_characteristics['name'].str.contains('Modelo #')].values).tolist()[0][0]['value'] if len(df_characteristics['values'][df_characteristics['name'].str.contains('Modelo #')].values)>0 else ''

    return descr_list_, modelo


