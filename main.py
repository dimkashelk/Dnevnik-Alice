from flask import Flask, request
import logging
import json
from data.const import *
from dnevnik import DnevnikAPI, DnevnikError
from datetime import datetime, timedelta

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, filename='app.log')

sessionStorage = {}


@app.route('/', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(request.json, response)
    logging.info(f'Response:  {response!r}')
    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']
    if req['session']['new']:
        # поймали нового пользователя
        sessionStorage[user_id] = {
            'authorized': False,
        }
        res['response']['text'] = 'Привет! Я - твой личный помощник с Дневником. ' \
                                  'Пожалуйста ознакомься с инструкцией, чтобы избежать ' \
                                  'недопонимай в разговоре'
        res['response']['tts'] = 'привет я твой личный помощник с дневником ' \
                                 'пожалуйста ознакомься с инструкцией чтобы избежать ' \
                                 'недопоним+аний в разговоре'
        return
    if any(i in req['request']['original_utterance'].lower()
           for i in ['инструкц', 'правила']):
        # пользователь просит инструкцию
        dop = ''
        for i, val in enumerate(rules_ru):
            dop += f'{i + 1}) {val.capitalize()}\n'
        dop = dop.strip()
        res['response']['text'] = 'У меня очень много правил, но они все маленькие и простые. ' \
                                  'Из-за их количества пришлось разбить их на отдельные ' \
                                  'категории:\n' + dop
        res['response']['tts'] = 'у меня очень много правил но они все маленькие и простые ' \
                                 'изза их количества пришлось разб+ить их на отдельные катег+ории ' \
                                 'просто ' \
                                 'выберите из предложенного что вас больше всего интересует'
        res['response']['buttons'] = get_buttons('rules')
    elif req['request']['original_utterance'].lower() in rules_ru:
        # пользователь выбрал конкретный пункт правил
        dop = rules(req['request']['original_utterance'].lower())
        res['response']['text'] = dop[0]
        res['response']['tts'] = dop[1]
    elif sessionStorage[user_id]['authorized']:
        if any(i in req['request']['original_utterance'].lower()
               for i in ['рейтинг', 'мест', 'в классе']) or \
                sessionStorage[user_id]['rating']:
            sessionStorage[user_id]['rating'] = True
            subject = get_subject(req['request']['original_utterance'].lower())
            if subject:
                subject_id = sessionStorage[user_id][subject]
                user_subject_average_mark = get_subject_average_mark(subject_id, user_id)
                group_subject_average_mark = get_group_subject_average_mark()
                res['response']['text'] = 'Ваш средний балл по предмету ' + subject + \
                                          ': ' + user_subject_average_mark + '\n' + \
                                          'Средний балл класса по предмету ' + subject + \
                                          ': ' + group_subject_average_mark
        # блок если наш пользователь авторизован, пытаем чего он хочет дальше
        if any(i in req['request']['original_utterance'].lower()
               for i in ['дз', 'домашк', 'домашнее задание', 'задали', 'задание по']):
            subject = get_subject(req['request']['original_utterance'].lower())
            for i in req['request']['nlu']['entities']:
                if i['type'] == 'YANDEX.DATETIME':
                    if i['value']['day_is_relative']:
                        now = datetime.now()
                        year, month, day = now.year, now.month, now.day
                        homeworks = sessionStorage[user_id]['dnevnik'].get_school_homework(
                            school_id=sessionStorage[user_id]['school_id'],
                            start_time=datetime(year=year, month=month, day=day) + timedelta(
                                days=i['value']['day']),
                            end_time=datetime(year=year, month=month, day=day) + timedelta(
                                days=i['value']['day'])
                        )
                        homework = {}
                        for i in homeworks['works']:
                            dop = sessionStorage[user_id]['dnevnik'].get_homework_by_id(i['id'])
                            if dop['subjects'][0]['name'] in homework.keys():
                                if dop['works'][0]['text'] not in homework[
                                    dop['subjects'][0]['name']]:
                                    homework[dop['subjects'][0]['name']].append(
                                        dop['works'][0]['text'])
                            else:
                                homework[dop['subjects'][0]['name']] = [dop['works'][0]['text']]
                        if len(homework.keys()) == 0:
                            res['response']['text'] = 'Заданий нет'
                            res['response']['tts'] = 'Заданий нет'
                            return
                        dop = 'Вот ваши задания:\n'
                        if subject is None:
                            for v in homework.keys():
                                dop += f'{v.capitalize()}: {"; ".join(homework[v])}\n'
                        else:
                            for v in list(filter(lambda x: check_words(x.lower(), subject),
                                                 homework.keys())):
                                dop += f'{v.capitalize()}: {"; ".join(homework[v])}\n'
                        res['response']['text'] = dop
                        res['response']['tts'] = 'вот ваши домашние задания'
                        return
                    elif not i['value']['month_is_relative']:
                        now = datetime.now()
                        year, month, day = now.year, now.month, now.day
                        homeworks = sessionStorage[user_id]['dnevnik'].get_school_homework(
                            school_id=sessionStorage[user_id]['school_id'],
                            start_time=datetime(year=year, month=i['value']['month'],
                                                day=i['value']['day']),
                            end_time=datetime(year=year, month=i['value']['month'],
                                              day=i['value']['day'])
                        )
                        homework = {}
                        for i in homeworks['works']:
                            dop = sessionStorage[user_id]['dnevnik'].get_homework_by_id(i['id'])
                            if dop['subjects'][0]['name'] in homework.keys():
                                if dop['works'][0]['text'] not in homework[
                                    dop['subjects'][0]['name']]:
                                    homework[dop['subjects'][0]['name']].append(
                                        dop['works'][0]['text'])
                            else:
                                homework[dop['subjects'][0]['name']] = [dop['works'][0]['text']]
                        if len(homework.keys()) == 0:
                            res['response']['text'] = 'Заданий нет'
                            res['response']['tts'] = 'Заданий нет'
                            return
                        dop = 'Вот ваши задания:\n'
                        if subject is None:
                            for v in homework.keys():
                                dop += f'{v.capitalize()}: {"; ".join(homework[v])}\n'
                        else:
                            for v in list(filter(lambda x: check_words(x.lower(), subject),
                                                 homework.keys())):
                                dop += f'{v.capitalize()}: {"; ".join(homework[v])}\n'
                        res['response']['text'] = dop
                        res['response']['tts'] = 'вот ваши домашние задания'
                        return
                    else:
                        res['response']['text'] = 'Я вас не поняла :('
                        res['response']['tts'] = 'я вас не поняла'
        elif any(i in req['request']['original_utterance'].lower()
                 for i in ['оценки', 'поставили']):
            subject = get_subject(req['request']['original_utterance'].lower())
            if any(i in req['request']['original_utterance'].lower()
                   for i in ['новые', 'последние']):
                # последние поставленные оценки
                marks = sessionStorage[user_id]['dnevnik'].get_last_marks(
                    person_id=sessionStorage[user_id]['person_id'],
                    group_id=sessionStorage[user_id]['edu_group']
                )['marks']
                dop = {}
                if subject is None:
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
                    for i in marks:
                        if i['lesson'] is None:
                            continue
                        else:
                            if datetime.now().strftime('%Y-%m-%d') in i['date']:
                                dop_subject = sessionStorage[user_id]['id-subject'][i['lesson']]
                                if not check_words(dop_subject, subject):
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
            for i in req['request']['nlu']['entities']:
                if i['type'] == 'YANDEX.DATETIME':
                    if 'year_is_relative' in i['value'].keys():
                        if not i['value']['year_is_relative']:
                            if 'month' in i['value'].keys() and 'day' in i['value'].keys():
                                marks = sessionStorage[user_id]['dnevnik'].get_marks_from_to(
                                    person_id=sessionStorage[user_id]['person_id'],
                                    school_id=sessionStorage[user_id]['school_id'],
                                    from_time=datetime(year=i['value']['year'],
                                                       month=i['value']['month'],
                                                       day=i['value']['day'],
                                                       hour=0,
                                                       minute=0,
                                                       second=0),
                                    to_time=datetime(year=i['value']['year'],
                                                     month=i['value']['month'],
                                                     day=i['value']['day'],
                                                     hour=23,
                                                     minute=59,
                                                     second=59)
                                )
                                if len(marks):
                                    dop = {}
                                    if subject is None:
                                        for i in marks:
                                            lesson = sessionStorage[user_id]['dnevnik'].get_lesson(
                                                i['lesson'])['subject']['name']
                                            if dop.get(lesson, False):
                                                dop[lesson].append(i['value'])
                                            else:
                                                dop[lesson] = [i['value']]
                                    else:
                                        for i in marks:
                                            lesson = sessionStorage[user_id]['dnevnik'].get_lesson(
                                                i['lesson'])['subject']['name']
                                            if check_words(lesson, subject):
                                                if dop.get(lesson, False):
                                                    dop[lesson].append(i['value'])
                                                else:
                                                    dop[lesson] = [i['value']]
                                    res['response']['text'] = 'Ваши оценки:\n'
                                    for i in dop.keys():
                                        res['response'][
                                            'text'] += f'{i.capitalize()} - {", ".join(dop[i])}'
                                    res['response']['tts'] = 'ваши оценки'
                                    return
                                else:
                                    res['response']['text'] = 'Оценок нет :('
                                    res['response']['tts'] = 'оценок нет'
                                    return
                            else:
                                res['response']['text'] = 'Оценок нет :('
                                res['response']['tts'] = 'оценок нет'
                                return
                    elif 'month_is_relative' in i['value'].keys():
                        if not i['value']['month_is_relative']:
                            year = datetime.now().year
                            date = datetime(year, i['value']['month'],
                                            i['value']['day']) + timedelta(days=-1)
                            marks = sessionStorage[user_id]['dnevnik'].get_marks_from_to(
                                person_id=sessionStorage[user_id]['person_id'],
                                school_id=sessionStorage[user_id]['school_id'],
                                from_time=datetime(year=date.year,
                                                   month=i['value']['month'],
                                                   day=i['value']['day'],
                                                   hour=0,
                                                   minute=0,
                                                   second=0),
                                to_time=datetime(year=date.year,
                                                 month=i['value']['month'],
                                                 day=i['value']['day'],
                                                 hour=23,
                                                 minute=59,
                                                 second=59)
                            )
                            if len(marks):
                                dop = {}
                                if subject is None:
                                    for i in marks:
                                        lesson = sessionStorage[user_id]['dnevnik'].get_lesson(
                                            i['lesson'])['subject']['name']
                                        if dop.get(lesson, False):
                                            dop[lesson].append(i['value'])
                                        else:
                                            dop[lesson] = [i['value']]
                                else:
                                    for i in marks:
                                        lesson = sessionStorage[user_id]['dnevnik'].get_lesson(
                                            i['lesson'])['subject']['name']
                                        if check_words(lesson, subject):
                                            if dop.get(lesson, False):
                                                dop[lesson].append(i['value'])
                                            else:
                                                dop[lesson] = [i['value']]
                                res['response']['text'] = 'Ваши оценки:\n'
                                for i in dop.keys():
                                    res['response'][
                                        'text'] += f'{i.capitalize()} - {", ".join(dop[i])}\n'
                                res['response']['tts'] = 'ваши оценки'
                                return
                            else:
                                res['response']['text'] = 'Оценок нет :('
                                res['response']['tts'] = 'оценок нет'
                                return
                    else:
                        if not i['value']['day_is_relative']:
                            year = datetime.now().year
                            month = datetime.now().month
                            marks = sessionStorage[user_id]['dnevnik'].get_marks_from_to(
                                person_id=sessionStorage[user_id]['person_id'],
                                school_id=sessionStorage[user_id]['school_id'],
                                from_time=datetime(year=year,
                                                   month=month,
                                                   day=i['value']['day'],
                                                   hour=0,
                                                   minute=0,
                                                   second=0),
                                to_time=datetime(year=year,
                                                 month=month,
                                                 day=i['value']['day'],
                                                 hour=23,
                                                 minute=59,
                                                 second=59)
                            )
                            if len(marks):
                                dop = {}
                                if subject is None:
                                    for i in marks:
                                        lesson = sessionStorage[user_id]['dnevnik'].get_lesson(
                                            i['lesson'])['subject']['name']
                                        if dop.get(lesson, False):
                                            dop[lesson].append(i['value'])
                                        else:
                                            dop[lesson] = [i['value']]
                                else:
                                    for i in marks:
                                        lesson = sessionStorage[user_id]['dnevnik'].get_lesson(
                                            i['lesson'])['subject']['name']
                                        if check_words(lesson, subject):
                                            if dop.get(lesson, False):
                                                dop[lesson].append(i['value'])
                                            else:
                                                dop[lesson] = [i['value']]
                                res['response']['text'] = 'Ваши оценки:\n'
                                for i in dop.keys():
                                    res['response'][
                                        'text'] += f'{i.capitalize()} - {", ".join(dop[i])}'
                                res['response']['tts'] = 'ваши оценки'
                                return
                            else:
                                res['response']['text'] = 'Оценок нет :('
                                res['response']['tts'] = 'оценок нет'
                                return
                        elif i['value']['day_is_relative']:
                            year = (datetime.now() + timedelta(days=i['value']['day'])).year
                            month = (datetime.now() + timedelta(days=i['value']['day'])).month
                            day = (datetime.now() + timedelta(days=i['value']['day'])).day
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
                            if len(marks):
                                dop = {}
                                if subject is None:
                                    for i in marks:
                                        lesson = sessionStorage[user_id]['dnevnik'].get_lesson(
                                            i['lesson'])['subject']['name']
                                        if dop.get(lesson, False):
                                            dop[lesson].append(i['value'])
                                        else:
                                            dop[lesson] = [i['value']]
                                else:
                                    for i in marks:
                                        lesson = sessionStorage[user_id]['dnevnik'].get_lesson(
                                            i['lesson'])['subject']['name']
                                        if check_words(lesson, subject):
                                            if dop.get(lesson, False):
                                                dop[lesson].append(i['value'])
                                            else:
                                                dop[lesson] = [i['value']]
                                res['response']['text'] = 'Ваши оценки:\n'
                                for i in dop.keys():
                                    res['response'][
                                        'text'] += f'{i.capitalize()} - {", ".join(dop[i])}'
                                res['response']['tts'] = 'ваши оценки'
                                return
                            else:
                                res['response']['text'] = 'Оценок нет :('
                                res['response']['tts'] = 'оценок нет'
                                return
            res['response']['text'] = 'Я вас не поняла :('
            res['response']['tts'] = 'я вас не поняла'
            return
    elif sessionStorage[user_id]['authorized'] is False and \
            len(req['request']['original_utterance'].split()) == 2 and \
            req['request']['original_utterance'].split()[0].lower() not in rules_ru and \
            req['request']['original_utterance'].split()[1].lower() not in rules_ru:
        # авторизация по логину и паролю
        dop = req['request']['original_utterance'].split()
        try:
            sessionStorage[user_id]['dnevnik'] = DnevnikAPI(login=dop[0],
                                                            password=dop[1])
        except DnevnikError as e:
            res['response']['text'] = str(e)
            res['response']['tts'] = str(e).lower()
            return
        sessionStorage[user_id]['authorized'] = True
        sessionStorage[user_id]['school_id'] = sessionStorage[user_id]['dnevnik'].get_school()[0][
            'id']
        sessionStorage[user_id]['edu_group'] = sessionStorage[user_id]['dnevnik'].get_edu_groups()[
            1]
        sessionStorage[user_id]['person_id'] = \
        sessionStorage[user_id]['dnevnik'].get_info_about_me()['personId']
        dop = sessionStorage[user_id]['dnevnik'].get_work_types(
            sessionStorage[user_id]['school_id'])
        sessionStorage[user_id]['id-subject'] = get_types_work(dop)
        sessionStorage[user_id]['subject-id'] = get_types_work(dop, subject_id=True)
        res['response']['text'] = 'Вы авторизовались и я подключена к дневнику!'
        res['response']['tts'] = 'вы авторизов+ались и я подключена к дневнику'
    else:
        res['response']['text'] = 'Я вас не поняла :('
        res['response']['tts'] = 'я вас не поняла'


def get_buttons(obj: str):
    title = []
    if obj == 'rules':
        for i in rules_ru:
            title.append({
                "title": i.capitalize(),
                "hide": True
            })
    return title


def rules(rul: str):
    text = []
    with open(f'./data/usage_rules/text/{rules_to_en[rul]}', encoding='utf-8') as file:
        text.append(file.read())
    with open(f'./data/usage_rules/tts/{rules_to_en[rul]}', encoding='utf-8') as file:
        text.append(file.read())
    return text


def get_subject(text):
    if ' по ' in text:
        ind = text.split().index('по') + 1
        return text.split()[ind]
    return None


def check_words(word1, word2):
    # fixme: исправить сравнение двух слов, короче надо придумать что-то новое
    dop = 0
    for i in range(min(len(word1), len(word2))):
        if word1[i] == word2[i]:
            dop += 1
    return dop >= len(word1) // 2 and dop >= len(word2) // 2


def get_types_work(req, subject_id=False):
    dop = {}
    if not subject_id:
        for i in req:
            dop[i['id']] = i['abbr']
    else:
        for i in req:
            dop[i['abbr']] = i['id']
    return dop


def get_start_school_year():
    now = datetime.now()
    month = now.month
    year = now.year
    if month < 9:
        year -= 1
    from_time = datetime(year, 9, 1)
    return from_time


def get_average(marks):
    marks_number = len(marks)
    marks_sum = sum(marks)
    average = round(marks_sum / marks_number, 2)
    return average


def get_subject_average_mark(subject_id, user_id):
    school_id = DnevnikAPI.get_school
    from_time = get_start_school_year()
    marks = DnevnikAPI.get_marks_from_to(user_id, school_id, from_time)
    subject_marks = sessionStorage[marks][subject_id]
    return get_average(subject_marks)


def get_group_subject_average_mark():
    group_id = DnevnikAPI.get_edu_groups()[1]
    subject_marks = DnevnikAPI.get_group_marks(group_id)
    return get_average(subject_marks)


if __name__ == '__main__':
    app.run()
