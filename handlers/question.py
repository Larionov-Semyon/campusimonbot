import os
import logging

from aiogram import Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from database import create, is_existed, list_users, get_user, update_term

question_router = Router()


class QuestionState(StatesGroup):
    """Storing the status for feedback (FAQ)"""
    sending = State()


@question_router.message(StateFilter(None), Command("question"))
async def message_send_handler(message: Message, state: FSMContext) -> None:
    user = get_user(message)
    await message.answer(
        'Напиши вопрос:',
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Отмена")]],
            resize_keyboard=True,
            ),
    )
    await state.set_state(QuestionState.sending)


@question_router.message(QuestionState.sending, Command("cansel"))
@question_router.message(QuestionState.sending, F.text.casefold() == 'отмена')
async def process_after_sending_cansel(message: Message, state: FSMContext, bot: Bot) -> None:
    creator = os.environ["CREATOR"]
    user = get_user(message)

    text_message = f'ATTEMPT SEND MESSAGE FROM {user}\n\n' \
                   f'TEXT:\n' \
                   f'{message.text}'
    await bot.send_message(chat_id=creator, text=text_message)

    await message.answer(
        "Вы не отправили сообщение",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.clear()


@question_router.message(QuestionState.sending)
async def process_after_sending_cansel(message: Message, state: FSMContext, bot: Bot) -> None:
    creator = os.environ["CREATOR"]
    user = get_user(message)

    text_message = f'SEND MESSAGE FROM {user}\n\n' \
                   f'TEXT:\n' \
                   f'{message.text}'
    await bot.send_message(chat_id=creator, text=text_message)

    await message.reply(
        "Вы отправили сообщение",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.clear()