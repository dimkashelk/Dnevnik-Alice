from datetime import datetime, timedelta
from .phrases import *
from dnevnik import DnevnikAPI
from session import Session


def get_schedule(sessionStorage: Session, user_id, res, year=None, month=None, day=None):
    """Получение расписания на дату"""
    user = sessionStorage.get_user(user_id)
    dn = DnevnikAPI(token=user.token)
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
    schedules = dn.get_schedules(
        user.person_id,
        user.edu_group,
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
        res['response']['text'] = res['response']['tts'] = get_random_phrases('schedule')
        for j in schedules['days'][0]['lessons']:
            dop = dn.get_lesson(j['id'])
            res['response']['text'] += j['number'] + ' ' + j['hours'] + ' ' + dop['subject']['name'] + '\n'
        return
    else:
        res['response']['text'] = res['response']['tts'] = get_random_phrases('schedule_is_not_available')
        return


def schedule(sessionStorage: Session, req, user_id, res):
    """Расписание"""
    try:
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
    except Exception:
        pass
    res['response']['text'] = res['response']['tts'] = get_random_phrases('not_understand')
    return
