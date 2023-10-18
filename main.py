import os
import asyncio
import logging

from handlers.start import start_router

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Bot token can be obtained via https://t.me/BotFather
TOKEN = os.getenv("BOT_TOKEN")


async def main() -> None:
    # Dispatcher is a root router
    dp = Dispatcher()
    # Register all the routers from handlers package
    dp.include_routers(
        start_router,
    )

    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())




# import os
# from dotenv import load_dotenv
# dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
# if os.path.exists(dotenv_path):
#     load_dotenv(dotenv_path)
#
# TOKEN = os.getenv("BOT_TOKEN")
#
# import asyncio
# import logging
# from aiogram import Bot, Dispatcher, types
# from aiogram.filters.command import Command
#
# # Включаем логирование, чтобы не пропустить важные сообщения
# logging.basicConfig(level=logging.INFO)
# # Объект бота
# bot = Bot(token=TOKEN)
# # bot.delete_webhook()
# # Диспетчер
# dp = Dispatcher()
#
#
# @dp.message(Command("start"))
# async def cmd_start(message: types.Message):
#     await message.answer("Hello!")
#
#
# async def main():
#     await dp.start_polling(bot)
#
# if __name__ == "__main__":
#     asyncio.run(main())