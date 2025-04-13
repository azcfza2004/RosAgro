import asyncio
from aiogram import  types, F, Router
from aiogram.client.session import aiohttp
from aiogram.types import CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from docx import Document
from view import keyboards as kb
from pathlib import Path

router = Router()
ChatID = -4612403783
#Инциализпция работы с файлом history
doc = Document()
number_message = 0
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
    global number_message
    user_name =  message.from_user.full_name
    message_id = message.message_id
    date = str(message.date)[:-6]
    date_for_file = date.replace(' ','').replace(':','')
    text = message.text
    doc.add_paragraph(f" Имя:{user_name}\n{text}\nДата:{date}\nID сообщения:{message_id}")
    doc.save(r'model/data/'+user_name+'_'+str(number_message)+'_'+date_for_file+'.docx')
    p = doc.paragraphs[0]
    p_e = p._element
    p_e.getparent().remove(p_e)
    number_message += 1

