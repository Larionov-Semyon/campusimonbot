import os
import logging

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiogram.exceptions import TelegramBadRequest

from database import create, is_existed, list_users, get_user, update_term

admin_router = Router()


class AdminState(StatesGroup):
    selection = State()
    write_post = State()
    sending = State()


@admin_router.message(Command("admin"))
async def command_admin_handler(message: Message) -> None:
    admins = os.getenv("ADMINS").split()
    creator = os.getenv("CREATOR")
    print(f'ADMINS: {admins}')

    await message.answer(f"Your chat.id: {message.chat.id}")
    if str(message.chat.id) == creator:
        await message.answer(f'{admins}')
    if str(message.chat.id) in admins:
        await message.answer('Successfully!')


@admin_router.message(Command("send_message"))
async def message_send_handler(message: Message, state: FSMContext) -> None:
    admins = os.getenv("ADMINS").split()
    if str(message.chat.id) in admins:
        await state.set_state(AdminState.selection)
        user = get_user(message)
        await message.answer(
            f'Выбери категории для отправки',
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="Далее"),]
                ],
                resize_keyboard=True,
            ),
        )
        await message.answer(
            f'<b>Выбери категории для отправки:</b>\n\n'
            f'Выберите интересующие вас направления:\n\n'
            f'Выставки\n'
            f'{"✅ Включено" if user["term1"] else "⛔️ Выключено"} - /toggle_term1\n\n'
            f'Собрания\n'
            f'{"✅ Включено" if user["term2"] else "⛔️ Выключено"} - /toggle_term2\n\n'
            f'Познавательное\n'
            f'{"✅ Включено" if user["term3"] else "⛔️ Выключено"} - /toggle_term3\n\n'
        )


@admin_router.message(AdminState.selection, F.text.casefold() == "далее")
async def process__write_post(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(AdminState.write_post)
    await message.answer(
        'Напиши пост:',
        reply_markup=ReplyKeyboardRemove(),
    )
    # await show_summary(message=message, data=data, positive=False)
    # await message.reply(text=message.text)


@admin_router.message(Command("cancel"))
@admin_router.message(F.text.casefold() == "сancel")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    await message.answer('Cancel')
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.answer(
        "Cancelled.",
        reply_markup=ReplyKeyboardRemove(),
    )


@admin_router.message(AdminState.write_post)
async def process_name(message: Message, state: FSMContext, bot: Bot) -> None:
    if message.text is None:
        photo = message.photo[-1]
        photo_id = photo.file_id
        file = await bot.get_file(photo_id)
        file_url = file.file_path
        print(f'message {message.text=} {message.caption=} {photo}')
        await state.update_data(caption=message.caption, photo=photo_id)
    else:
        await state.update_data(text=message.text)
    await state.set_state(AdminState.sending)

    user = get_user(message)
    data = await state.get_data()
    try:
        if 'text' in data:
            await bot.send_message(chat_id=user['chatid'], text=data['text'])
        elif 'photo' in data:
            # photo = InputFile(data['photo'], 'rb')
            await bot.send_photo(chat_id=user['chatid'], photo=data['photo'], caption=data['caption'])
    except TelegramBadRequest:
        await message.answer('Тут должен был быть пост, но что-то пошло не по плану')

    await message.answer(
        f'Отправить?',
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Yes"),
                    KeyboardButton(text="No"),
                ]
            ],
            resize_keyboard=True,
        ),
    )


@admin_router.message(AdminState.sending, F.text.casefold() == "no")
async def process_dont_like_write_bots(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    print(f'data {data}')
    await state.clear()
    await message.answer(
        "Вы не отправили сообщение",
        reply_markup=ReplyKeyboardRemove(),
    )
    # await show_summary(message=message, data=data, positive=False)


@admin_router.message(AdminState.sending, F.text.casefold() == "yes")
async def process_like_write_bots(message: Message, state: FSMContext, bot: Bot) -> None:

    await message.reply(
        "Отправляем сообщения",
        reply_markup=ReplyKeyboardRemove(),
    )

    data = await state.get_data()
    print(f'data {data}')

    user = get_user(message)
    lst = []
    if user['term1'] == 1 and user['term2'] == 1 and user['term3'] == 1:
        lst = list_users()
    else:
        if user['term1'] == 1:
            lst += list_users('term1')
        if user['term2'] == 1:
            lst += list_users('term2')
        if user['term3'] == 1:
            lst += list_users('term3')

    ans = []
    for l in lst:
        print('l', l)
        ans.append(l['chatid'])
    ans = list(set(ans))

    print(ans)

    checker = {'all': len(ans), 'good': 0, 'bad': 0}
    for user_id in ans:
        print(f'SENDING {user}')
        try:
            if 'text' in data:
                await bot.send_message(chat_id=user_id, text=data['text'])
            elif 'photo' in data:
                # photo = InputFile(data['photo'], 'rb')
                await bot.send_photo(chat_id=user_id, photo=data['photo'], caption=data['caption'])

            checker['good'] += 1
        except TelegramBadRequest:
            checker['bad'] += 1

    await state.clear()
    await message.answer(
        f'Готово {checker}',
        reply_markup=ReplyKeyboardRemove(),
    )