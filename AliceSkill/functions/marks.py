from datetime import datetime, timedelta
from AliceSkill.dnevnik import DnevnikAPI
from AliceSkill.session import Session
from .subjects import *
from .phrases import *


def new_marks(sessionStorage: Session, user_id, subject, res):
    """Последние выставленные оценки"""
    user = sessionStorage.get_user(user_id)
    dn = DnevnikAPI(token=user.token)
    last_marks = dn.get_last_marks(
        person_id=user.person_id,
        group_id=user.edu_group
    )
    marks = last_marks['marks']
    dop = {}
    if subject is None:
        # нет конкретного предмета
        for i in marks:
            if i['lesson'] is None:
                continue
            else:
                if datetime.now().strftime('%Y-%m-%d') in i['date']:
                    dop_subject = dn.get_lesson(i['lesson'])['subject']['name']
                    if dop.get(dop_subject, False):
                        dop[dop_subject].append(i['value'])
                    else:
                        dop[dop_subject] = [i['value']]
            if datetime.now().strftime('%Y-%m-%d') not in i['date']:
                break
    else:
        # оценки по конкретному предмету
        for i in marks:
            if i['lesson'] is None:
                continue
            else:
                if datetime.now().strftime('%Y-%m-%d') in i['date']:
                    dop_subject = dn.get_lesson(i['lesson'])['subject']['name']
                    if not check_subjects(dop_subject, subject):
                        continue
                    if dop.get(dop_subject, False):
                        dop[dop_subject].append(i['value'])
                    else:
                        dop[dop_subject] = [i['value']]
            if datetime.now().strftime('%Y-%m-%d') not in i['date']:
                break
    if len(dop.keys()):
        res['response']['text'] = res['response']['tts'] = get_random_phrases('new_marks')
        for i in dop.keys():
            res['response']['text'] += f'{i.capitalize()} - {", ".join(dop[i])}\n'
        return
    else:
        res['response']['text'] = res['response']['tts'] = get_random_phrases('nothing_is_exposed')
        return


def get_marks(sessionStorage: Session, user_id, subject, res, year=None, month=None, day=None, days=None):
    """Основная функция получения оценок на конкретную дату"""
    user = sessionStorage.get_user(user_id)
    dn = DnevnikAPI(token=user.token)
    if year is not None:
        marks = dn.get_marks_from_to(
            person_id=user.person_id,
            school_id=user.school_id,
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
        marks = dn.get_marks_from_to(
            person_id=user.person_id,
            school_id=user.school_id,
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
        marks = dn.get_marks_from_to(
            person_id=user.person_id,
            school_id=user.school_id,
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
        marks = dn.get_marks_from_to(
            person_id=user.person_id,
            school_id=user.school_id,
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
                lesson = dn.get_lesson(j['lesson'])['subject']['name']
                if dop.get(lesson, False):
                    dop[lesson].append(j['value'])
                else:
                    dop[lesson] = [j['value']]
        else:
            # предмет выбран
            for j in marks:
                lesson = dn.get_lesson(j['lesson'])['subject']['name']
                if check_subjects(lesson, subject):
                    if dop.get(lesson, False):
                        dop[lesson].append(j['value'])
                    else:
                        dop[lesson] = [j['value']]
        dop_phrase = get_random_phrases('marks')
        res['response']['text'] = dop_phrase
        for j in dop.keys():
            res['response'][
                'text'] += f'{j.capitalize()} - {", ".join(dop[j])}\n'
        res['response']['tts'] = dop_phrase
        return
    else:
        res['response']['text'] = res['response']['tts'] = get_random_phrases('no_marks')
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
                        res['response']['text'] = res['response']['tts'] = get_random_phrases('no_marks')
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
    res['response']['text'] = res['response']['tts'] = get_random_phrases('not_understand')
    return


def final_marks(req, sessionStorage: Session, user_id, subject, res):
    """Финальные оценки"""
    user = sessionStorage.get_user(user_id)
    dn = DnevnikAPI(token=user.token)
    final = dn.get_person_final_marks(
        person_id=user.person_id,
        group_id=user.edu_group
    )
    user_text = req['request']['original_utterance']
    dict_marks = {}
    if any([i in user_text for i in ['итог', 'год']]):
        # пользователь хочет узнать годовую оценку
        for i in final['marks']:
            work = get_work_by_id(final['works'], i['work'])
            if work is None:
                continue
            if work['periodType'] == 'Year':
                dict_marks[find_subject_name(final['subjects'], work['subjectId'])] = \
                    i['textValue']
    else:
        # показываем оценки за четверть или другой период обучения
        period = 0
        for i in req['request']['nlu']['entities']:
            if i['type'] == 'YANDEX.NUMBER':
                period = i['value']
                break
        if period:
            for i in final['marks']:
                work = get_work_by_id(final['works'], i['work'])
                if work is None:
                    continue
                if work['periodNumber'] != period and work['periodType'] != 'Year':
                    dict_marks[find_subject_name(final['subjects'], work['subjectId'])] = \
                        i['textValue']
        else:
            res['response']['text'], res['response']['tts'] = get_random_phrases('no_marks')
            return
    dop_phrase = get_random_phrases('marks')
    if subject is None:
        res['response']['text'] = dop_phrase
        for j in dict_marks.keys():
            res['response']['text'] += \
                f'{j.capitalize()} - {", ".join(dict_marks[j])}\n'
        res['response']['tts'] = dop_phrase
        return
    else:
        res['response']['text'] = dop_phrase
        for j in dict_marks.keys():
            if check_subjects(j, subject):
                res['response']['text'] += \
                    f'{j.capitalize()} - {", ".join(dict_marks[j])}\n'
        res['response']['tts'] = dop_phrase
        if res['response']['text'] == dop_phrase:
            res['response']['text'] = res['response']['tts'] = get_random_phrases('not_understand_subject')
            return
        return


def marks(req, sessionStorage, user_id, res):
    """Оценки"""
    subject = get_subject(req['request']['original_utterance'].lower())
    if any(i in req['request']['original_utterance'].lower()
           for i in ['новые', 'последние']):
        # последние поставленные оценки
        try:
            new_marks(sessionStorage=sessionStorage, user_id=user_id, subject=subject, res=res)
        except Exception as e:
            res['response']['text'] = res['response']['tts'] = get_random_phrases('not_understand')
        return
    if any(i in req['request']['original_utterance'].lower()
           for i in ['итог', 'финал', 'четверт', 'триместр', 'семестр']):
        # итоговые оценки
        try:
            final_marks(sessionStorage=sessionStorage, user_id=user_id, subject=subject, res=res, req=req)
        except Exception:
            res['response']['text'] = res['response']['tts'] = get_random_phrases('not_understand')
        return
    # выставленные оценки
    try:
        old_marks(req=req, sessionStorage=sessionStorage, user_id=user_id, subject=subject, res=res)
    except Exception:
        res['response']['text'] = res['response']['tts'] = get_random_phrases('not_understand')
    return


def get_work_by_id(works: list, work_id: int):
    for i in works:
        if i['id'] == work_id:
            return i
