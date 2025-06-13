from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os

# Escopos
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Autenticação
def autenticar():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)

# Upload para o Drive
def upload_arquivo(nome_arquivo):
    service = autenticar()
    arquivo = MediaFileUpload(nome_arquivo, mimetype='application/sql')
    response = service.files().create(
        body={'name': nome_arquivo},
        media_body=arquivo
    ).execute()
    print(f'Arquivo enviado para o Drive: {response["id"]}')


upload_arquivo('backup_reserva_laboratorio_20250613_030655.sql')  
