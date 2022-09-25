import sqlite3
from config import DB_PATH, SCHEDULE_JPG_DAY


def create(groupChatId, scheduleId, userId):
    try:
        db = sqlite3.connect(DB_PATH)
        cursor = db.cursor()

        group = scheduleId[:-2]
        cursor.execute(f"""SELECT id FROM schedulesId WHERE id = '{group}'""")
        if cursor.fetchone() is None:
            return True, 0

        cursor.execute("""CREATE TABLE IF NOT EXISTS groupChats(
                id INTEGER,
                scheduleId INTEGER
        )""")
        db.commit()

        cursor.execute(f"""SELECT id FROM groupChats WHERE id = '{groupChatId}'""")
        if cursor.fetchone() is None:
            cursor.execute(f"""INSERT INTO groupChats(id, scheduleId) VALUES('{groupChatId}', '{scheduleId}')""")
            db.commit()
        else:
            cursor.execute(
                f"""SELECT scheduleId FROM groupChats WHERE id = '{groupChatId}' AND scheduleId = '{scheduleId}'""")
            if cursor.fetchone() is None:
                cursor.execute(f"""UPDATE groupChats SET scheduleId = '{scheduleId}' WHERE id = '{groupChatId}'""")
                db.commit()
            else:
                return False, 'такая запись уже существуют'

        cursor.execute("""CREATE TABLE IF NOT EXISTS groupUsers(
                                        id INTEGER,
                                        userId INTEGER
                                )""")
        db.commit()

        cursor.execute(f"""SELECT id FROM groupUsers WHERE id = '{groupChatId}'""")
        if cursor.fetchone() is None:
            cursor.execute(
                f"""INSERT INTO groupUsers(id, userId) VALUES({groupChatId}, {userId})""")
            db.commit()
        else:
            cursor.execute(f"""SELECT userId FROM groupUsers WHERE userId = '{userId}'""")
            if cursor.fetchone() is None:
                cursor.execute(
                    f"""INSERT INTO groupUsers(id, userId) VALUES({groupChatId}, {userId})""")
                db.commit()

        # cursor.execute("""CREATE TABLE IF NOT EXISTS user(
        #                                     id INTEGER,
        #                                     name TEXT,
        #                                     phone TEXT,
        #                                     git TEXT
        #                             )""")
        # db.commit()
        #
        # cursor.execute(f"""SELECT id FROM user WHERE id = '{userId}'""")
        # if cursor.fetchone() is None:
        #     cursor.execute(
        #         f"""INSERT INTO user(id, name, phone, git) VALUES({userId}, '{name}', '0', '0')""")
        #     db.commit()

        db.close()
        return False, 'данные внесены'
    except Exception as ex:
        print("create", ex)
        return 'неудача'


def regUserToDB(userId, data, typ):
    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()

    try:
        cursor.execute(f"""SELECT id FROM user WHERE id = '{userId}'""")
        if cursor.fetchone() is None:
            return 'неудача'
        else:
            if typ == 'Phone':
                cursor.execute(f"""UPDATE user SET {typ} = {data} WHERE id = {userId}""")
                db.commit()

        response = ''
        for n in cursor.execute(f"""SELECT name, {typ} FROM user WHERE id = '{userId}'"""):
            response = f'{n[0]}: {n[1]}'
        db.close()
        return response
    except Exception as ex:
        print(ex)
        return 'неудача'


def postUserToDB(userId, name):
    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()

    cursor.execute(f"""SELECT id FROM user WHERE id = '{userId}'""")
    if cursor.fetchone() is None:
        cursor.execute(
            f"""INSERT INTO user(id, name, phone, git) VALUES({userId}, '{name}', '0', '0')""")
        db.commit()

    db.close()


def info(groupChatId, typ):
    try:
        db = sqlite3.connect(DB_PATH)
        cursor = db.cursor()

        data = []
        users = []
        for user in cursor.execute(f"""SELECT userId FROM groupUsers WHERE id = '{groupChatId}'"""):
            users.append(user[0])

        for user in users:
            for n in cursor.execute(f"""SELECT name, {typ} FROM user WHERE id = '{user}'"""):
                if n[1] != '0':
                    data.append([n[0], n[1]])
                else:
                    data.append([n[0], None])

        db.close()
        return data
    except Exception as ex:
        print("info", ex)


