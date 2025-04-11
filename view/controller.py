import asyncio

from aiogram import  types, F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from . import keyboards as kb

router = Router()

class Href(StatesGroup): # состояния
    start = State()
    generate = State()
    callable = State()
    flag = 0

@router.message(F.text == 'Старт')
async def echo(message: types.Message,state: FSMContext):
    await message.answer(text = f'Здравствуйте, {message.from_user.first_name}.\nВведите данные')
    await state.set_state(Href.start)

@router.message(F.text) #Обработка любого текста
async def on_start(message: types.Message, state: FSMContext):
    await message.answer(text="Нажмите старт",
                         reply_markup=kb.start)
    await state.clear()

# Сделать процесс бар
@router.message(Href.start)
async def process_bar( message: types.Message, state: FSMContext):
    await state.update_data(href =message.text)
    await message.answer(text='Идёт генерация сводного отчёта')
    await state.set_state(Href.generate)


@router.message(Href.generate)
async def generate_report (message: types.Message, state:FSMContext):
    pass
@router.message(F.text == "Стоп")
async def cmd_stop(message: types.Message, state: FSMContext):
    await state.update_data(flag=1)
    await message.answer(text="Что- то пошло так или не так",
                         reply_markup=kb.start)


