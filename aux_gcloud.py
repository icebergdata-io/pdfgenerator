import os
from google.cloud import storage
from google.auth import default
from dotenv import load_dotenv
from datetime import timedelta
from aux_context import get_credentials

def get_secrets_from_secret_manager(secret_id):
    from google.cloud import secretmanager
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/iceflow/secrets/{secret_id}/versions/latest"
    return client.access_secret_version(name=name).payload.data.decode('UTF-8')

def load_dotenv_full():
    envfile = get_secrets_from_secret_manager('pdfgeneratordotenv')
    with open('.env', 'w') as f: f.write(envfile)

    serviceaccountfile = get_secrets_from_secret_manager('serviceaccountcoppeljson')
    with open('serviceaccountcoppel.json', 'w') as f: f.write(serviceaccountfile)

    load_dotenv()

def pdf_to_gcloud_bucket(pdf_file):
    storage_client = storage.Client(credentials=get_credentials())
    bucket = storage_client.bucket('pdfgeneratorcoppel')
    bucket.blob(os.path.basename(pdf_file)).upload_from_filename(pdf_file)
    print(f"PDF uploaded to Google Cloud Storage: {pdf_file}")

def generate_signed_url(bucket_name, blob_name, expiration_time):
    storage_client = storage.Client()
    return storage_client.bucket(bucket_name).blob(blob_name).generate_signed_url(
        expiration=timedelta(hours=expiration_time), method='GET'
    )
