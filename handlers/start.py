import os
from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from database import create, is_existed, list_users, get_user, update_term

start_router = Router()


@start_router.message(Command("start"))
async def command_start_handler(message: Message, bot: Bot) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(
        f'Привет, <b>{message.from_user.full_name}!</b>\n'
        f'Это бот проекта Campus'
    )
    if not is_existed(message):
        user = create(message)
        print(f'CREATE USER {user}')

        await message.answer(
            f'Ты здесь впервые и мы рады тебя видеть! '
            f'Тут ты можешь получать актальные новости нашего проекты, '
            f'а еще ссылки на тематические группы. Жми на /subscribe '
            f'чтобы подписаться на интересные для тебя рассылки'
        )

        creator = os.getenv("CREATOR")
        await bot.send_message(chat_id=creator, text=f'CREATE USER {user}')


@start_router.message(Command("subscribe"))
async def command_subscribe_handler(message: Message) -> None:
    user = get_user(message)
    await message.answer(
        f'<b>Настройка подписок</b>\n\n'
        f'Выберите интересующие вас направления:\n\n'
        f'Выставки\n'
        f'{"✅ Включено" if user["term1"] else "⛔️ Выключено"} - /toggle_term1\n\n'
        f'Собрания\n'
        f'{"✅ Включено" if user["term2"] else "⛔️ Выключено"} - /toggle_term2\n\n'
        f'Познавательное\n'
        f'{"✅ Включено" if user["term3"] else "⛔️ Выключено"} - /toggle_term3\n\n'
    )


@start_router.message(Command("toggle_term1"))
async def command_start_handler(message: Message) -> None:
    update_term(message, 'term1')
    await command_subscribe_handler(message)


@start_router.message(Command("toggle_term2"))
async def command_start_handler(message: Message) -> None:
    update_term(message, 'term2')
    await command_subscribe_handler(message)


@start_router.message(Command("toggle_term3"))
async def command_start_handler(message: Message) -> None:
    update_term(message, 'term3')
    await command_subscribe_handler(message)


# @start_router.message(Command("add"))
# async def command_start_handler(message: Message) -> None:
#     create(message)
#     await message.answer(
#         f"Hello, <b>{message.from_user.full_name}!</b>",
#         reply_markup=ReplyKeyboardRemove(),
#     )


# @start_router.message(Command("is"))
# async def command_start_handler(message: Message) -> None:
#     is_existed(message)
#     await message.answer(f"Hello, <b>{message.from_user.full_name}!</b>")


# @start_router.message(Command("list_users"))
# async def command_start_handler(message: Message) -> None:
#     list_users()
#     await message.answer(f"Hello, <b>{message.from_user.full_name}!</b>")


# @start_router.message(Command("list_users_term1"))
# async def command_start_handler(message: Message) -> None:
#     list_users('term1')
#     await message.answer(f"Hello, <b>{message.from_user.full_name}!</b>")
#
#
# @start_router.message(Command("get_user"))
# async def command_start_handler(message: Message) -> None:
#     get_user(message)
#     await message.answer(f"Hello, <b>{message.from_user.full_name}!</b>")
