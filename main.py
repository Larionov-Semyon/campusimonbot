import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from handlers.start import start_router
from handlers.admin import admin_router
from handlers.question import question_router
from handlers.echo import echo_router
# from handlers.constants import

# Take the token from the .env file
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Bot token can be obtained via https://t.me/BotFather
# TOKEN = os.getenv("BOT_TOKEN")
TOKEN = os.environ["BOT_TOKEN"]


async def main() -> None:
    # Dispatcher is a root router
    dp = Dispatcher()
    # Register all the routers from handlers package
    dp.include_routers(
        start_router,
        admin_router,
        question_router,
        echo_router,
    )

    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)

    # # Skip the accumulated updates and start polling
    # await bot.delete_webhook(drop_pending_updates=True)

    creator = os.getenv("CREATOR")
    await bot.send_message(chat_id=creator, text=f'START BOT')

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())