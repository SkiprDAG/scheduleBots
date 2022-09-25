import json
import os

import requests
from bs4 import BeautifulSoup

from schedule import makeSchedule
from config import PATH
from db.database import createScheduleId

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.167 YaBrowser/22.7.4.957 Yowser/2.5 Safari/537.36'
}
proxies = {
    'https': 'http://kJW2MH:cGynUa@195.216.133.192:8000'
}
opts = {
    '8:15': '9:45',
    '10:00': '11:30',
    '11:45': '13:15',
    '13:45': '15:15',
    '15:30': '17:00',
    '17:10': '18:40',
    '18:45': '20:15',
    '20:20': '21:50'
}
opts1 = {
    'even': 'this',
    'Знаменатель': 'this',
    'odd': 'next',
    'Числитель': 'next',
    'all': 'all',
    '': 'all'
}
opts2 = {
    'even': 'next',
    'Знаменатель': 'next',
    'odd': 'this',
    'Числитель': 'this',
    'all': 'all',
    '': 'all'
}


def parsIrgups(link, pid):
    data = {
        'pid': pid,
    }
    try:
        session = requests.Session()
        response = session.get(link, data=data, proxies=proxies, headers=headers)
        html = BeautifulSoup(response.text, 'html.parser')

        d = {}
        i = 1
        for days in html.select('.panel-success'):
            day = html.find(class_='chisl').text.split(',')[-1].strip()
            d[f'{i}'] = []
            for couples in days.select('.panel-body > .row'):
                auditorium = couples.find(class_='col-md-1').text.strip()
                teacher = couples.find(class_='col-md-3').text.strip()
                time = couples.find(class_='col-md-2').contents
                name = couples.find(class_='col-md-5').contents[0].text.strip()
                typ = couples.find(class_='col-md-5').contents[2].text.replace('(', '').replace(')', '').strip()
                group = couples.find(class_='col-md-5').contents[4].text
                timeStart = time[1].text.replace('\n', '').replace(' ', '').split('-')[0]
                timeEnd = time[1].text.replace('\n', '').replace(' ', '').split('-')[1]
                week = time[3].text.strip()
                if day == 'числитель':
                    week = opts2[week]
                else:
                    week = opts1[week]
                d[f'{i}'].append(
                    {
                        "time start": timeStart,
                        "time end": timeEnd,
                        "type": typ,
                        "name": name,
                        "teacher": teacher,
                        "auditorium": auditorium,
                        "group": group,
                        "week": week
                    }
                )
            i += 1
        with open(PATH + f'data//pid//data_{pid}.json', 'w') as outfile:
            json.dump(d, outfile)
        return True
    except Exception as ex:
        print(ex)
        return False


def mainIrgups():
    with open(PATH + f'data//pid//pid.json', 'r', encoding="utf-8") as file:
        groups = json.load(file)
    for i in range(2823, 5052):
        if groups.get(f'{i}'):
            group = f"{groups.get(f'{i}')}".split("[{'group': '")[1].split("'")[0]
            pid = f"{groups.get(f'{i}')}".split("'pid': ")[1].split("}")[0]
            link = f"https://www.irgups.ru/eis/rasp/index.php?action=student&pid={pid}"
            r = parsIrgups(link=link, pid=pid)
            if r:
                createScheduleId([group, pid])
                makeSchedule(pid)
                os.remove(PATH + f"data//pid//data_{pid}.json")
    return 'end pars'


def parsIrnitu(link, pid):
    try:
        session = requests.Session()
        response = session.get(link, proxies=proxies, headers=headers)
        html = BeautifulSoup(response.text, 'html.parser')

        d = {}
        i = 1
        for days in html.select('.content '):
            if f'{days}'.split('<p>')[1].split('<')[0] != 'Нет расписания на выбранную дату':
                data = days.find(class_='alert alert-info').contents
                day = data[5].text.split(' ')[1]
                group = data[3].text.split(' ')[1]
                for couples in days.select('.class-lines'):
                    d[f'{i}'] = []
                    for couple in couples.select('.class-line-item'):
                        for coup in couple.select('.class-tail'):
                            week = f'{coup}'.split('class-tail class-')[1].split('-')[0]
                            if coup.text != 'свободно':
                                auditorium = coup.find(class_='class-aud').text
                                time = couple.find(class_='class-time').text
                                info = coup.find_all(class_='class-info')
                                typ = info[0].text.split(' ')[0]
                                try:
                                    teacher = info[0].text.split(' ')[1:]
                                    teacher = teacher[0] + ' ' + teacher[1]
                                except Exception:
                                    teacher = ''
                                name = coup.find(class_='class-pred').text
                                if info[1].text.find('подгруппа') > 0:
                                    num = info[1].text.split(' ')[2]
                                else:
                                    num = ')'
                                if name.split(' ')[0] == "Проект":
                                    name = 'Проект'
                                    typ = 'Проект'
                                    auditorium = 'Смотрите в расписание проектов'
                                if name != 'Проект':
                                    if day == 'четная':
                                        week = opts2[week]
                                    else:
                                        week = opts1[week]
                                    d[f'{i}'].append(
                                        {
                                            "time start": time,
                                            "time end": opts[time],
                                            "type": typ,
                                            "name": name,
                                            "teacher": teacher,
                                            "auditorium": auditorium,
                                            "group": group + '-' + num,
                                            "week": week
                                        }
                                    )
                    i += 1
                with open(PATH + f'data//pid//data_{pid}.json', 'w') as outfile:
                    json.dump(d, outfile)
                return True
    except Exception as ex:
        print('response', ex)
        return False


def mainIrnitu():
    for j in range(0, 10):
        with open(PATH + f'data//pid//pid{j}.json', 'r') as file:
            groups = json.load(file)
        for i in groups:
            if groups.get(f'{i}'):
                group = f"{groups.get(f'{i}')}".split("[{'group': '")[1].split("'")[0]
                pid = f"{groups.get(f'{i}')}".split("'pid': '")[1].split("'}")[0]
                link = f"https://www.istu.edu/schedule/?group={pid}"
                r = parsIrnitu(link=link, pid=pid)
                if r:
                    createScheduleId([group, pid])
                    makeSchedule(pid, 7)
                    os.remove(PATH + f"data//pid//data_{pid}.json")
    return 'end pars'


if __name__ == "__main__":
    mainIrgups()
    # mainIrnitu()
