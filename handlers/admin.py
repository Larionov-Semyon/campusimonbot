import os
import logging
from datetime import date
import json

from aiogram import Router, F, Bot
from aiogram.filters import Command, BaseFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
)
from aiogram.exceptions import TelegramBadRequest
from aiogram.exceptions import AiogramError, TelegramForbiddenError
from aiogram.utils.media_group import MediaGroupBuilder

from database import create, is_existed, list_users, get_user, update_term, get_user_from_chatid
from handlers.constants import toggles, get_admins, get_creator
from filters.filter_admin import AdminFilter


admin_router = Router()
# проверка что пользователь является администратором
admin_router.message.filter(AdminFilter(get_admins()))


class AdminState(StatesGroup):
    selection = State()
    write_post = State()
    waiting = State()
    sending = State()


@admin_router.message(Command("admin"))
async def command_admin_handler(message: Message) -> None:
    """Command /admin"""
    creator = get_creator()

    # отправка списка админов
    if str(message.chat.id) == creator:
        await message.answer(f'{get_admins()}')

    # отправка списка доступных админам команд
    text_message = f'Команды доступные админам:\n\n' \
                   f'/send_message - отправить пост\n\n' \
                   f'/stat - статистика'
    await message.answer(text_message)


@admin_router.message(Command('stat'))
async def command_stat_handler(message: Message) -> None:
    """Command /stat. Sending application usage statistics"""
    list_all_users = list_users()
    text_message = f'Всего users - {len(list_all_users)}\n\n'

    text_message += 'Количество подписанных на разные tags:\n'
    ans = {}
    for toggle in toggles.keys():
        lst = list_users(toggle)
        ans[toggle] = len(lst)
    text_message += '\n'.join([f'{toggle} - {ans[toggle]}' for toggle in toggles])
    text_message += '\n\n'

    last_user = list_all_users[-1]
    text_message += f'Last user: {last_user["chatid"]} - {last_user["username"]}\n' \
                    f'Дата регистрации: {last_user["registrationdate"]}'

    await message.answer(text_message)


@admin_router.message(Command("send_message"))
async def message_send_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(AdminState.selection)
    user = get_user(message)
    await message.answer(
        f'<b>Выбери категории для отправки</b>\n\n'
        + '\n'.join([
            f'{toggles[key]}\n'
            f'{"✅ Включено" if user[key] else "⛔️ Выключено"} - /toggle_{key}\n'
            for key in toggles]),
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Далее"), ]
            ],
            resize_keyboard=True,
        ),
    )


@admin_router.message(AdminState.selection, F.text.startswith('/toggle_'))
async def message_toggle_handler(message: Message, state: FSMContext) -> None:
    data = message.text[8:]
    print(data)
    user = get_user(message)
    update_term(user, data)
    await message_send_handler(message, state)


@admin_router.message(AdminState.selection, F.text.casefold() == "далее")
async def process__write_post(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(AdminState.write_post)
    await message.answer(
        'Напиши пост:',
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.update_data(photo=[], video=[], document=[])


@admin_router.message(AdminState.selection, F.text.casefold() != "далее")
async def process__write_post(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        'Отмена',
        reply_markup=ReplyKeyboardRemove(),
    )


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
    print('----------------')
    print(*message)

    data = await state.get_data()

    if message.text is not None:
        # print(f'text {message.html_text}')
        data['text'] = message.html_text
    if message.caption is not None and 'caption' not in data:
        print(f'caption {message.html_text}')
        data['caption'] = message.html_text
    if message.photo is not None:
        # print(f'{message.photo[0].file_id=}')
        data['photo'].append(message.photo[0].file_id)
    if message.video is not None:
        data['video'].append(message.video.file_id)
    if message.document is not None:
        data['document'].append(message.document.file_id)

    print(f'{data=}')
    await state.update_data(data)
    print('----------------')
    await state.set_state(AdminState.waiting)

    await message.answer(
        'Нажмите далее',
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Далее"), ]
            ],
            resize_keyboard=True,
        ),
    )


@admin_router.message(AdminState.waiting)
async def process(message: Message, state: FSMContext, bot: Bot):

    await message.answer(f'Так будет выглядеть ваше сообщение:')

    data = await state.get_data()
    print(f'waiting {data=}')

    user = get_user(message)

    await _send_message(bot, data, user['chatid'])

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

    await state.set_state(AdminState.sending)


async def _send_message(bot: Bot, data, chat_id):
    if 'text' in data:
        await bot.send_message(chat_id=chat_id, text=data['text'], reply_markup=ReplyKeyboardRemove())
    else:
        if 'caption' in data:
            caption = data['caption']
        else:
            caption = None
        media_group = MediaGroupBuilder(caption=caption)
        for photo_id in data['photo']:
            print(f'{photo_id=}')
            media_group.add_photo(photo_id)
        for video_id in data['video']:
            print(f'{video_id=}')
            media_group.add_video(video_id)
        for doc_id in data['document']:
            print(f'{doc_id=}')
            media_group.add_document(doc_id)
        await bot.send_media_group(chat_id=chat_id, media=media_group.build())


@admin_router.message(AdminState.sending, F.text.casefold() == "no")
async def process_dont_like_write_bots(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    print(f'data {data}')
    await state.clear()
    await message.answer(
        "Вы не отправили сообщение",
        reply_markup=ReplyKeyboardRemove(),
    )


@admin_router.message(AdminState.sending, F.text.casefold() == "yes")
async def process_sending(message: Message, state: FSMContext, bot: Bot) -> None:
    creator = get_creator()

    await message.reply(
        "Отправляем сообщения",
        reply_markup=ReplyKeyboardRemove(),
    )

    data = await state.get_data()
    print(f'data {data}')

    sender = get_user(message)

    # получение списка уникальных id юзеров которые подписаны на теги рассылки
    ans = []
    for toggle in toggles.keys():
        if sender[toggle] == 1:
            lst = list_users(toggle)
            ans += [dict_user['chatid'] for dict_user in lst if get_user]
    ans = list(set(ans))
    print(ans)

    # начало отправки рассылки
    checker = {'all': len(ans), 'good': 0, 'bad': 0, 'is_blocked': 0}
    for user_id in ans:
        print(f'SENDING {user_id}')
        try:
            await _send_message(bot, data, user_id)

            user = get_user_from_chatid(user_id)
            if user['is_blocked'] == 1:
                update_term(user, 'is_blocked')

            checker['good'] += 1

        except TelegramForbiddenError:
            checker['bad'] += 1
            checker['is_blocked'] += 1

            user = get_user_from_chatid(user_id)
            if user['is_blocked'] == 0:
                update_term(user, 'is_blocked')

        except AiogramError as E:
            print(E)
            await bot.send_message(chat_id=creator, text=f'ERROR - {date.today()} - {E}')
            await message.reply(text=f'ERROR - {date.today()} - {F}')
            checker['bad'] += 1

    await state.clear()
    await message.answer(
        f'Готово {checker}',
        reply_markup=ReplyKeyboardRemove(),
    )
    await bot.send_message(chat_id=creator, text=f'Отчет отправки поста {sender["username"]}\n{checker}')