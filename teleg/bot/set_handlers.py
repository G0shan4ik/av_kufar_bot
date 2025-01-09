from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import F
from aiogram.enums import ParseMode
from aiogram.utils.markdown import hbold, hlink

from .core import router, dp, admin_id
from .commands import set_commands
from .states import AddState
from .keyboard import cancel_kb, start_kb, delete_kb
from .helpers import get_links


@dp.message(CommandStart())
async def start_cmd(message: Message):
    user_id = message.from_user.id
    await set_commands()
    await message.answer(f'{hbold("Доброго времени суток")} {hbold(" -ADMIN-") if user_id == admin_id else ""}', reply_markup=start_kb(user_id))
    await message.answer(f'{"✌🏿" if user_id == admin_id else "✋"}')
    await message.answer('Нажмите на кнопку: "Добавить ссылку.", чтобы получать свежие уведомления по вашей ссылке')


@router.message(F.text == "Добавить ссылку.")
async def add_link(message: Message, state: FSMContext):
    await message.answer('Пришлите мне ссылку, по которой вы хотите узнавать самые свежие объявления авто.\n'
                         '(Наш бот может обрабатывать ссылки с Kufar.by и Av.by)',
                         reply_markup=cancel_kb()
                         )
    await state.set_state(AddState.add_id)


@router.message(Command(commands=['all_links']))
async def get_all_links(message: Message, state: FSMContext):
    all_links = get_links(message.chat.id)
    send_text = 'Вот все ваши ссылки в формате : \n\nсайт\nваша ссылка'
    if len(all_links) == 0:
        send_text = 'У вас нет сохранённых ссылок(\nЧтобы добавить ссылку, нажмите на кнопку - "Добавить ссылку."'

    await message.answer(
        text=send_text,
        reply_markup=start_kb(message.from_user.id),
    )
    for item in all_links:
        st_name = 'Av.by' if item[1] == 'av' else 'Kufar.by'
        link = hlink(item[-1], item[-1])
        await message.answer(
            text=f'{st_name}\n\n{link}',
            disable_web_page_preview=True,
            reply_markup=delete_kb(item[0])
        )


@router.message(Command(commands=['help']))
async def delete_link(message: Message, state: FSMContext):
    await message.answer(
        text=f'Команда /start - {hbold("запустит бота.")}\n'
             f'Команда /all_links - {hbold("выведет список сохранённых ссылок.")}\n'
             f'''Чтобы установить ссылку, нажмите на кнопку - "{hbold('Добавить ссылку.')}"\n''',
        reply_markup=start_kb(message.from_user.id)
    )
