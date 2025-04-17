import asyncio
import os
import logging
import time
from datetime import datetime
from aiogram import types, F, Router
from aiogram.types import FSInputFile
from docx import Document
from model.assistant import catch_messages, clear_file
from model.excel import write_data, generate_table, check_table


router = Router()

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Словарь для хранения времени с последнего сообщения и флага отправки сообщения
user_data = {}

number_docx = 1

async def send_reminder(message: types.Message, chat_id: int):
    """
    Отправляет напоминание пользователю.

    Args:
        :param chat_id: ID определённого чата
        :param message: Объект сообщения от пользователя (aiogram.types.message).
    """
    try:
        global user_data

        document = FSInputFile("model/data/table1.xlsx")
        user_data[chat_id]['reminder_sent'] = True  # Устанавливаем флаг, что напоминание отправлено
        await message.bot.send_document(chat_id=chat_id, document = document, caption="Сгенерированный отчёт")
        # user_data[chat_id]['reminder_sent'] = True  # Устанавливаем флаг, что напоминание отправлено
    except Exception as e:
        logging.error(f"Ошибка при отправке таблицы пользователю {chat_id}: {e}")
        await message.answer("Ошибка при отправке сгенерированного отчёта")

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

        #Формирование корректной даты
        correct_date = timestamp_str[8:13] + "-" + timestamp_str[6:8] + "-" + timestamp_str[4:6] + " " + timestamp_str[2:4] + "_" + timestamp_str[0:2] + "_00"

        # Создаем новый документ .docx
        doc = Document()
        doc.add_paragraph(text)
        doc.save(filepath)
        number_docx += 1

        logging.info(f"Сообщение от {user_name} сохранено в {filepath}")

        logging.info(f"Возвращенный текст: {text}")

        #Очищаем файл для записи очередной порции данных
        clear_file('model/processed_data/data.jsonl')

        correct_date = correct_date.replace("_", ":")
        #Вызов обработки полученного сообщения
        catch_messages(text, correct_date)

        #В случае если таблицы для записи нет - создать ее
        if not os.path.isfile('model/data/table1.xlsx'):
            generate_table()
        #Дозапись данных в таблицу
        write_data()
        #Проверка возможных ошибок в таблице
        check_table()


    except Exception as e:
        logging.error(f"Ошибка при обработке сообщения: {e}")
        await message.reply(f"Произошла ошибка при генерации отчёта")


async def process_message(message: types.Message):
    """
    Обрабатывает все текстовые сообщения и проверяет время последнего сообщения
        Args:
        :param message: Объект сообщения от пользователя (aiogram.types.message).
    """
    try:
        global user_data

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


        await asyncio.sleep(5)  # Ждем 2 минуты
        if (time.time() - int(user_data[chat_id]['last_message_time']) >= 5 and
                not user_data[chat_id]['reminder_sent']):
            await send_reminder(message, chat_id)
    except Exception as e:
        logging.error(
            f"Ошибка при обработке сообщения от пользователя {message.from_user.id} в чате {message.chat.id}: {e}",
            exc_info=True)
        await  message.answer("Ошибка обработки сообщения")

@router.message(F.text)
async def any_message_handler(message: types.Message):
    await process_message(message)

