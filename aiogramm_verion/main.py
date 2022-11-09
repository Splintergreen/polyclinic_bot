from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.utils import executor
from variables import headers, patient_check_url, check_speciality_url, doctor_check_url, appointment_url
import os
from dotenv import load_dotenv
import requests
from data import RequestData
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram_calendar import dialog_cal_callback, DialogCalendar  # simple_cal_callback, SimpleCalendar


load_dotenv()
secret_token = os.getenv('TOKEN')
bot = Bot(secret_token)

storage = MemoryStorage()  # класс для хранения значений из ммашины состояний
dp = Dispatcher(bot, storage=storage)


class FSMStates(StatesGroup):
    first_name = State()
    last_name = State()
    patient_birthday = State()
    patient_id = State()
    speciality_id = State()
    clinic_id = State()
    doctor_id = State()
    selected_time = State()

    def patient_data(self):
        patient_data = {
            "patient_form-first_name": self.first_name,
            "patient_form-last_name": self.last_name,
            "patient_form-birthday": self.patient_birthday,
            "patient_form-clinic_id": '403'  # self.clinic_id
        }
        return patient_data


request_data = FSMStates()


@dp.message_handler(commands='start', state=None)
async def start(message: types.Message):
    await FSMStates.first_name.set()
    await message.answer('Введите имя пациента:')


# Функция для возможности отмены машины состояний
@dp.message_handler(state='*', commands='отмена')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_state_mashine(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('OK')


@dp.message_handler(state=FSMStates.first_name)
async def state1_func(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['first_name'] = message.text
    await FSMStates.next()
    await message.answer('Введите фамилию пациента:')


@dp.message_handler(state=FSMStates.last_name)
async def state2_func(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['last_name'] = message.text
    await state.reset_state(with_data=False)
    await message.answer(
        'Выберите дату рождения',
        reply_markup=await DialogCalendar().start_calendar()
    )


@dp.callback_query_handler(dialog_cal_callback.filter())
async def process_dialog_calendar(
    callback_query: types.CallbackQuery,
    callback_data: dict,
    state: FSMContext
):
    selected, date = await DialogCalendar().process_selection(
        callback_query, callback_data
    )
    if selected:
        await FSMStates.patient_birthday.set()  # Снова запускаю "state".
        await state.update_data(date=f'{date.strftime("%d.%m.%Y")}')
        await FSMStates.next()
        await callback_query.message.answer('Выберите специальность врача:')


# async def patient_id(message):
#     response = requests.post(
#         url=patient_check_url,
#         headers=headers,
#         data=request_data.patient_data(),
#         verify=False
#     )
#     try:
#         data = response.json().get('response').get('patient_id')
#     except AttributeError:
#         await message.answer(response.json().get('error'))
#         return None
#     return data

# @dp.callback_query_handler(state=FSMStates.patient_id)
@dp.message_handler(state=FSMStates.patient_id)
async def get_patient_id(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        response = requests.post(
            url=patient_check_url,
            headers=headers,
            data=request_data.patient_data(),
            verify=False
        )
        try:
            result = response.json().get('response').get('patient_id')
            await FSMStates.next()
        except AttributeError:
            await message.answer(response.json().get('error'))
            result = None
        data['patient_id'] = result
    # await message.answer('Введите фамилию пациента:')
    async with state.proxy() as data:
        await message.reply(str(data))




# # функция для сохранения фото, хранится ID фотки, сама фотка на серваке телеги
# # получаем последний ответ и закрываем машину состояний
# @dp.message_handler(content_types=['photo'], state=FSMStates.photo_data)
# async def photo_state_func(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['photo_data'] = message.photo[0].file_id
#     # await FSMStates.next()
#     # await message.reply('сюда можно закинуть фотку')


#     async with state.proxy() as data:
#         await message.reply(str(data))

#     await state.finish()



@dp.message_handler()
async def echo_send(message: types.Message):
    # await message.answer(message.text)
    # await message.reply(message.text)
    await bot.send_message(message.from_user.id, message.text)

executor.start_polling(dp, skip_updates=True)
