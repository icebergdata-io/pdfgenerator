
from aux_gsheet import get_sheet

def read_inputs(sh):
    file_name   = sh[1].get_named_range('_pdf_name').cells[0][0].value
    user        = sh[1].get_named_range('_email').cells[0][0].value
    url_values  = sh[1].get_named_range('_input_urls').cells

    #keep only the urls that contain coppel.com
    url_values = [i for i in url_values if i[0].value.find('coppel.com') != -1]

    input_info_block = [[i[0].value, i[1].value, i[2].value] for i in url_values if i[0].value != '']

    print(f'file_name: {file_name}')
    print(f'user: {user}')
    print(f'url_list: {len(input_info_block)}')

    sh[1].update_value('E10', "Reading Inputs")

    return input_info_block