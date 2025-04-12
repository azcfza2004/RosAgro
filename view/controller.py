import asyncio
from aiogram import  types, F, Router
from aiogram.client.session import aiohttp
from aiogram.types import CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from docx import Document
from view import keyboards as kb

router = Router()
ChatID = -4612403783

#Инциализпция работы с файлом history
doc = Document(r'model\data\history.docx')

class Href(StatesGroup): # состояния
    start = State()
    generate = State()
    callable = State()
    waiting_for_message = State()
    flag = 0

@router.message(F.text == 'Старт')
async def echo(message: types.Message,state: FSMContext):
    await message.answer(text = f'Здравствуйте, {message.from_user.first_name}.\nВведите данные',
                         reply_markup=kb.start)
    await state.set_state(Href.start)


# Сделать процесс бар
@router.message(Href.start)
async def process_bar( message: types.Message, state: FSMContext):
    await state.update_data(href =message.text)
    await message.answer(text='Идёт генерация сводного отчёта')
    await state.set_state(Href.generate)

@router.message(F.text == "Start")
async def handle_message(message: types.Message, state: FSMContext):
    await state.set_state(Href.waiting_for_message)

# Сбор информации с чата построчно
@router.message(Href.waiting_for_message)
async def handle_message(message: types.Message, state: FSMContext):
    user_name =  message.from_user.full_name
    message_id = message.message_id
    date = message.date
    text = message.text
    doc.add_paragraph(f" Имя: {user_name}, Текст: {text}, Дата: {date}, id сообщения: {message_id}")
    doc.save(r'model\data\history.docx')

