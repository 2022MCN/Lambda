import json
import os

class ServiceAccountKey:
    service_account_key = {
        "type": os.environ['sombra_GCP_storage_type'],
        "project_id": os.environ['sombra_GCP_storage_project_id'],
        "private_key_id": os.environ['sombra_GCP_storage_private_key_id'],
        "private_key": os.environ['sombra_GCP_storage_private_key'],
        "client_email": os.environ['sombra_GCP_storage_client_email'],
        "client_id": os.environ['sombra_GCP_storage_client_id'],
        "auth_uri": os.environ['sombra_GCP_storage_auth_uri'],
        "token_uri": os.environ['sombra_GCP_storage_token_uri'],
        "auth_provider_x509_cert_url": os.environ['sombra_GCP_storage_auth_provider_x509_cert_url'],
        "client_x509_cert_url": os.environ['sombra_GCP_storage_client_x509_cert_url']
    }
    service_account_key_json = json.dumps(service_account_key)