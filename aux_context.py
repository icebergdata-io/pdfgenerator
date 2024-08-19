import pygsheets
from google.auth import default
import os
import shutil


credentials, project = default()
credentials = credentials.with_scopes(['https://www.googleapis.com/auth/spreadsheets'])
gc = pygsheets.authorize(custom_credentials=credentials)
gheet_id = os.getenv('GSHEET_ID')
sh = gc.open_by_key(gheet_id)

def get_sheet():
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
        