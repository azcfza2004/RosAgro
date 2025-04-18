import asyncio
import os
import glob
import logging
import time
import re
from datetime import datetime
from aiogram import types, F, Router
from aiogram.types import FSInputFile
from docx import Document
from model.assistant import catch_messages, clear_file
from model.excel import write_data, generate_table, check_table
from model. google_drive import *

folder_id = '1J2magEKLM476PjfiqLV6Cc_b4iyLNPhT'
folder = ''
router = Router()

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Словарь для хранения времени с последнего сообщения и флага отправки сообщения
user_data = {}
# Порядковый номер документа
number_docx = 1
# Количество сообщений не связанных с заполнением сводной таблицы
number_errors = 0

def is_agronom_report(text):
    """
        Определяет - является ли сообщение отчетом агронома

        Args:
            :param text - сообщение агронома

        Returns:
            bool: обозначение является ли сообщение отчетом агронома
        """

    # Нормализация текста
    text = text.lower()
    text = re.sub(r'[.,\-—)(]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    # Словари всех вариантов написания
    operations = {
        'диск', 'дисков', 'дискование', 'пахот', 'пахота', 'вспашк', 'чизел',
        'чизелевание', 'прикат', 'прокатывание', 'выравн', 'выравнивание',
        'культ', 'культивация', 'боронован', 'боронование', 'сев', 'посев',
        'уборк', 'уборка', 'внесен', 'внесение', 'подкорм', 'подкормка',
        'сзр', 'гербицид', 'герб', 'обработк', 'затравк', 'затравка',
        'подготовк', 'мин удобр', 'внес мин удобр', 'подкормка', 'химпрополка',
        'довсходовое', 'предпосевн', 'предп', 'предпосевная', 'прокат'
    }

    cultures = {
        # Пшеница
        'пш', 'пшениц', 'оз пш', 'оз. пш', 'озим пш', 'озим. пш', 'оз пшениц',
        # Ячмень
        'ячм', 'ячмен', 'оз ячм', 'оз. ячм', 'озим ячм', 'оз ячмень',
        # Свекла
        'сах св', 'сах. св', 'свекл', 'сах свекл', 'сахарн св', 'сахар. св', 'сах.св', 'сах/св',
        # Кукуруза
        'кук', 'кукуруз', 'кук зерн', 'кук. зерн', 'кук силос', 'кук. силос', 'кук/сил', 'кук/зерн',
        # Рапс
        'рапс', 'оз рапс', 'оз. рапс',
        # Подсолнечник
        'подсол', 'подсолнечн', 'подс', 'подсолн',
        # Соя
        'соя', 'соев', 'соевые', 'сою',
        # Травы
        'мн тр', 'многол тр', 'многолет тр', 'трав', 'кормовые',
        # Овёс
        'овс', 'овса', 'оз овс',
        # Горох
        'горох',
        # Силос
        'сил', 'силос'
    }

    structural = {
        'пу', 'по пу', 'по.пу', 'попу', 'отд', 'отделение', 'отд.', 'бригада',
        'день', 'ночь', 'га', 'оз', 'г', 'план', 'остаток', 'от начала', 'закончили'
    }

    locations = {
        'юг', 'аор', 'тск', 'сп коломейцево', 'ао кропоткинское', 'мир',
        'рассвет', 'восход', 'воронежская', 'ростовская', 'краснодарская'
    }

    # Проверка 1: Наличие сельхозоперации (минимум 1)
    has_operation = any(op in text for op in operations)

    # Проверка 2: Наличие культуры (минимум 1)
    has_culture = any(cult in text for cult in cultures)

    # Проверка 3: Формат площадей (X/Y, X-Y, X Y)
    has_areas = re.search(r'\b\d+\s*[\/\- ]\s*\d+\b', text)

    # Проверка 4: Структурные элементы (ПУ/Отд и др.)
    has_structure = any(struct in text for struct in structural) or \
                    re.search(r'(пу|отд)\s*\d+', text)

    # Проверка 5: Дата в начале (DD.MM, DD.MM.YY)
    has_date = re.search(r'^\d{1,2}\s*\.\s*\d{1,2}(\s*\.\s*\d{2,4})?\b', text)

    # Проверка 6: Проценты выполнения
    has_percent = re.search(r'\d+\s*%|\(\d+%\)', text)

    # Проверка 7: Единицы измерения (га, кг, т, л)
    has_units = re.search(r'\b\d+\s*(га|кг|т|л)\b', text)

    # Проверка 8: Локации/подразделения
    has_location = any(loc in text for loc in locations)

    # Проверка 9: Урожайность/вал
    has_yield = re.search(r'(урож|урожайность|вал)\s*\d+', text)

    # Комбинированные критерии
    main_criteria = sum([
        has_operation,
        has_culture,
        bool(has_areas),
        bool(has_structure),
        bool(has_location)
    ])

    secondary_criteria = sum([
        bool(has_date),
        bool(has_percent),
        bool(has_units),
        bool(has_yield)
    ])

    # Сообщение считается отчетом если:
    # 1. Есть ≥3 основных критерия ИЛИ
    # 2. Дата + ≥1 основной критерий ИЛИ
    # 3. ≥2 основных + ≥2 второстепенных критерия
    return (main_criteria >= 3) or \
        (has_date and main_criteria >= 1) or \
        (main_criteria >= 2 and secondary_criteria >= 2)

async def send_reminder(message: types.Message, chat_id: int):
    """
    Отправляет отчёт пользователям в чат.

    Args:
        :param chat_id: ID определённого чата
        :param message: Объект сообщения от пользователя (aiogram.types.message).
    """
    try:
        global user_data

        # Поиск последнего сохраненного файла
        fallback_pattern = f"model/data/*_Лонг-айленд.xlsx"
        matching_files = sorted(glob.glob(fallback_pattern), reverse=True)
        file_name = matching_files[0] if matching_files else None
        new_file_name = file_name[11:]
        # print(new_file_name)
        # Отправка сводного отчёта в гугл диск
        load_excel(file_path=new_file_name, folder_id=folder_id)

        document = FSInputFile(file_name)
        try:
            if os.path.exists(file_name):
                os.remove(file_name)
                print(f"Файл {file_name} успешно удален.")
                return True
            else:
                print(f"Файл {file_name} не существует.")
                return False
        except Exception as e:
            print(f"Ошибка при удалении файла: {e}")
            return False
        user_data[chat_id]['reminder_sent'] = True  # Устанавливаем флаг, что напоминание отправлено
        await message.bot.send_document(chat_id=chat_id, document = document, caption="Сгенерированный отчёт")
        logging.info(f'Количество необработанных сообщений (флуд): {number_errors}')

    except Exception as e:
        logging.error(f"Ошибка при отправке таблицы пользователю {chat_id}: {e}")
        # await message.answer("Ошибка при отправке сгенерированного отчёта")

async def handle_message(message: types.Message, date: float):
    """
    Обрабатывает сообщение и составляет

    Args:
        :param date: Дата этого сообщения
        :param message: Объект сообщения от пользователя (aiogram.types.message).
    """
    try:
        global number_docx
        global folder

        # Получаем информацию о пользователе и сообщении
        user_name = message.from_user.full_name
        text = message.text


        # Формируем имя файла (имяпользователя_номерсообщения_времядата.docx)
        timestamp_str = datetime.fromtimestamp(date).strftime("%M%H%d%m%Y")
        filename = f"{user_name}_{number_docx}_{timestamp_str}.docx"
        filepath = os.path.join("model/data", filename)


        # Разбираем строку обратно в datetime
        parsed_date = datetime.strptime(timestamp_str, "%M%H%d%m%Y")
        # Теперь можно получить нормальную дату в любом формате
        correct_date = parsed_date.strftime("%Y-%m-%d %H:%M")

        # Создаем новый документ .docx
        doc = Document()
        doc.add_paragraph(text)
        doc.save(filepath)
        number_docx += 1

        # Отправка файла в гугл таблицу
        if get_folder_id('message', parent_id=folder_id) == None:
            folder = create_folder(folder_name='message', folder_id=folder_id)

        load_word(filename, folder_id=folder)

        logging.info(f"Сообщение от {user_name} сохранено в {filepath}")

        logging.info(f"Возвращенный текст: {text}")

        #Очищаем файл для записи очередной порции данных
        clear_file('model/processed_data/data.jsonl')

        #Вызов обработки полученного сообщения
        catch_messages(text, correct_date)

        # Формируем имя файла (ЧасДеньМесяцГод_НазваниеКоманды.xlsx)
        timestamp_str = datetime.fromtimestamp(date).strftime("%H%d%m%Y")
        filename = f"{timestamp_str}_Лонг-айленд.xlsx"

        #В случае если таблицы для записи нет - создать ее
        if not os.path.isfile(f'model/data/{filename}'):
            generate_table(f'model/data/{filename}')

        #Дозапись данных в таблицу
        write_data(table_name=f'model/data/{filename}')

        #Проверка возможных ошибок в таблице
        check_table(f'model/data/{filename}')

    except Exception as e:
        logging.error(f"Ошибка при обработке сообщения: {e}")
        # await message.reply(f"Произошла ошибка при генерации отчёта")


async def process_message(message: types.Message):
    """
    Обрабатывает все текстовые сообщения и проверяет время последнего сообщения
        Args:
        :param message: Объект сообщения от пользователя (aiogram.types.message).
    """
    try:
        global user_data
        global number_errors

        # Проверка на флуд
        if not is_agronom_report(message.text):
            number_errors += 1
            return
        else:
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


            await asyncio.sleep(120)  # Ждем 2 минуты
            if (time.time() - int(user_data[chat_id]['last_message_time']) >= 120 and
                    not user_data[chat_id]['reminder_sent']):
                await send_reminder(message, chat_id)
    except Exception as e:
        logging.error(
            f"Ошибка при обработке сообщения от пользователя {message.from_user.id} в чате {message.chat.id}: {e}",
            exc_info=True)
        # await  message.answer("Ошибка обработки сообщения")

@router.message(F.text)
async def any_message_handler(message: types.Message):
    await process_message(message)

