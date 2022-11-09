import requests
from pprint import pprint
from variables import headers, patient_check_url, check_speciality_url, doctor_check_url, appointment_url
from data import RequestData
from dataclasses import asdict
from datetime import date, datetime
import os
import telebot
from telegram_bot_calendar import DetailedTelegramCalendar, WMonthTelegramCalendar
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

your_translation_months = list('abcdefghijkl')
your_translation_days_of_week = list('yourtra')

class MyTranslationCalendar(WMonthTelegramCalendar):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.days_of_week['yourtransl'] = your_translation_days_of_week
        self.months['yourtransl'] = your_translation_months
from dotenv import load_dotenv 

load_dotenv()
LSTEP = {'y': 'год', 'm': 'месяц', 'd': 'день'}
secret_token = os.getenv('TOKEN')
bot = telebot.TeleBot(secret_token)
request_data = RequestData()


@bot.message_handler(content_types=['text'])
def start(message):
    rep_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    start_button = KeyboardButton('/start')
    rep_keyboard.add(start_button)
    bot.send_message(message.from_user.id, "Вас приветствует бот записи на прием в поликлинику.", reply_markup=rep_keyboard)

    if message.text == '/start':
        bot.send_message(message.from_user.id, "Введите имя?")
        bot.register_next_step_handler(message, get_first_name); 
    else:
        bot.send_message(message.from_user.id, 'Напиши /start')
    # bot.delete_message(message.from_user.id, message.message_id)

def get_first_name(message):
    request_data.first_name = message.text
    bot.send_message(message.from_user.id, 'Введите фамилию?')
    bot.register_next_step_handler(message, get_last_name)

def get_last_name(message):
    request_data.last_name = message.text
    get_age(message)


def get_age(message):
    calendar, step = DetailedTelegramCalendar(calendar_id=1, locale='ru', max_date=date.today()).build()
    bot.send_message(message.chat.id,
                     f"Выберите {LSTEP[step]} рождения",
                     reply_markup=calendar)

@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def cal(c):
    birthday, key, step = DetailedTelegramCalendar(calendar_id=1, locale='ru', max_date=date.today()).process(c.data)
    if not birthday and key:
        bot.edit_message_text(f"Выберите {LSTEP[step]} рождения",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif birthday:
        request_data.patient_birthday = birthday
        patient_check(message = c.message.chat.id)

@bot.callback_query_handler(func=MyTranslationCalendar.func(calendar_id=2))
def cal_date(c):
    # min_date = datetime.strptime('20221004', "%Y%m%d").date()
    time, key, step = MyTranslationCalendar(calendar_id=2, locale='ru').process(c.data)
    if not time and key:
        bot.edit_message_text(f"Выберите {LSTEP['d']} записи",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif time:
        request_data.selected_time = time

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data.startswith('speciality_id_'):
        doctor_check(call)
    elif call.data.startswith('doc_id_'):
        appointment_check(call)

def patient_check(message):
    response = requests.post(
        url=patient_check_url,
        headers=headers,
        data=request_data.patient_data(),
        verify=False
    )
    request_data.patient_id = response.json().get('response').get('patient_id')
    check_speciality(message)

#Выбор специальности врача
def check_speciality(message):
    response = requests.post(
        url=check_speciality_url,
        headers=headers,
        data=request_data.speciality_data(),
        verify=False
    )
    keyboard = InlineKeyboardMarkup()
    speciality_list = response.json().get('response')
    for speciality in speciality_list:
        name = speciality.get('NameSpesiality')
        numbers = speciality.get('CountFreeParticipantIE')
        speciality_id = str(speciality.get('IdSpesiality'))
        key = InlineKeyboardButton(text=f'{name}>> номерков >> {numbers}'.title(), callback_data=f'speciality_id_{speciality_id}')
        keyboard.add(key)
    bot.send_message(message, text='Выберите специальность врача', reply_markup=keyboard)


# Выберите врача с вашего участка
def doctor_check(call):
    request_data.speciality_id = call.data.split('_id_')[-1]
    response = requests.post(
        url=doctor_check_url,
        headers=headers,
        data=request_data.doctor_data(),
        verify=False
    )
    keyboard_doc = InlineKeyboardMarkup()
    doctor_list = response.json().get('response')
    for doctor in doctor_list:
        name = doctor.get('Name')
        doc_id = str(doctor.get('IdDoc'))
        # aria_num = doctor.get('AriaNumber')
        # free_num = doctor.get('CountFreeTicket')
        key = InlineKeyboardButton(text=f'{name.split(" (")[0]}', callback_data=f'doc_id_{doc_id}')
        keyboard_doc.add(key)
    bot.send_message(call.message.chat.id, text='Выберите фамилию врача', reply_markup=keyboard_doc)

# Время приема
def appointment_check(call):
    request_data.doctor_id = call.data.split('_id_')[-1]
    response = requests.post(
        url=appointment_url,
        headers=headers,
        data=request_data.appointment_data(),
        verify=False
    )
    appointment_list = response.json().get('response')
    # pprint(appointment_list)
    date_list = []
    # for appoint in appointment_list:
    #     date_list.append(datetime.strptime(str(appoint).replace('-', ''), "%Y%m%d").date() )
    # min_date = date_list[0]#datetime.strptime('20221004', "%Y%m%d").date()
    # max_date = date_list[-1]
    calendar, step = MyTranslationCalendar(calendar_id=2, locale='ru').build()
    bot.send_message(call.message.chat.id,
                     f"Выберите {LSTEP['d']} записи",
                     reply_markup=calendar)

# Выберите дату записи
# date_list = []
# for date in appointment_list:
#     print(f"Доступная дата записи - {date}")
#     date_list.append(date)
# date_input = input('Выберите и введите дату: ==> ')
# for date in date_list:
#     if date == date_input:
#         print('Доступное время для записи:')
#         for time in appointment_list.get(date):
#             appointment_time = time.get('date_start')
#             print(appointment_time.get('time'))


def main():
    bot.polling(none_stop=True)
    # while True:


if __name__ == '__main__':
    main()
