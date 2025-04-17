from docx import Document
import json
import os

from setuptools import logging
from yandex_cloud_ml_sdk import YCloudML

# Инициализация SDK Yandex Cloud ML
sdk = YCloudML(
    folder_id="b1g6rjppcrrhq56lsqr0",  # Идентификатор облачной папки
    auth="AQVNxTuU2_Efl4APdsHSsNBwMzOpuLziy4TeHEr2"  # Токен авторизации
)

# Инициализация модели LLAMA Lite и настройка генерации
model = (sdk.models.completions("gpt://b1g6rjppcrrhq56lsqr0/llama-lite/latest@tamrshipv191qfa0c9qe8"))
model = model.configure(temperature=0.1, max_tokens=3000)

def create_thread():
    """
        Создает новый тред для обработки запроса
    """
    return sdk.threads.create(ttl_days=1, expiration_policy="static")

def create_assistant(model, tools=None):
    """
        Создает ассистента с указанной моделью и инструментами

        Args:
            :param model: Модель нейросети
            :param tools: Инструменты ассистента
    """
    kwargs = {}
    if tools and len(tools) > 0:
        kwargs = {"tools": tools}
    return sdk.assistants.create(
        model,
        ttl_days=1,
        expiration_policy="since_last_active",
        **kwargs
    )

def clear_file(filename):
    """
        Очищает содержимое указанного файла

        Args:
            :param filename: Имя файла для очистки
    """
    try:
        with open(filename, 'w') as file:
            file.write('')
    except IOError as e:
        logging.error(f"Ошибка очистки файла {filename}: {str(e)}")


def process_data(response, date):
    """
        Обрабатывает ответ нейросети и записывает его в формате json

        Args:
            :param response: Полный текст ответа нейросети
            :param date: Дата этого сообщения
    """

    key_names = [
        "Дата",
        "Подразделение",
        "Операция",
        "Культура",
        "За день, га",
        "С начала операции, га",
        "Вал за день, ц",
        "Вал с начала, ц"
    ]

    # Создаем директорию, если ее нет
    os.makedirs('model/processed_data', exist_ok=True)

    try:
        with open('model/processed_data/data.jsonl', 'a+', encoding='utf-8') as jsonl_file:
            data_lines = response.strip().split("\n")
            data_dict = {}

            for line in data_lines:
                line = line.strip()

                # Пропускаем пустые строки, если словарь пуст
                if not line and not data_dict:
                    continue

                if line:
                    try:
                        # Обрабатываем строки с ключами и значениями
                        if ": " in line:
                            key, value = map(str.strip, line.split(": ", 1))
                            if key in key_names:
                                data_dict[key] = value
                        elif line.endswith(":"):
                            data_dict[line[:-1].strip()] = ""
                        else:
                            data_dict[line.strip()] = ""
                    except Exception as e:
                        logging.error(f"Ошибка при обработке строки: {line}. Ошибка: {e}")
                else:
                    # Обработка завершенной записи
                    if len(data_dict) == 8:
                        # Проверка даты
                        if data_dict['Дата'] == "":
                            data_dict['Дата'] = date
                        jsonl_file.write(json.dumps(data_dict, ensure_ascii=False) + '\n')
                    data_dict = {}

            # Обработка последней записи, если она существует
            if data_dict and len(data_dict) == 8:
                # Проверка даты
                if data_dict['Дата'] == "":
                    data_dict['Дата'] = date
                jsonl_file.write(json.dumps(data_dict, ensure_ascii=False) + '\n')

    except Exception as e:
        logging.error(f"Ошибка при открытии или записи в файл: Ошибка: {e}")


def catch_messages(text, date):
    """
        Основной пайплайн обработки сообщения

        Args:
            :param text: Полный текст сообщения от пользователя
            :param date: Дата этого сообщения
    """
    try:
        # Валидация входных данных
        if not text.strip():
            raise ValueError("Пустой текст сообщения")


        # Создание и настройка ассистента
        assistant = create_assistant(model)
        assistant.update(
            instruction=
            """
            Ты — помощник агронома, который должен распределить информацию из собщения по группам.
            Каждая группа обязательно выводится с новой строки:
            Дата,
            Подразделение,
            Операция,
            Культура,
            За день га,
            С начала операции га,
            Вал за день ц,
            Вал с начала ц
            """
        )

        # Обработка запроса
        thread = create_thread()
        thread.write(text)

        response = assistant.run(thread).wait()
        if not response.text:
            raise RuntimeError("Пустой ответ от модели")

        process_data(response.text, date)

    except Exception as e:
        logging.error(f"Ошибка обработки сообщения: {str(e)}")
    finally:
        # Обязательная очистка ресурсов
        if 'thread' in locals():
            thread.delete()
        if 'assistant' in locals():
            assistant.delete()
