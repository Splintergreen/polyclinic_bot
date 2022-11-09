from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.utils import executor
import os
from dotenv import load_dotenv
import requests
from data import RequestData
from aiogram.contrib.fsm_storage.memory import MemoryStorage


load_dotenv()
secret_token = os.getenv('TOKEN')
bot = Bot(secret_token)
request_data = RequestData()
storage = MemoryStorage()  # класс для хранения значений из ммашины состояний
dp = Dispatcher(bot, storage=storage)


class FSMStates(StatesGroup):
    state1 = State()
    state2 = State()
    # state3 = State()
    photo_data = State()


@dp.message_handler(commands='start', state=None)
async def start(message: types.Message):
    await FSMStates.state1.set()  # Запуск первого состояния машины состояний
    await message.reply('Введите что-то для state1')

# Функция для возможности отмены машины состояний
@dp.message_handler(state='*', commands='отмена')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_state_mashine(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('OK')


@dp.message_handler(state=FSMStates.state1)
async def state1_func(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['state1'] = message.text  # сохраняем полученный от пользователя ввод в словарь
    await FSMStates.next()  # переход к следующему состоянию машины состояний
    await message.reply('А теперь для state2')


@dp.message_handler(state=FSMStates.state2)
async def state2_func(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['state2'] = message.text
    await FSMStates.next()
    await message.reply('Теперь можно и картинку загрузить')





# функция для сохранения фото, хранится ID фотки, сама фотка на серваке телеги
# получаем последний ответ и закрываем машину состояний
@dp.message_handler(content_types=['photo'], state=FSMStates.photo_data)
async def photo_state_func(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo_data'] = message.photo[0].file_id
    # await FSMStates.next()
    # await message.reply('сюда можно закинуть фотку')


    async with state.proxy() as data:
        await message.reply(str(data))

    await state.finish()



@dp.message_handler()
async def echo_send(message: types.Message):
    # await message.answer(message.text)
    # await message.reply(message.text)
    await bot.send_message(message.from_user.id, message.text)

executor.start_polling(dp, skip_updates=True)
