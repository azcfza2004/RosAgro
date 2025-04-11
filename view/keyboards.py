from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

start = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text = 'Старт')]], # Кнопка старт
                            resize_keyboard= True)
