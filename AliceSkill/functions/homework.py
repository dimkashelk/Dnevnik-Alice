from datetime import datetime, timedelta
from .subjects import *
from .phrases import *
from AliceSkill.dnevnik import DnevnikAPI
from AliceSkill.session import Session


def get_homework(sessionStorage: Session, user_id, res, subject, days=None, months=None, years=None):
    """Получение домашнего задания по конретной дате"""
    user = sessionStorage.get_user(user_id)
    user.token
    dn = DnevnikAPI(token=user.token)
    now = datetime.now()
    year, month, day = now.year, now.month, now.day
    if years is None and months is None:
        homeworks = dn.get_school_homework(
            school_id=user.school_id,
            start_time=datetime(year=year, month=month, day=day) + timedelta(days=days),
            end_time=datetime(year=year, month=month, day=day) + timedelta(days=days)
        )
    elif years is None and months is not None:
        homeworks = dn.get_school_homework(
            school_id=user.school_id,
            start_time=datetime(year=year, month=months, day=days),
            end_time=datetime(year=year, month=months, day=days)
        )
    else:
        homeworks = dn.get_school_homework(
            school_id=user.school_id,
            start_time=datetime(year=years, month=months, day=days),
            end_time=datetime(year=years, month=months, day=days)
        )
    # формирование словаря предмет: домашнее задание
    homework = {}
    for j in homeworks['works']:
        dop = dn.get_homework_by_id(j['id'])
        if dop['subjects'][0]['name'] in homework.keys():
            if dop['works'][0]['text'].strip() not in \
                    homework[dop['subjects'][0]['name']]:
                homework[dop['subjects'][0]['name']].append(
                    dop['works'][0]['text'].strip())
        else:
            homework[dop['subjects'][0]['name']] = [dop['works'][0]['text'].strip()]
    if len(homework.keys()) == 0:
        # если заданий не нашлось
        res['response']['text'] = res['response']['tts'] = get_random_phrases('no_homework')
        return
    phrase = get_random_phrases('homework')
    dop = phrase
    if subject is None:
        # пользователь хочет дз по всем предмета
        for v in homework.keys():
            dop += f'{v.capitalize()}: {"; ".join(homework[v])}\n'
    else:
        # пользователь хочет дз по конкретному предмету
        for v in list(filter(lambda x: check_subjects(x.lower(), subject),
                             homework.keys())):
            dop += f'{v.capitalize()}: {"; ".join(homework[v])}\n'
    res['response']['text'] = dop
    res['response']['tts'] = phrase
    return


def homework(req, sessionStorage, user_id, res):
    """Основная функция получения домашнего задания"""
    subject = get_subject(req['request']['original_utterance'].lower())
    try:
        for i in req['request']['nlu']['entities']:
            if i['type'] == 'YANDEX.DATETIME':
                if i['value']['day_is_relative']:
                    # домашка на один из ближайших дней
                    get_homework(sessionStorage=sessionStorage,
                                 user_id=user_id,
                                 res=res,
                                 subject=subject,
                                 days=i['value']['day'])
                    return
                elif 'year_is_relative' in i['value'].keys():
                    if not i['value']['year_is_relative']:
                        # домашка на конкретный дату: год, месяц, день
                        get_homework(sessionStorage=sessionStorage,
                                     user_id=user_id,
                                     res=res,
                                     subject=subject,
                                     days=i['value']['day'],
                                     months=i['value']['month'],
                                     years=i['value']['year'])
                        return
                elif not i['value']['month_is_relative']:
                    # домашка на конкретный месяц и дату
                    get_homework(sessionStorage=sessionStorage,
                                 user_id=user_id,
                                 res=res,
                                 subject=subject,
                                 days=i['value']['day'],
                                 months=i['value']['month'])
                    return
                else:
                    res['response']['text'] = res['response']['tts'] = get_random_phrases('not_understand')
                    return
    except Exception as e:
        print(e)
    res['response']['text'] = res['response']['tts'] = get_random_phrases('not_understand')
    return
