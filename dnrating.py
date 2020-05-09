from flask import Flask, request
import logging
import json
from data.const import *
from base import DnevnikAPI, DnevnikError
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
        sessionStorage[user_id] = {
            'authorized': False,
            'homework': False
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
        dop = ''
        for i, val in enumerate(rules_ru):
            dop += f'{i + 1}) {val.capitalize()}\n'
        dop = dop.strip()
        res['response']['text'] = 'У меня очень много правил, но они все маленькие и простые. ' \
                                  'Из-за их количества пришлось разбить их на отдельные ' \
                                  'категории:\n' + dop
        res['response']['tts'] = 'у меня очень много правил но они все маленькие и простые ' \
                                 'изза их количества пришлось разб+ить их на отдельные ' \
                                 'катег+ории ' \
                                 '' \
                                 '' \
                                 'просто ' \
                                 'выберите из предложенного что вас больше всего интересует'
        res['response']['buttons'] = get_buttons('rules')
    elif req['request']['original_utterance'].lower() in rules_ru:
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
    dop = 0
    for i in range(min(len(word1), len(word2))):
        if word1[i] == word2[i]:
            dop += 1
    return dop >= len(word1) // 2 and dop >= len(word2) // 2


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
