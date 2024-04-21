import os
from aiogram import Router, Bot, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message

from database import create, is_existed, list_users, get_user, update_term

echo_router = Router()


@echo_router.message(StateFilter(None))
async def command_echo_handler(message: Message, bot: Bot) -> None:
        user = get_user(message)

        text_message = f'ECHO USER {user["chatid"]} {user["username"]}\n {message.text}'
        print(text_message)

        creator = os.getenv("CREATOR")
        await bot.send_message(chat_id=creator, text=text_message)