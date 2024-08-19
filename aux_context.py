import os
import json
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import pygsheets
import shutil


# Load environment variables
from dotenv import load_dotenv
load_dotenv()


def get_credentials():

    #also upload to bucket
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/cloud-platform']
    
    SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
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
        