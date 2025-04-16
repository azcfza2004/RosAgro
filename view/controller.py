import os
import logging
from datetime import datetime

from aiogram import types, F, Router
from docx import Document

from model.assistant import catch_messages, clear_file
from model.excel import write_data, generate_table

router = Router()

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

number_docx = 1

async def handle_message(message: types.Message):
    """
    Сохраняет текст сообщения от пользователя в файл .docx.

    Args:
        :param message: Объект сообщения от пользователя (aiogram.types.message).
    """
    try:
        global number_docx

        # Получаем информацию о пользователе и сообщении
        user_name = message.from_user.full_name
        #date = message.date + datetime.timedelta(hours=3)
        text = message.text

        # Формируем имя файла (имяпользователя_номерсообщения_времядата.docx)
        #timestamp_str = date.strftime("%M%H%d%m%Y")
        #filename = f"{user_name}_{number_docx}_{timestamp_str}.docx"
        filename = f"{user_name}_{number_docx}_{1}.docx"
        filepath = os.path.join("model/data", filename)

        # Создаем новый документ .docx
        doc = Document()
        doc.add_paragraph(text)
        doc.save(filepath)
        number_docx += 1

        logging.info(f"Сообщение от {user_name} сохранено в {filepath}")

        logging.info(f"Возвращенный текст: {text}")  # Пример использования возвращенного значения
        clear_file('model/processed_data/data.jsonl')
        catch_messages(text)

        if (os.path.isfile('model/data/table1.xlsx') == False):
            generate_table()
        write_data()


    except Exception as e:
        logging.error(f"Ошибка при обработке сообщения: {e}")
        await message.reply(f"Произошла ошибка при сохранении сообщения: {e}")  # Отправляем сообщение об ошибке пользователю


@router.message(F.text)
async def process_message(message: types.Message, ):
    """Обрабатывает все текстовые сообщения, сохраняя их в файл."""
    await handle_message(message) # вызываем асинхронную функцию