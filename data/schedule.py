import json
import os

from PIL import Image, ImageDraw, ImageFont

from config import SCHEDULE_JPG_EMPTY, PATH, FONT_REGULAR, FONT_BOLD, SCHEDULE_PNG_LEKCIY, SCHEDULE_PNG_LABA, SCHEDULE_PNG_PRACTIC
from db.database import scheduleToBD

opts = {
    1: "Понедельник",
    2: "Вторник",
    3: "Среда",
    4: "Четверг",
    5: "Пятница",
    6: "Суббота",
    8: "Понедельник",
    9: "Вторник",
    10: "Среда",
    11: "Четверг",
    12: "Пятница",
    13: "Суббота",
    15: "this",
    16: "next",
    "0": "week",
    "1": "monday",
    "2": "tuesday",
    "3": "wednesday",
    "4": "thursday",
    "5": "friday",
    "6": "saturday",
    "8": "monday",
    "9": "tuesday",
    "10": "wednesday",
    "11": "thursday",
    "12": "friday",
    "13": "saturday",
    "Понедельник": "monday",
    "Вторник": "tuesday",
    "Среда": "wednesday",
    "Четверг": "thursday",
    "Пятница": "friday",
    "Суббота": "saturday"
}


def makeSchedule(group, v=0):
    db_days = makeDay(group=group, v=v)
    makeWeek()
    db_OT = sortSchedule(db_days=db_days)
    buildingSchedule(db_one=db_OT[0], db_two=db_OT[1], group=group)
    return 'end'


def makeDay(group, v):
    db_days = []
    with open(PATH + f"data//pid//data_{group}.json", "r", encoding='utf-8') as file:
        data = json.load(file)
    for j in range(1, 3):
        for i in range(1, 7):
            try:
                db_days.append(toImage(date_day=opts[i], couple=data.get(f"{i}"), week="this", num=j))
            except Exception:
                db_days.append(None)
        for i in range(8, 14):
            n = i - v
            try:
                db_days.append(toImage(date_day=opts[n], couple=data.get(f"{n}"), week="next", num=j))
            except Exception:
                db_days.append(None)
    return db_days


