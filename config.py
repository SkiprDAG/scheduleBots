import os
import pytz
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

TOKEN_VK = str(os.getenv('TOKEN_VK'))
GROUP_VK = str(os.getenv('GROUP_VK'))
TOKEN_DISCORD = str(os.getenv('TOKEN_DISCORD'))
TOKEN_TELEGRAM = str(os.getenv('TOKEN_TELEGRAM'))
USER_ID_VK = str(os.getenv('USER_ID_VK'))
USER_ID_T = str(os.getenv('USER_ID_T'))

PATH = 'PATH//Schedule//ScheduleBots//'
DB_PATH = 'PATH//Schedule//ScheduleBots//db//database.db'
SCHEDULE_JPG_DAY = 'PATH//Schedule//ScheduleBots//Schedule//day.jpg'
SCHEDULE_JPG_EMPTY = 'PATH//Schedule//ScheduleBots//Schedule//empty.jpg'
SCHEDULE_PNG_LABA = 'PATH//Schedule//ScheduleBots//Schedule//Property_1=Laba.png'
SCHEDULE_PNG_LEKCIY = 'PATH//Schedule//ScheduleBots//Schedule//Property_1=Lekciy.png'
SCHEDULE_PNG_PRACTIC = 'PATH//Schedule//ScheduleBots//Schedule//Property_1=Practic.png'
FONT_BOLD = 'PATH//Schedule//ScheduleBots///Schedule//font//MONTSERRAT_BOLD.ttf'
FONT_REGULAR = 'PATH//Schedule//ScheduleBots//Schedule//font//MONTSERRAT_REGULAR.ttf'

admin_id = [
    USER_ID_VK
]

MSG_HELLO_VK = "Приветствую вас! Введите полное название вашей группы:" \
               "\nМожно посмотреть в личном кабинете или на сайте ИрГУПСа" \
               "\n(@softenginebot 'аббревиатура.1-год-группа(форма обучения)-подгруппа')" \
               "\nПример: @softenginebot ПИ.1-20-1(И,О)-2"
MSG_HELLO_T = "Приветствую вас! Введите полное название вашей группы:" \
              "\nМожно посмотреть в личном кабинете или на сайте ИрГУПСа" \
              "\n('аббревиатура.1-год-группа(форма обучения)-подгруппа')" \
              "\nПример: ПИ.1-20-1(И,О)-2"
GROUP_NOT_FOUND = ''
MSG_CHECK_BUTTON = 'снизу появились кнопки \nдумаю по их название и так всё понятно...'
THIS_SUNDAY = 'ты кого хочешь ное... ты думаешь мы дол...\nСегодня воскресенье'
NEXT_SUNDAY = 'ты кого хочешь ное... ты думаешь мы дол...\nЗавтра воскресенье'
EXCEPTION = 'неудача'
CHECK = 'проверка...'
CANCEL = 'Данные внесены'

opts = {
    1: "monday",
    2: "tuesday",
    3: "wednesday",
    4: "thursday",
    5: "friday",
    6: "saturday"
}


def dayWeek(msg):
    i = 1
    if msg[0] == 'Next':
        i = 2
    week = 'this'
    tz = pytz.timezone('Etc/GMT-8')
    day = datetime.now().astimezone(tz).weekday() + i
    if day > 7:
        day = 1
        week = 'next'
    try:
        m = [opts[day], week]
    except Exception:
        m = day
    return m


def sunday(msg, day):
    if day == 7:
        if msg[0] == 'Next':
            return NEXT_SUNDAY
        elif msg[0] == 'This':
            return THIS_SUNDAY
    else:
        return EXCEPTION
