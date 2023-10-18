from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from database import create, is_existed, list_users, get_user, update_term

start_router = Router()


@start_router.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Hello, <b>{message.from_user.full_name}!</b>")


@start_router.message(Command("add"))
async def command_start_handler(message: Message) -> None:
    create(message)
    await message.answer(f"Hello, <b>{message.from_user.full_name}!</b>")


@start_router.message(Command("is"))
async def command_start_handler(message: Message) -> None:
    is_existed(message)
    await message.answer(f"Hello, <b>{message.from_user.full_name}!</b>")


@start_router.message(Command("list_users"))
async def command_start_handler(message: Message) -> None:
    list_users()
    await message.answer(f"Hello, <b>{message.from_user.full_name}!</b>")


@start_router.message(Command("list_users_term1"))
async def command_start_handler(message: Message) -> None:
    list_users('term1')
    await message.answer(f"Hello, <b>{message.from_user.full_name}!</b>")


@start_router.message(Command("get_user"))
async def command_start_handler(message: Message) -> None:
    get_user(message)
    await message.answer(f"Hello, <b>{message.from_user.full_name}!</b>")


@start_router.message(Command("update_term1"))
async def command_start_handler(message: Message) -> None:
    update_term(message, 'term1')
    await message.answer(f"Hello, <b>{message.from_user.full_name}!</b>")