def toImage(date_day, couple, week, num):
    m = 0
    for i in range(0, len(couple)):
        group = couple[i].get("group")
        w = couple[i].get('week')
        if (group[-1] == f'{num}' or group[-1] == ')') and (w == week or w == 'all'):
            m += 1

    textSize = 10
    colorViewPrimary = 'white'
    colorViewSecondary = '#b6b6b6'

    width = 1200
    height = 160
    if m != 0:
        schedule = Image.new("RGB", (width, height * (m + 1)), "white")
    else:
        schedule = Image.new("RGB", (0, 0), "white")

    font1Size = 40
    font2Size = 22
    font1 = ImageFont.truetype(FONT_BOLD, font1Size)
    font2 = ImageFont.truetype(FONT_REGULAR, font2Size)

    marginLeft = 104
    pencil = ImageDraw.Draw(schedule)
    pencil.text((marginLeft, 15), date_day, font=font1, fill="black", size=textSize)

    sizeP = 162
    lab = Image.open(SCHEDULE_PNG_LABA, 'r')
    lek = Image.open(SCHEDULE_PNG_LEKCIY, 'r')
    pra = Image.open(SCHEDULE_PNG_PRACTIC, 'r')

    paddingLeft1 = 50
    paddingLeft2 = 150
    paddingTop1 = 48
    paddingTop2 = 88
    start = 90
    z = 0
    try:
        for i in range(0, len(couple)):
            group = couple[i].get("group")
            w = couple[i].get('week')
            if (group[-1] == f'{num}' or group[-1] == ')') and (w == week or w == 'all'):
                interval = 10
                if z == 0:
                    interval = 30
                marginTop = start + z * sizeP + interval * z

                text = ''
                if couple[i].get('type') == 'практика' or couple[i].get('type') == "Практические семинарские занятия":
                    schedule.paste(pra, (marginLeft, marginTop), mask=pra)
                    text = '  Практика'
                if couple[i].get('type') == 'лекция' or couple[i].get('type') == "Лекция":
                    schedule.paste(lek, (marginLeft, marginTop), mask=lek)
                    text = '    Лекция'
                if couple[i].get('type') == 'лабораторная' or couple[i].get('type') == 'Лабораторная работа':
                    schedule.paste(lab, (marginLeft, marginTop), mask=lab)
                    text = 'Лаб.Работа'
                z += 1

                pencil.text((paddingLeft1 + marginLeft + 1, marginTop + paddingTop1 + 2), couple[i].get("time start"), font=font2, fill=colorViewSecondary)
                pencil.text((paddingLeft1 + marginLeft, marginTop + paddingTop1), couple[i].get("time start"), font=font2, fill=colorViewPrimary, size=textSize)

                pencil.text((paddingLeft1 + marginLeft + 1, marginTop + paddingTop2 + 2), couple[i].get("time end"), font=font2, fill=colorViewSecondary)
                pencil.text((paddingLeft1 + marginLeft, marginTop + paddingTop2), couple[i].get("time end"), font=font2, fill=colorViewPrimary, size=textSize)

                if len(couple[i].get("name")) > 40:
                    name = couple[i].get("name")[:40] + '...'
                else:
                    name = couple[i].get("name")
                pencil.text((paddingLeft2 + marginLeft + 1, marginTop + paddingTop1 + 2), name, font=font2, fill=colorViewSecondary)
                pencil.text((paddingLeft2 + marginLeft, marginTop + paddingTop1), name, font=font2, fill=colorViewPrimary, size=textSize)

                pencil.text((paddingLeft2 + marginLeft + 1, marginTop + paddingTop2 + 2), couple[i].get("teacher"), font=font2, fill=colorViewSecondary)
                pencil.text((paddingLeft2 + marginLeft, marginTop + paddingTop2), couple[i].get("teacher"), font=font2, fill=colorViewPrimary, size=textSize)

                g = marginLeft + len(text) * font2Size - font2Size
                if text == '    Лекция':
                    g -= font2Size
                pencil.text((schedule.size[0] - g + 1, marginTop + paddingTop1 + 2), text, font=font2, fill=colorViewSecondary)
                pencil.text((schedule.size[0] - g, marginTop + paddingTop1), text, font=font2, fill=colorViewPrimary, size=textSize)

                aud = couple[i].get("auditorium")
                if len(aud) > 6:
                    aud = ''
                g -= len(aud) * len(text) + len(text) + len(aud)
                if text == '    Лекция':
                    g += font2Size
                pencil.text((schedule.size[0] - g + 1, marginTop + paddingTop2 + 2), aud, font=font2, fill=colorViewSecondary)
                pencil.text((schedule.size[0] - g, marginTop + paddingTop2), aud, font=font2, fill=colorViewPrimary, size=textSize)
    except Exception as ex:
        print(ex)
    try:
        schedule.save(PATH + f"Schedule//{opts[date_day]}//Schedule_{opts[date_day]}_{week}_{num}.jpg")
        return [opts[date_day], week, num]
    except Exception as ex:
        print("toImage", ex)


