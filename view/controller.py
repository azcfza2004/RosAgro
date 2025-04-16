import asyncio
import os
import logging
import time

from datetime import timedelta, datetime
from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from docx import Document
from model.assistant import catch_messages, clear_file
from model.excel import write_data, generate_table

router = Router()

class State_time(StatesGroup): # состояния
    state_time = State()

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Словарь для хранения времени с последнего сообщения и флага отправки сообщения
user_data = {}

number_docx = 1

async def send_reminder(message: types.Message, user_id: int):
    """
    Отправляет напоминание пользователю.

    Args:
        :param user_id: ID определённого чата
        :param message: Объект сообщения от пользователя (aiogram.types.message).
    """
    try:
        await message.answer("Крокодило Бомбордило.")
        user_data[user_id]['reminder_sent'] = True  # Устанавливаем флаг, что напоминание отправлено
    except Exception as e:
        logging.error(f"Ошибка при отправке напоминания пользователю {user_id}: {e}")

async def handle_message(message: types.Message, date: float):
    """
    Сохраняет текст сообщения от пользователя в файл .docx.

    Args:
        :param date: Дата этого сообщения
        :param message: Объект сообщения от пользователя (aiogram.types.message).
    """
    try:
        global number_docx

        # Получаем информацию о пользователе и сообщении
        user_name = message.from_user.full_name
        text = message.text

        # Формируем имя файла (имяпользователя_номерсообщения_времядата.docx)
        timestamp_str = datetime.fromtimestamp(date).strftime("%M%H%d%m%Y")
        filename = f"{user_name}_{number_docx}_{timestamp_str}.docx"
        filepath = os.path.join("model/data", filename)

        # Создаем новый документ .docx
        doc = Document()
        doc.add_paragraph(text)
        doc.save(filepath)
        number_docx += 1

        logging.info(f"Сообщение от {user_name} сохранено в {filepath}")

        logging.info(f"Возвращенный текст: {text}")
        clear_file('model/processed_data/data.jsonl')
        catch_messages(text)

        if not os.path.isfile('model/data/table1.xlsx'):
            generate_table()
        write_data()


    except Exception as e:
        logging.error(f"Ошибка при обработке сообщения: {e}")
        await message.reply(f"Произошла ошибка при сохранении сообщения: {e}")


@router.message(F.text)
async def process_message(message: types.Message, state: FSMContext):
    """Обрабатывает все текстовые сообщения, сохраняя их в файл."""
    chat_id = message.chat.id
    date = time.time()

    await handle_message(message, date)

    # Добавляем ID чата в словарь, если чат новый
    if chat_id not in user_data:
        user_data[chat_id] = {
            'last_message_time': date,
            'reminder_sent': False
        }
    else:
        user_data[chat_id]['last_message_time'] = date
        user_data[chat_id]['reminder_sent'] = False


    await asyncio.sleep(20)  # Ждем 5 секунд
    if (time.time() - int(user_data[chat_id]['last_message_time']) >= 19 and
            not user_data[chat_id]['reminder_sent']):
        await send_reminder(message, chat_id)

