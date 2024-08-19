import os
import json
import tempfile
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import pygsheets
import shutil


def get_credentials():
    creds_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    if not creds_json:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS_JSON environment variable is not set")
    
    creds_dict = json.loads(creds_json)
    
    # Create a temporary file to store the credentials
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        json.dump(creds_dict, temp_file)
        temp_file_path = temp_file.name
    
    # Use the temporary file to create credentials
    creds = service_account.Credentials.from_service_account_file(
        temp_file_path, 
        scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    )
    
    # Delete the temporary file
    os.unlink(temp_file_path)
    
    return creds

def get_sheet():
    creds = get_credentials()
    client = pygsheets.authorize(custom_credentials=creds)
    sh = client.open_by_key(os.getenv('GSHEET_ID'))
    return sh

def setup_folders():
    # Define main_folder at the top
    main_folder = os.getenv('OUTPUT_FOLDER')

    if os.path.exists(main_folder):
        shutil.rmtree(main_folder)

    """Function to setup folders (create directories)."""
    create_directories([
        f'{main_folder}/html',
        f'{main_folder}/raw',
        f'{main_folder}/clean',
        f'{main_folder}/images',
        f'{main_folder}/search'
    ])

def create_directories(paths):
    """Function to create necessary directories."""
    for path in paths:
        os.makedirs(path, exist_ok=True)
        