import asyncio
import logging
from aiogram import Bot, Dispatcher
from view.controller import router

bot = Bot(token = TOKEN_API)
dp = Dispatcher()


async def main():
    """ Метод для запуска бота """
    dp.include_router(router)
    await dp.start_polling(bot, skip_updates=True) # запуск

if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')

