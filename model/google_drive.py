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


def get_folder_id(folder_name, parent_id=None):
    """
    Проверяет наличие папки в Google Drive и возвращает её ID.

    Args:
        folder_name (str): Название папки для поиска
        parent_id (str, optional): ID родительской папки. Если None, ищет в корне Drive.

    Returns:
        str|None: ID папки если найдена, иначе None
    """
    try:
        # Формируем запрос для поиска папки
        query = [
            "mimeType='application/vnd.google-apps.folder'",
            f"name='{folder_name}'",
            "trashed=false"
        ]

        if parent_id:
            query.append(f"'{parent_id}' in parents")

        # Выполняем запрос
        results = service.files().list(
            q=" and ".join(query),
            fields="files(id, name)",
            pageSize=10  # Ограничиваем количество результатов
        ).execute()

        folders = results.get('files', [])

        if folders:
            # Возвращаем ID первой найденной папки
            return folders[0]['id']

        return None

    except Exception as e:
        print(f"Ошибка при поиске папки '{folder_name}': {e}")
        return None

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