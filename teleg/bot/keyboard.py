from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from teleg.database import ParsInfo

from os import getenv
from dotenv import load_dotenv

load_dotenv()

ADMIN_ID = getenv('ADMIN_ID')

def start_kb(user_id: int):
    res_kb = [
            [KeyboardButton(text="Добавить ссылку.")],
            [KeyboardButton(text="Добавить юзера👨‍👩‍👦‍👦")]
        ] if user_id == int(ADMIN_ID) else [[KeyboardButton(text="Добавить ссылку.")]]
    return ReplyKeyboardMarkup(
        keyboard=res_kb,
        resize_keyboard=True,
        one_time_keyboard=True
    )

def cancel_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отмена")]],
        resize_keyboard=True,
        one_time_keyboard=True
        )


def get_flag_ikb(item: ParsInfo):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='⬅️',
                                     callback_data=f'previous-{item.ad_id}-{0}'),
                InlineKeyboardButton(text='➡️',
                                     callback_data=f'next_photo-{item.ad_id}-{0}')
             ],
            [InlineKeyboardButton(text='Ссылка на объявление', url=item.link)]
        ]
    )


def delete_kb(unique_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Удалить ссылку💣', callback_data='delete-' + unique_id)]
        ]
    )