def scheduleToBD(scheduleId, schedule, num):
    week = schedule[0]
    monday = schedule[1]
    tuesday = schedule[2]
    wednesday = schedule[3]
    thursday = schedule[4]
    friday = schedule[5]
    saturday = schedule[6]
    text = 'this'

    try:
        db = sqlite3.connect(DB_PATH)
        cursor = db.cursor()

        cursor.execute("""CREATE TABLE IF NOT EXISTS schedule(
                                                id TEXT,
                                                week BLOB,
                                                monday BLOB,
                                                tuesday BLOB,
                                                wednesday BLOB,
                                                thursday BLOB,
                                                friday BLOB,
                                                saturday BLOB
                                        )""")
        db.commit()
        for i in range(0, 2):
            if i == 1:
                week = schedule[7]
                monday = schedule[8]
                tuesday = schedule[9]
                wednesday = schedule[10]
                thursday = schedule[11]
                friday = schedule[12]
                saturday = schedule[13]
                text = 'next'

            cursor.execute(f"""SELECT id FROM schedule WHERE id = '{scheduleId}-{num}-{text}'""")
            if cursor.fetchone() is None:
                cursor.execute(f"""INSERT INTO schedule(
                    id, week, monday, tuesday, wednesday, thursday, friday, saturday
                ) VALUES(?, ?, ?, ?, ?, ?, ?, ?)""", (
                    f'{scheduleId}-{num}-{text}', week, monday, tuesday, wednesday, thursday, friday, saturday))
                db.commit()
            else:
                cursor.execute(f"""UPDATE schedule SET
                                    week = ?, 
                                    monday = ?, 
                                    tuesday = ?, 
                                    wednesday = ?, 
                                    thursday = ?, 
                                    friday = ?, 
                                    saturday = ?
                WHERE id = '{scheduleId}-{num}-{text}'""",
                               (week, monday, tuesday, wednesday, thursday, friday, saturday))
                db.commit()

        db.close()
    except Exception as ex:
        print("schedule", ex)


def getDay(groupChatId, day, week='this'):
    try:
        db = sqlite3.connect(DB_PATH)
        cursor = db.cursor()

        scheduleId = ''
        for groupId in cursor.execute(f"""SELECT scheduleId FROM groupChats WHERE id = '{groupChatId}'"""):
            scheduleId = groupId[0]

        groupFirst = scheduleId[:-2]
        groupLast = scheduleId[-1:]
        if scheduleId[-1:] == ')':
            groupLast = 1
            groupFirst = scheduleId
        pid = ''
        for pidId in cursor.execute(f"""SELECT scheduleId FROM schedulesId WHERE id = ?""", (f'{groupFirst}',)):
            pid = pidId[0]

        if pid is not None:
            for n in cursor.execute(f"""SELECT {day} FROM schedule WHERE id = ?""", (f'{pid}-{groupLast}-{week}',)):
                writeToFile(n[0], SCHEDULE_JPG_DAY)
                return SCHEDULE_JPG_DAY

        db.close()
    except Exception as ex:
        print("getDay", ex)


def writeToFile(data, filename):
    with open(filename, 'wb') as file:
        file.write(data)


def createScheduleId(group):
    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS schedulesId(
                    id INTEGER,
                    scheduleId TEXT
            )""")
    db.commit()

    cursor.execute(f"""SELECT id FROM schedulesId WHERE id = '{group[0].upper()}'""")
    if cursor.fetchone() is None:
        cursor.execute(f"""INSERT INTO schedulesId(id, scheduleId) VALUES('{group[0].upper()}', '{group[1]}')""")
        db.commit()
    else:
        cursor.execute(f"""SELECT scheduleId FROM schedulesId WHERE scheduleId = '{group[1]}'""")
        if cursor.fetchone() is None:
            cursor.execute(f"""UPDATE schedulesId SET scheduleId = '{group[1]}'""")
            db.commit()
    db.close()


def checkGroup(group):
    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()

    cursor.execute(f"""SELECT id FROM groupChats WHERE id = '{group}'""")
    if cursor.fetchone() is None:
        return False
    else:
        return True
