from datetime import datetime, timedelta
from .subjects import *


def new_marks(sessionStorage, user_id, subject, res):
    """Последние выставленные оценки"""
    marks = sessionStorage[user_id]['dnevnik'].get_last_marks(
        person_id=sessionStorage[user_id]['person_id'],
        group_id=sessionStorage[user_id]['edu_group']
    )['marks']
    dop = {}
    if subject is None:
        # нет конкретного предмета
        for i in marks:
            if i['lesson'] is None:
                continue
            else:
                if datetime.now().strftime('%Y-%m-%d') in i['date']:
                    dop_subject = sessionStorage[user_id]['id-subject'][i['lesson']]
                    if dop.get(dop_subject, False):
                        dop[dop_subject].append(i['value'])
                    else:
                        dop[dop_subject] = [i['value']]
    else:
        # оценки по конкретному предмету
        for i in marks:
            if i['lesson'] is None:
                continue
            else:
                if datetime.now().strftime('%Y-%m-%d') in i['date']:
                    dop_subject = sessionStorage[user_id]['id-subject'][i['lesson']]
                    if not check_subjects(dop_subject, subject):
                        continue
                    if dop.get(dop_subject, False):
                        dop[dop_subject].append(i['value'])
                    else:
                        dop[dop_subject] = [i['value']]
    if len(dop.keys()):
        res['response']['text'] = 'Ваши оценки:\n'
        res['response']['tts'] = 'Ваши оценки'
        for i in dop.keys():
            res['response']['text'] += f'{i.capitalize()} - {", ".join(dop[i])}\n'
        return
    else:
        res['response']['text'] = 'За сегодня ничего не поставили :('
        res['response']['tts'] = 'За сегодня ничего не поставили'
        return


def get_marks(sessionStorage, user_id, subject, res, year=None, month=None, day=None, days=None):
    """Основная функция получения оценок на конкретную дату"""
    if year is not None:
        marks = sessionStorage[user_id]['dnevnik'].get_marks_from_to(
            person_id=sessionStorage[user_id]['person_id'],
            school_id=sessionStorage[user_id]['school_id'],
            from_time=datetime(year=year,
                               month=month,
                               day=day,
                               hour=0,
                               minute=0,
                               second=0),
            to_time=datetime(year=year,
                             month=month,
                             day=day,
                             hour=23,
                             minute=59,
                             second=59)
        )
    elif month is not None:
        year = datetime.now().year
        marks = sessionStorage[user_id]['dnevnik'].get_marks_from_to(
            person_id=sessionStorage[user_id]['person_id'],
            school_id=sessionStorage[user_id]['school_id'],
            from_time=datetime(year=year,
                               month=month,
                               day=day,
                               hour=0,
                               minute=0,
                               second=0),
            to_time=datetime(year=year,
                             month=month,
                             day=day,
                             hour=23,
                             minute=59,
                             second=59)
        )
    elif day is not None:
        year = datetime.now().year
        month = datetime.now().month
        marks = sessionStorage[user_id]['dnevnik'].get_marks_from_to(
            person_id=sessionStorage[user_id]['person_id'],
            school_id=sessionStorage[user_id]['school_id'],
            from_time=datetime(year=year,
                               month=month,
                               day=day,
                               hour=0,
                               minute=0,
                               second=0),
            to_time=datetime(year=year,
                             month=month,
                             day=day,
                             hour=23,
                             minute=59,
                             second=59)
        )
    else:
        year = datetime.now().year
        month = datetime.now().month
        marks = sessionStorage[user_id]['dnevnik'].get_marks_from_to(
            person_id=sessionStorage[user_id]['person_id'],
            school_id=sessionStorage[user_id]['school_id'],
            from_time=datetime(year=year,
                               month=month,
                               day=day,
                               hour=0,
                               minute=0,
                               second=0) + timedelta(days=days),
            to_time=datetime(year=year,
                             month=month,
                             day=day,
                             hour=23,
                             minute=59,
                             second=59) + timedelta(days=days)
        )
    if len(marks):
        dop = {}
        if subject is None:
            # предмет не выбран
            for j in marks:
                lesson = sessionStorage[user_id]['dnevnik'].get_lesson(
                    j['lesson'])['subject']['name']
                if dop.get(lesson, False):
                    dop[lesson].append(j['value'])
                else:
                    dop[lesson] = [j['value']]
        else:
            # предмет выбран
            for j in marks:
                lesson = sessionStorage[user_id]['dnevnik'].get_lesson(
                    j['lesson'])['subject']['name']
                if check_subjects(lesson, subject):
                    if dop.get(lesson, False):
                        dop[lesson].append(j['value'])
                    else:
                        dop[lesson] = [j['value']]
        res['response']['text'] = 'Ваши оценки:\n'
        for j in dop.keys():
            res['response'][
                'text'] += f'{j.capitalize()} - {", ".join(dop[j])}\n'
        res['response']['tts'] = 'ваши оценки'
        return
    else:
        res['response']['text'] = 'Оценок нет :('
        res['response']['tts'] = 'оценок нет'
        return


def old_marks(req, sessionStorage, user_id, subject, res):
    """Получение оценок на конкретную дату"""
    for i in req['request']['nlu']['entities']:
        if i['type'] == 'YANDEX.DATETIME':
            if 'year_is_relative' in i['value'].keys():
                if not i['value']['year_is_relative']:
                    if 'month' in i['value'].keys() and 'day' in i['value'].keys():
                        get_marks(sessionStorage=sessionStorage,
                                  user_id=user_id,
                                  subject=subject,
                                  res=res,
                                  year=i['value']['year'],
                                  month=i['value']['month'],
                                  day=i['value']['day'])
                        return
                    else:
                        res['response']['text'] = 'Оценок нет :('
                        res['response']['tts'] = 'оценок нет'
                        return
            elif 'month_is_relative' in i['value'].keys():
                if not i['value']['month_is_relative']:
                    get_marks(sessionStorage=sessionStorage,
                              user_id=user_id,
                              subject=subject,
                              res=res,
                              month=i['value']['month'],
                              day=i['value']['day'])
                    return
            else:
                if not i['value']['day_is_relative']:
                    get_marks(sessionStorage=sessionStorage,
                              user_id=user_id,
                              subject=subject,
                              res=res,
                              day=i['value']['day'])
                    return
                elif i['value']['day_is_relative']:
                    get_marks(sessionStorage=sessionStorage,
                              user_id=user_id,
                              subject=subject,
                              res=res,
                              days=i['value']['day'])
                    return
    res['response']['text'] = 'Я вас не поняла :('
    res['response']['tts'] = 'я вас не поняла'
    return


def final_marks(req, sessionStorage, user_id, subject, res):
    """Финальные оценки"""
    final = sessionStorage['user_id']['dnevnik'].get_person_final_marks(
        person_id=sessionStorage['user_id']['person_id'],
        group_id=sessionStorage['user_id']['group_id']
    )


def marks(req, sessionStorage, user_id, res):
    """Оценки"""
    subject = get_subject(req['request']['original_utterance'].lower())
    if any(i in req['request']['original_utterance'].lower()
           for i in ['новые', 'последние']):
        # последние поставленные оценки
        new_marks(sessionStorage=sessionStorage, user_id=user_id, subject=subject, res=res)
        return

    # выставвленные оценки
    old_marks(req=req, sessionStorage=sessionStorage, user_id=user_id, subject=subject, res=res)
    return
