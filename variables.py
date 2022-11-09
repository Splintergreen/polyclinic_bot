# from main import doctor_check


headers = {
    'Host': 'kuban-online.ru',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0',
    'Accept': '*/*',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'https://kuban-online.ru',
    'Referer': 'https://kuban-online.ru/signup/free/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
}

clinic_list_url = 'https://kuban-online.ru/api/clinic_list/'
patient_check_url = 'https://kuban-online.ru/api/check_patient/'
check_speciality_url = 'https://kuban-online.ru/api/speciality_list/'
doctor_check_url = 'https://kuban-online.ru/api/doctor_list/'
appointment_url = 'https://kuban-online.ru/api/appointment_list/'