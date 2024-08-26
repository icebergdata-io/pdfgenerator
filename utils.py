import os

def create_output_folders():
    # Define the folder structure
    folders = [
        'output',
        'output/clean',
        'output/raw',
        'output/html',
        'output/images',
        'output/pages',
        'output/pdfs'
    ]

    # Create each folder if it doesn't exist
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"Created folder: {folder}")

if __name__ == "__main__":
    create_output_folders()