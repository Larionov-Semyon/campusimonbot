import os
from functools import wraps
from aiogram import Router, Bot, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from database import create, is_existed, list_users, get_user, update_term
from handlers.constants import toggles

start_router = Router()


@start_router.message(Command("start"))
async def command_start_handler(message: Message, bot: Bot) -> None:
    """
    This handler receives messages with `/start` command
    """
    if is_existed(message):
        await message.answer(
            f'Привет, <b>{message.from_user.full_name}!</b>\n'
            f'Это бот проекта Campus \n\n'
            f'Список основных команд:\n'
            f'/subscribe - подписки\n'
            f'/help - FAQ\n'
            f'/question  - задать вопрос\n',
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        creator = os.getenv("CREATOR")
        await bot.send_message(chat_id=creator,
                               text=f'CREATE USER {message.from_user.id} {message.from_user.username}')

        user = create(message)
        print(f'CREATE USER {user}')

        await message.answer(
            f'Привет! Это бот проекта Campus \n\n'
            f'Ты здесь впервые и мы рады тебя видеть!\n'
            f'Тут ты можешь получать актальные новости нашего проекты, '
            f'а еще ссылки на тематические группы. Жми на /subscribe '
            f'чтобы подписаться на интересные для тебя рассылки.\n\n'
            f'Если возникли вопросы, то можешь глянуть раздел '
            f'часто задаваемых вопросов (FAQ) /help или задать вопрос '
            f'напрямую администраторам /question.',
            reply_markup=ReplyKeyboardRemove(),
        )

        creator = os.getenv("CREATOR")
        await bot.send_message(chat_id=creator, text=f'CREATE USER SUCCESSFULLY! \n {user}')


@start_router.message(Command("help"))
async def command_help_handler(message: Message, bot: Bot) -> None:
    """
    This handler receives messages with `/help` command
    """
    await message.answer(
        f'<b>Часто задаваемые вопросы FAQ:</b>\n'
        f'1) Как работает наш бот?\n'
        f'Наш бот помогает тебе знакомиться с интересными '
        f'событиями в городе через подписки. Ты можешь подписаться /subscribe '
        f'на интересные тебе тематики, и получать уведомления о '
        f'событиях на эту тему\n'
        f'2) Как получить совет или помощь по волнующим меня вопросам?\n'
        f'У нас есть возможность обратиться за советом к экспертам проекта, '
        f'для этого жмите на /question и пишите администраторам.\n'
        f'3) Где получить полезные советы и рекомендации?\n'
        f'Мы регулярно размещаем полезные советы, студенческие лайфхаки '
        f'и интересные посты в нашем телеграм-канале @campus_explorer.'
    )


@start_router.message(Command("subscribe"))
async def command_subscribe_handler(message: Message) -> None:
    user = get_user(message)
    await message.answer(
        f'<b>Настройка подписок</b>\n\n'
        f'Выберите интересующие вас направления:\n\n'
        + '\n'.join([
            f'{toggles[key]}\n'
            f'{"✅ Включено" if user[key] else "⛔️ Выключено"} - /toggle_{key}\n'
            for key in toggles])
    )


@start_router.message(StateFilter(None), F.text.startswith('/toggle_'))
async def command_start_handler(message: Message) -> None:
    data = message.text[8:]
    print(data)
    user = get_user(message)
    update_term(user, data)
    await command_subscribe_handler(message)


@start_router.message(Command("kill"))
async def command_help_handler(message: Message, bot: Bot) -> None:
    """
    Stop the program (radically!)
    """
    creator = os.getenv("CREATOR")
    user = get_user(message)
    if user['chatid'] == creator:
        await bot.send_message(chat_id=creator, text=f'KILL BOT')
        quit()