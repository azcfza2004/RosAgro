from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Путь к JSON-файлу с ключами
SERVICE_ACCOUNT_FILE = 'data/rosagro-457208-a317a0388f0c.json'
# ID папки, к которой предоставили доступ
FOLDER_ID = '1J2magEKLM476PjfiqLV6Cc_b4iyLNPhT'
# ID папки c docx файлами, к которой предоставили доступ
# DOCX_FOLDER_ID = '1YWc2LKFFmeCFlMnEQldtXVHRrrUUWtDh'

# Создаем credentials
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=['https://www.googleapis.com/auth/drive']
)

# Создаем сервис
service = build('drive', 'v3', credentials=credentials)


def create_folder(folder_name, parent_folder_id=FOLDER_ID):
    # Метаданные для новой папки
    file_metadata = {
        'name': folder_name,
        'parents': [parent_folder_id],
        'mimeType': 'application/vnd.google-apps.folder'
    }

    # Создаем папку
    folder = service.files().create(
        body=file_metadata,
        fields='id'
    ).execute()

    print(f"Folder ID: {folder.get('id')}")
    return folder.get('id')

# Загрузка Таблицы
def load_excel(file_path='Проблемы_с_датой.xlsx', folder_id=FOLDER_ID):
    file_metadata = {
        'name': file_path,
        'parents': [FOLDER_ID]
    }
    media = MediaFileUpload('data/' + file_path, mimetype='mimetype=application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

# Загрузка word
def load_word(file_path='BN_1_150418042025.docx', folder_id=FOLDER_ID ):
    file_metadata = {
        'name': file_path,
        'parents': [folder_id]
    }
    media = MediaFileUpload('data/' + file_path, mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
