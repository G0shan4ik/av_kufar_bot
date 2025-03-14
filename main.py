from aiogram.methods import DeleteWebhook
from aiogram.utils.markdown import hbold

from teleg.bot.core import bot_, dp, admin_id
from teleg.database import init
from teleg.parser.pars_data import schedule

import sys
import logging
import asyncio


async def on_startup(dispatcher):
    await bot_.send_message(
        chat_id=admin_id,
        text=hbold('Бот снова запущен!')
    )


async def on_shutdown(dispatcher):
    await bot_.send_message(
        chat_id=admin_id,
        text=hbold('Бот остановлен 😥, дла проведения технических работ!\n'
                   'Это не займёт много времени)')
    )

async def main():
    await bot_(DeleteWebhook(drop_pending_updates=True))
    init()

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    await asyncio.gather(
        dp.start_polling(bot_),
        schedule()
    )


def start_dev():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())