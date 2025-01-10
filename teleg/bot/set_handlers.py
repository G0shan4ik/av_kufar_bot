from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import F
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
    await message.answer('Нажмите на кнопку:\n'
                         f'1){hbold("Следить за авто.")}, чтобы получать свежие уведомления по новым машинам\n'
                         f'2){hbold("Следить за другим объектом.")}, чтобы получать свежие уведомления по желаемому объекту')


@router.message(F.text == "Следить за авто.")
async def add_car_link(message: Message, state: FSMContext):
    await message.answer(f'Пришлите мне ссылку, по которой вы хотите узнавать новые объявления {hbold("автомобилей")}.',
                         # '(Наш бот может обрабатывать ссылки с Kufar.by и Av.by)',
                         reply_markup=cancel_kb()
                         )
    await state.set_state(AddState.add_id_car)

@router.message(F.text == "Следить за другим объектом.")
async def add_obj_link(message: Message, state: FSMContext):
    await message.answer(f'Пришлите мне ссылку, по которой вы хотите узнавать новые объявления {hbold("по указанной ссылке.")}',
                         reply_markup=cancel_kb()
                         )
    await state.set_state(AddState.add_id_obj)

@router.message(Command(commands=['all_links']))
async def get_all_links(message: Message):
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
        link = hlink(item[-2], item[-2])
        await message.answer(
            text=f'{st_name}{" (ссылка по авто)" if not item[-1] else " (ссылка по объекту)"}\n\n{link}',
            disable_web_page_preview=True,
            reply_markup=delete_kb(item[0])
        )


@router.message(Command(commands=['help']))
async def get_help_text(message: Message):
    await message.answer(
        text=f'Команда /start - {hbold("запустит бота.")}\n'
             f'Команда /all_links - {hbold("выведет список сохранённых ссылок.")}\n'
             f'''Чтобы установить ссылку, нажмите на кнопку - "{hbold('Добавить ссылку.')}"\n''',
        reply_markup=start_kb(message.from_user.id)
    )
