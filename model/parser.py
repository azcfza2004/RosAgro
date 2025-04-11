from bs4 import BeautifulSoup
import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError


async def save_cookies():
    """
       Асинхронная функция для сохранения cookies и данных сессии WhatsApp Web.
    """
    try:
        # Создаем экземпляр Playwright (автоматическое закрытие через async with)
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                channel='chrome',
                headless=False  # Показать браузер пользователю
            )

            # Создаем новый контекст браузера
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto('https://web.whatsapp.com')

            print("Пожалуйста, отсканируйте QR-код в WhatsApp на телефоне")
            print("Ожидание 50 секунд для завершения авторизации...")

            await asyncio.sleep(50)

            # Сохраняем состояние сессии (куки, localStorage и т.д.)
            await context.storage_state(path='cookies/state.json')
            print("Данные авторизации успешно сохранены в файл cookies/state.json")

            await browser.close()

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        raise


# Запускаем асинхронную функцию
if __name__ == "__main__":
    asyncio.run(save_cookies())