def makeWeek():
    for i in range(15, 17):
        for j in range(1, 3):
            try:
                width = 0
                height = 0
                try:
                    img = Image.open(
                        PATH + f"//Schedule//monday//Schedule_monday_{opts[i]}_{j}.jpg")
                    width = img.size[0]
                    height += img.size[1]
                except Exception:
                    img = Image.open(SCHEDULE_JPG_EMPTY)
                try:
                    img1 = Image.open(
                        PATH + f"//Schedule//tuesday//Schedule_tuesday_{opts[i]}_{j}.jpg")
                    width = img1.size[0]
                    height += img1.size[1]
                except Exception:
                    img1 = Image.open(SCHEDULE_JPG_EMPTY)
                try:
                    img2 = Image.open(
                        PATH + f"//Schedule//wednesday//Schedule_wednesday_{opts[i]}_{j}.jpg")
                    width = img2.size[0]
                    height += img2.size[1]
                except Exception:
                    img2 = Image.open(SCHEDULE_JPG_EMPTY)
                try:
                    img3 = Image.open(
                        PATH + f"//Schedule//thursday//Schedule_thursday_{opts[i]}_{j}.jpg")
                    width = img3.size[0]
                    height += img3.size[1]
                except Exception:
                    img3 = Image.open(SCHEDULE_JPG_EMPTY)
                try:
                    img4 = Image.open(
                        PATH + f"//Schedule//friday//Schedule_friday_{opts[i]}_{j}.jpg")
                    width = img4.size[0]
                    height += img4.size[1]
                except Exception:
                    img4 = Image.open(SCHEDULE_JPG_EMPTY)
                try:
                    img5 = Image.open(
                        PATH + f"//Schedule//saturday//Schedule_saturday_{opts[i]}_{j}.jpg")
                    width = img5.size[0]
                    height += img5.size[1]
                except Exception:
                    img5 = Image.open(SCHEDULE_JPG_EMPTY)

                schedule = Image.new("RGB", (width, height), "white")
                schedule.paste(img, (0, 0))
                schedule.paste(img1, (0, img.size[1]))
                schedule.paste(img2, (0, img.size[1] + img1.size[1]))
                schedule.paste(img3, (0, img.size[1] + img1.size[1] + img2.size[1]))
                schedule.paste(img4, (0, img.size[1] + img1.size[1] + img2.size[1] + img3.size[1]))
                schedule.paste(img5, (0, img.size[1] + img1.size[1] + img2.size[1] + img3.size[1] + img4.size[1]))
                schedule.save(PATH + f"//Schedule//week//Schedule_{opts[i]}_{j}.jpg")
            except Exception as ex:
                print("makeWeek", ex)


def sortSchedule(db_days):
    db_one = []
    db_two = []
    for i in range(0, 24):
        if i < 12:
            if i == 0:
                db_one.append(['week', 'this', 1])
            elif i == 6:
                db_one.append(['week', 'next', 1])
            db_one.append(db_days[i])
        else:
            if i == 12:
                db_two.append(['week', 'this', 2])
            elif i == 18:
                db_two.append(['week', 'next', 2])
            db_two.append(db_days[i])
    return db_one, db_two


def buildingSchedule(db_one, db_two, group):
    one = []
    two = []
    oneT = []
    twoT = []
    for i in db_one:
        try:
            if i[0] == 'week':
                one.append(convertToBinaryData(PATH + f"Schedule//week//Schedule_{i[1]}_{i[2]}.jpg"))
                oneT.append(PATH + f"Schedule//week//Schedule_{i[1]}_{i[2]}.jpg")
            else:
                one.append(convertToBinaryData(PATH + f"Schedule//{i[0]}//Schedule_{i[0]}_{i[1]}_{i[2]}.jpg"))
                oneT.append(PATH + f"Schedule//{i[0]}//Schedule_{i[0]}_{i[1]}_{i[2]}.jpg")
        except Exception:
            one.append(None)
            oneT.append(None)
    for i in db_two:
        try:
            if i[0] == 'week':
                two.append(convertToBinaryData(PATH + f"Schedule//week//Schedule_{i[1]}_{i[2]}.jpg"))
                twoT.append(PATH + f"Schedule//week//Schedule_{i[1]}_{i[2]}.jpg")
            else:
                two.append(convertToBinaryData(PATH + f"Schedule//{i[0]}//Schedule_{i[0]}_{i[1]}_{i[2]}.jpg"))
                twoT.append(PATH + f"Schedule//{i[0]}//Schedule_{i[0]}_{i[1]}_{i[2]}.jpg")
        except Exception:
            two.append(None)
            twoT.append(None)
    scheduleToBD(scheduleId=group, schedule=one, num=1)
    scheduleToBD(scheduleId=group, schedule=two, num=2)
    for i in oneT:
        try:
            os.remove(i)
        except Exception:
            pass
    for i in twoT:
        try:
            os.remove(i)
        except Exception:
            pass


def convertToBinaryData(filename):
    with open(filename, 'rb') as file:
        blob_data = file.read()
    return blob_data
