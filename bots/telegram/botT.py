from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils import executor

from config import CANCEL, dayWeek, sunday, USER_ID_T
from config import TOKEN_TELEGRAM, MSG_HELLO_T, MSG_CHECK_BUTTON, EXCEPTION, CHECK
from db.database import create, getDay, checkGroup

bot = Bot(token=TOKEN_TELEGRAM, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

primaryKeyboard = types.ReplyKeyboardMarkup(keyboard=[
    [
        types.KeyboardButton('This Day'),
        types.KeyboardButton('Next Day')
    ],
    [
        types.KeyboardButton('This Week'),
        types.KeyboardButton('Next Week')
    ]
], resize_keyboard=True)


class Form(StatesGroup):
    groupId = State()


async def on_startup(dp):
    print('Бот запущен!')

    await set_commands(dp)


async def set_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand('start', 'Запуск')
        # types.BotCommand('help', 'Помощь')
    ])


@dp.message_handler(Command('start'))
async def start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [
            types.KeyboardButton('Cancel')
        ]
    ], resize_keyboard=True)
    await message.answer(MSG_HELLO_T, reply_markup=keyboard)
    await Form.groupId.set()


@dp.message_handler(state=Form.groupId)
async def hand(message: types.Message, state: FSMContext):
    if message.text == 'Cancel':
        await cancel(message)
        await state.finish()
        return
    await message.answer(CHECK)
    group = message.text.upper().replace(" ", "")
    msg = create(message.chat.id, group, message.from_user.id)
    if msg[0]:
        await message.answer(
            f'Не существует группы {group}\nПовторите попытку\nПример: ПИ.1-20-1(И,О)-2'
        )
        await Form.groupId.set()
    else:
        await state.update_data(groupId=group)
        await message.answer(msg[1], reply_markup=primaryKeyboard, reply=True)
        await message.answer(MSG_CHECK_BUTTON)
        await dp.bot.send_message(chat_id=USER_ID_T, text=f'{message.chat.id}, {message.text}')
        await state.finish()


async def cancel(message: types.Message):
    if checkGroup(message.chat.id):
        await message.answer(CANCEL, reply_markup=primaryKeyboard, reply=True)
    else:
        await message.answer(CANCEL, reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(Text(equals='This Day'))
async def start(message: types.Message):
    msg = message.text.split(' ')
    day = dayWeek(msg)
    try:
        response = getDay(message.from_id, day[0], 'this')
        photo = open(response, 'rb')
        await bot.send_photo(message.chat.id, photo)
    except Exception:
        try:
            response = getDay(message.chat.id, day[0], 'this')
            photo = open(response, 'rb')
            await bot.send_photo(message.chat.id, photo)
        except Exception as ex:
            print(ex)
            await message.answer(sunday(msg, day))


@dp.message_handler(Text(equals='Next Day'))
async def start(message: types.Message):
    msg = message.text.split(' ')
    day = dayWeek(msg)
    try:
        response = getDay(message.from_id, day[0], day[1])
        photo = open(response, 'rb')
        await bot.send_photo(message.chat.id, photo)
    except Exception:
        try:
            response = getDay(message.chat.id, day[0], day[1])
            photo = open(response, 'rb')
            await bot.send_photo(message.chat.id, photo)
        except Exception as ex:
            print(ex)
            await message.answer(sunday(msg, day))


@dp.message_handler(Text(equals='This Week'))
async def start(message: types.Message):
    try:
        response = getDay(message.from_id, 'week', 'this')
        photo = open(response, 'rb')
        await bot.send_photo(message.chat.id, photo)
    except Exception:
        try:
            response = getDay(message.chat.id, 'week', 'this')
            photo = open(response, 'rb')
            await bot.send_photo(message.chat.id, photo)
        except Exception as ex:
            print(ex)
            await message.answer(EXCEPTION)


@dp.message_handler(Text(equals='Next Week'))
async def start(message: types.Message):
    try:
        response = getDay(message.from_id, 'week', 'next')
        photo = open(response, 'rb')
        await bot.send_photo(message.chat.id, photo)
    except Exception:
        try:
            response = getDay(message.chat.id, 'week', 'next')
            photo = open(response, 'rb')
            await bot.send_photo(message.chat.id, photo)
        except Exception as ex:
            print(ex)
            await message.answer(EXCEPTION)


def startT():
    executor.start_polling(dp, on_startup=on_startup)


if __name__ == '__main__':
    startT()
