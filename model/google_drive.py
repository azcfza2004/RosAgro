from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Путь к JSON-файлу с ключами
SERVICE_ACCOUNT_FILE = 'model/data/rosagro-457208-a317a0388f0c.json'
# ID папки, к которой предоставили доступ
FOLDER_ID = '1J2magEKLM476PjfiqLV6Cc_b4iyLNPhT'


# Создаем credentials
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=['https://www.googleapis.com/auth/drive']
)

# Создаем сервис
service = build('drive', 'v3', credentials=credentials)


def check_folder_exists(folder_name, parent_id=FOLDER_ID):
    """
        Проверяет, существует ли папка в Google Drive.
        :param folder_name: Название папки
        :param parent_folder_id: ID корневой папки
    """
    query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false"

    if parent_id:
        query += f" and '{parent_id}' in parents"

    results = service.files().list(
        q=query,
        fields="files(id, name)"
    ).execute()

    folders = results.get('files', [])
    return bool(folders)


def create_folder(folder_name, parent_folder_id=FOLDER_ID):
    """
    Создание папки в гугл диске
    :param folder_name: Название папки
    :param parent_folder_id: ID корневой папки
    """
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


def load_excel(file_path, folder_id=FOLDER_ID):
    """
    Загрузка таблицы в гугл диск
    :param file_path: путь до таблицы
    :param folder_id: ID корневой папки
    """
    file_metadata = {
        'name': file_path,
        'parents': [folder_id]
    }
    media = MediaFileUpload('model/data/' + file_path, mimetype='mimetype=application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

# Загрузка word
def load_word(file_path, folder_id=FOLDER_ID ):
    """
    Загрузка файлов текстовых сообщений
    :param file_path: Имя файла
    :param folder_id: ID корневой папки
    """
    file_metadata = {
        'name': file_path,
        'parents': [folder_id]
    }
    media = MediaFileUpload('model/data/' + file_path, mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
