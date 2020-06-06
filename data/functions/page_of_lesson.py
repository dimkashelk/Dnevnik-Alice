from datetime import datetime, timedelta


def lesson(req, sessionStorage, user_id, res):
    """Функция, отвечающая за формирование страницы урока, с основными данными"""
    number_lesson, date = 0, datetime.now()
    # пытаемся дату урока
    date_fl = False
    for i in req['request']['nlu']['entities']:
        if i['type'] == 'YANDEX.DATETIME':
            if i['value']['day_is_relative']:
                # урок на ближайшую даты
                date += timedelta(days=i['value']['day'])
            elif 'year_is_relative' in i['value'].keys():
                if not i['value']['year_is_relative']:
                    # урок в конкретную дату: год, месяц, день
                    date = datetime(year=i['value']['year'],
                                    month=i['value']['month'],
                                    day=i['value']['day'])
            elif not i['value']['month_is_relative']:
                # урок на конкретный месяц и дату
                date = datetime(year=date.year,
                                month=i['value']['month'],
                                day=i['value']['day'])
            date_fl = True
    # если в том, что сказал пользователь есть конкретная дата и номер урока,
    # то в алисе есть проблема, она не может различить число от даты,
    # поэтому приходится использовать дополнительную функцию
    number_lesson = get_number_lesson(date, req)
    if not number_lesson:
        # если не нашли номер, то выдаем сообщение об ошибке
        res['response']['text'] = 'Я вас не поняла :('
        res['response']['tts'] = 'я вас не поняла'
        return
    schedules = sessionStorage[user_id]['dnevnik'].get_schedules(
        sessionStorage[user_id]['person_id'],
        sessionStorage[user_id]['edu_group'],
        params={'startDate': (
            datetime(year=date.year,
                     month=date.month,
                     day=date.day,
                     hour=0,
                     minute=0,
                     second=0)),
            'endDate': (
                datetime(year=date.year,
                         month=date.month,
                         day=date.day,
                         hour=23,
                         minute=59,
                         second=59))}
    )
    if not date_fl:
        # Нужно для открытия конкретного урока после расписания на сегодня
        if not len(schedules['days'][0]['lessons']):
            res['response']['text'] = 'Уроков нет :('
            res['response']['tts'] = 'уроков нет'
            return
        fl = False
        for i in schedules['days'][0]['lessons']:
            if i['number'] == number_lesson:
                les = sessionStorage[user_id]['dnevnik'].get_lesson(i['id'])
                fl = True
                place = i['place']
        if not fl:
            res['response']['text'] = 'Такого урока нет :('
            res['response']['tts'] = 'такого урока нет'
            return
    else:
        # скорее всего пользователь хочет урок на конретную дату
        # (возможно и сегодня, но при поиске даты в первом цикле
        # сразу становится понятно на какую дату он просит)
        if len(schedules['days'][0]['lessons']):
            # берем из расписания конретный урок
            try:
                les = sessionStorage[user_id]['dnevnik'].get_lesson(
                    schedules['days'][0]['lessons'][number_lesson - 1]['id'])
            except IndexError:
                res['response']['text'] = 'Такого урока нет :('
                res['response']['tts'] = 'такого урока нет'
                return
        else:
            res['response']['text'] = 'Урок не доступен :('
            res['response']['tts'] = 'урок не доступен'
            return
        place = get_place_of_lesson(number_lesson, schedules)
    teachers = []
    for i in les['teachers']:
        person = sessionStorage[user_id]['dnevnik'].get_person(i)
        teachers.append(' '.join([person['lastName'],
                                  person['firstName'],
                                  person['middleName']]))
    homeworks = []
    for i in les['works']:
        if i['type'] == 'Homework':
            if i['text'].strip() not in homeworks:
                homeworks.append(i['text'].strip())
    year, month, day = map(int, les['date'].split('T')[0].split('-'))
    time = get_time_of_lesson(sessionStorage=sessionStorage,
                              user_id=user_id,
                              date=datetime(year=year,
                                            month=month,
                                            day=day),
                              number_lesson=number_lesson)
    res['response']['text'] = f"Время: {time}\n" \
        f"Кабинет: {place}\n" \
        f"Урок: {les['subject']['name']}\n" \
        f"{'Учителя' if len(teachers) > 1 else 'Учитель'}: {'; '.join(teachers)}\n" \
        f"Тема занятий: {les['title']}\n" \
        f"{'Домашние задания' if len(homeworks) > 1 else 'Домашнее задание'}: " \
        f"{'; '.join(homeworks)}"
    res['response']['tts'] = 'Страница урока'
    return


def get_time_of_lesson(sessionStorage, user_id, date, number_lesson):
    schedules = sessionStorage[user_id]['dnevnik'].get_schedules(
        sessionStorage[user_id]['person_id'],
        sessionStorage[user_id]['edu_group'],
        params={'startDate': (
            datetime(year=date.year,
                     month=date.month,
                     day=date.day,
                     hour=0,
                     minute=0,
                     second=0)),
            'endDate': (
                datetime(year=date.year,
                         month=date.month,
                         day=date.day,
                         hour=23,
                         minute=59,
                         second=59))}
    )
    if len(schedules['days'][0]['lessons']):
        return schedules['days'][0]['lessons'][number_lesson - 1]['hours']
    return False


def get_number_lesson(date, req):
    numbers, ans = [], 0
    for i in req['request']['nlu']['entities']:
        if i['type'] == 'YANDEX.NUMBER':
            numbers.append(i['value'])
    for i in numbers:
        if i != date.day and i != date.year:
            ans = i
    return ans


def get_place_of_lesson(number_lesson, schedules):
    for i in schedules['days'][0]['lessons']:
        if i['number'] == number_lesson:
            return i['place']
    return False
