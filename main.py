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
            'homework': False
        }
        res['response']['text'] = 'Привет! Я - твой личный помощник с Дневником. ' \
                                  'Пожалуйста ознакомься с инструкцией, чтобы избежать недопонимай в разговоре'
        res['response']['tts'] = 'привет я твой личный помощник с дневником ' \
                                 'пожалуйста ознакомься с инструкцией чтобы избежать недопоним+аний в разговоре'
        return
    if any(i in req['request']['original_utterance'].lower()
           for i in ['инструкц', 'правила']):
        # пользователь просит инструкцию
        dop = ''
        for i, val in enumerate(rules_ru):
            dop += f'{i + 1}) {val.capitalize()}\n'
        dop = dop.strip()
        res['response']['text'] = 'У меня очень много правил, но они все маленькие и простые. ' \
                                  'Из-за их количества пришлось разбить их на отдельные категории:\n' + dop
        res['response']['tts'] = 'у меня очень много правил но они все маленькие и простые ' \
                                 'изза их количества пришлось разб+ить их на отдельные катег+ории просто ' \
                                 'выберите из предложенного что вас больше всего интересует'
        res['response']['buttons'] = get_buttons('rules')
    elif req['request']['original_utterance'].lower() in rules_ru:
        # пользователь выбрал конкретный пункт правил
        dop = rules(req['request']['original_utterance'].lower())
        res['response']['text'] = dop[0]
        res['response']['tts'] = dop[1]
    elif sessionStorage[user_id]['authorized']:
        # блок если наш пользователь авторизован, пытаем чего он хочет дальше
        if any(i in req['request']['original_utterance'].lower()
               for i in ['дз', 'домашк', 'домашнее задание', 'задали', 'задание по']) or \
                sessionStorage[user_id]['homework']:
            sessionStorage[user_id]['homework'] = True
            for i in req['request']['nlu']['entities']:
                if i['type'] == 'YANDEX.DATETIME':
                    if i['value']['day_is_relative']:
                        now = datetime.now()
                        year, month, day = now.year, now.month, now.day
                        homeworks = sessionStorage[user_id]['dnevnik'].get_school_homework(
                            school_id=sessionStorage[user_id]['school_id'],
                            start_time=datetime(year=year, month=month, day=day) + timedelta(days=i['value']['day']),
                            end_time=datetime(year=year, month=month, day=day) + timedelta(days=i['value']['day'])
                        )
                        homework = {}
                        for i in homeworks['works']:
                            dop = sessionStorage[user_id]['dnevnik'].get_homework_by_id(i['id'])
                            if dop['subjects'][0]['name'] in homework.keys():
                                if dop['works'][0]['text'] not in homework[dop['subjects'][0]['name']]:
                                    homework[dop['subjects'][0]['name']].append(dop['works'][0]['text'])
                            else:
                                homework[dop['subjects'][0]['name']] = [dop['works'][0]['text']]
                        if len(homework.keys()) == 0:
                            res['response']['text'] = 'Заданий нет'
                            res['response']['tts'] = 'Заданий нет'
                            return
                        dop = 'Вот ваши задания:\n'
                        for v in homework.keys():
                            dop += f'{v.capitalize()}: {"; ".join(homework[v])}\n'
                        res['response']['text'] = dop
                        res['response']['tts'] = 'вот ваши домашние задания'
                        return
                    elif not i['value']['month_is_relative']:
                        now = datetime.now()
                        year, month, day = now.year, now.month, now.day
                        homeworks = sessionStorage[user_id]['dnevnik'].get_school_homework(
                            school_id=sessionStorage[user_id]['school_id'],
                            start_time=datetime(year=year, month=i['value']['month'], day=i['value']['day']),
                            end_time=datetime(year=year, month=i['value']['month'], day=i['value']['day'])
                        )
                        homework = {}
                        for i in homeworks['works']:
                            dop = sessionStorage[user_id]['dnevnik'].get_homework_by_id(i['id'])
                            if dop['subjects'][0]['name'] in homework.keys():
                                if dop['works'][0]['text'] not in homework[dop['subjects'][0]['name']]:
                                    homework[dop['subjects'][0]['name']].append(dop['works'][0]['text'])
                            else:
                                homework[dop['subjects'][0]['name']] = [dop['works'][0]['text']]
                        if len(homework.keys()) == 0:
                            res['response']['text'] = 'Заданий нет'
                            res['response']['tts'] = 'Заданий нет'
                            return
                        dop = 'Вот ваши задания:\n'
                        for v in homework.keys():
                            dop += f'{v.capitalize()}: {"; ".join(homework[v])}\n'
                        res['response']['text'] = dop
                        res['response']['tts'] = 'вот ваши домашние задания'
                        return
                    else:
                        res['response']['text'] = 'Я вас не поняла :('
                        res['response']['tts'] = 'я вас не поняла'
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
        sessionStorage[user_id]['school_id'] = sessionStorage[user_id]['dnevnik'].get_school()[0]['id']
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


if __name__ == '__main__':
    app.run()
