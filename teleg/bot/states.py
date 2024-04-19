from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from .core import router
from .helpers import delete_link, get_user
from .keyboard import start_kb

from teleg.parser.pars_data import first_pars


class AddState(StatesGroup):
    add_id = State()


@router.message(F.text == 'Отмена')  # exit the state
async def exit_the_state(message: Message, state: FSMContext):
    await message.answer(
        text='Вы вурнулись в главное меню.',
        reply_markup=start_kb(message.from_user.id)
    )
    await state.clear()


@router.message(AddState.add_id, F.text.startswith('https://'))
async def add_link_(message: Message, state: FSMContext):
    site_name = 'kufar'
    if 'cars.av.by' in message.text:
        site_name = 'av'
    print(site_name)
    await first_pars(url=message.text, user_id=message.from_user.id, site_name=site_name)

    get_user(
        id_user=message.from_user.id,
        link=message.text,
        site_name=site_name
    )

    await message.answer(
        text='Ваша ссылка успешно установлена!',
        reply_markup=start_kb(message.from_user.id)
    )

    await state.clear()
