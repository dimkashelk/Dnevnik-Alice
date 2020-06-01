from datetime import datetime, timedelta


def get_schedule(sessionStorage, user_id, res, year=None, month=None, day=None):
    if year is None and month is None:
        date = datetime.now() + timedelta(days=day)
    elif year is None and month is not None:
        date = datetime(year=datetime.now().year,
                        month=month,
                        day=day)
    else:
        date = datetime(year=year,
                        month=month,
                        day=day)
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
        res['response']['text'] = 'Ваше расписание:\n'
        for j in schedules['days'][0]['lessons']:
            dop = sessionStorage[user_id]['dnevnik'].get_lesson(j['id'])
            res['response']['text'] += j['hours'] + ' ' + dop['subject']['name'] + '\n'
        res['response']['tts'] = 'ваше расписание'
        return
    else:
        res['response']['text'] = 'Расписание не доступно'
        res['response']['tts'] = 'Расписание не доступно'
        return


def schedule(sessionStorage, req, user_id, res):
    for i in req['request']['nlu']['entities']:
        if i['type'] == 'YANDEX.DATETIME':
            if i['value']['day_is_relative']:
                get_schedule(sessionStorage=sessionStorage,
                             user_id=user_id,
                             res=res,
                             day=i['value']['day'])
                return
            elif not i['value']['month_is_relative']:
                get_schedule(sessionStorage=sessionStorage,
                             user_id=user_id,
                             res=res,
                             day=i['value']['day'],
                             month=i['value']['month'])
                return
            elif not i['value']['year_is_relative']:
                get_schedule(sessionStorage=sessionStorage,
                             user_id=user_id,
                             res=res,
                             day=i['value']['day'],
                             month=i['value']['month'],
                             year=i['value']['year'])
                return
    res['response']['text'] = 'Я вас не поняла :('
    res['response']['tts'] = 'я вас не поняла'
    return
