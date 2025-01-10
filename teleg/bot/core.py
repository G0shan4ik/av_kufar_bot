from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties


from os import getenv

from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv


load_dotenv()

bot_ = Bot(
    token=getenv('TOKEN_API'),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

admin_id = int(getenv('ADMIN_ID'))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_routers(router)
