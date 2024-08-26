
from aux_context import get_sheet
import os 

def read_inputs(sh):
    try:
        file_name = sh[1].get_named_range('_pdf_name').cells[0][0].value
        user = sh[1].get_named_range('_email').cells[0][0].value
        url_values = sh[1].get_named_range('_input_urls').cells

        if not file_name or not user:
            raise ValueError("File name or user email is missing")

        # Sanitize file_name and user
        file_name = ''.join(e for e in file_name if e.isalnum() or e in ['_', '-'])
        user = ''.join(e for e in user if e.isalnum() or e in ['_', '-', '@', '.'])

        # Set environmental variables
        os.environ['FILENAMETOSAVE'] = file_name
        os.environ['USER'] = user

        # Filter and process URL values
        input_info_block = []
        for row in url_values:
            if row[0].value and 'coppel.com' in row[0].value:
                url = row[0].value.strip()
                category = row[1].value.strip() if row[1].value else ''
                subcategory = row[2].value.strip() if row[2].value else ''
                input_info_block.append([url, category, subcategory])

        print(f'file_name: {file_name}')
        print(f'user: {user}')
        print(f'url_list: {len(input_info_block)}')

        sh[1].update_value('E10', "Reading Inputs")

        if not input_info_block:
            print("Warning: No valid URLs found")

        return input_info_block

    except Exception as e:
        print(f"Error reading inputs: {str(e)}")
        sh[1].update_value('E10', "Error Reading Inputs")
        return []