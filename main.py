import subprocess
from flask import Flask, request, send_file
import logging
import json
from data.const import *
from data.functions.schedule import *
from data.functions.homework import *
from data.functions.marks import *
from data.functions.authorization import *
from data.functions.page_of_lesson import *

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, filename='app.log')

sessionStorage = {}


@app.route('/log')
def get_log():
    return send_file('app.log')


@app.route('/update')
def update():
    process = subprocess.Popen('/bin/bash update_from_git.sh'.split())
    return 'request accepted'


@app.route('/', methods=['POST'])
def main():
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
        logging.info(f'Request: {request.json!r}')
        dop = ''
        for i, val in enumerate(rules_ru):
            dop += f'{i + 1}) {val.capitalize()}\n'
        dop = dop.strip()
        res['response']['text'] = 'У меня очень много правил, но они все маленькие и простые. ' \
                                  'Из-за их количества пришлось разбить их на отдельные ' \
                                  'категории:\n' + dop
        res['response']['tts'] = 'у меня очень много правил но они все маленькие и простые ' \
                                 'изза их количества пришлось разб+ить их на отдельные катег+ории ' \
                                 '' \
                                 'просто ' \
                                 'выберите из предложенного что вас больше всего интересует'
        res['response']['buttons'] = get_buttons('rules')
    elif req['request']['original_utterance'].lower() in rules_ru:
        # пользователь выбрал конкретный пункт правил
        logging.info(f'Request: {request.json!r}')
        dop = rules(req['request']['original_utterance'].lower())
        res['response']['text'] = dop[0]
        res['response']['tts'] = dop[1]
    elif sessionStorage[user_id]['authorized']:
        # блок если наш пользователь авторизован, пытаем чего он хочет дальше
        logging.info(f'Request: {request.json!r}')
        if any(i in req['request']['original_utterance'].lower()
               for i in ['расписани']):
            # пользователь требует расписание
            schedule(req=req, user_id=user_id, res=res, sessionStorage=sessionStorage)
            return
        elif any(i in req['request']['original_utterance'].lower()
                 for i in ['урок', 'кабинет']):
            # пользователь требует конкретный урок
            lesson(req=req,
                   sessionStorage=sessionStorage,
                   user_id=user_id,
                   res=res)
            return
        elif any(i in req['request']['original_utterance'].lower()
                 for i in ['дз', 'домашк', 'домашнее задание', 'задали', 'задание по']):
            # пользователь требует свою домашку
            homework(req=req, sessionStorage=sessionStorage, user_id=user_id, res=res)
            return
        elif any(i in req['request']['original_utterance'].lower()
                 for i in ['оценки', 'поставили']):
            # пользователь хочет увидеть оценки
            marks(req=req, sessionStorage=sessionStorage, user_id=user_id, res=res)
            return
        elif any(i in req['request']['original_utterance'].lower()
                 for i in ['выход', 'выйди']):
            # выходим из аккаунта
            sessionStorage[user_id] = {
                'authorized': False,
            }
            res['response']['text'] = 'Я вышла из аккаунта, до скорой встречи'
            res['response']['tts'] = 'я вышла из аккаунта до скорой встречи'
            res['response']['end_session'] = True
            return
        # не поняла пользователя
        res['response']['text'] = 'Я вас не поняла :('
        res['response']['tts'] = 'я вас не поняла'
        return
    elif sessionStorage[user_id]['authorized'] is False and \
            len(req['request']['original_utterance'].split()) == 2 and \
            req['request']['original_utterance'].split()[0].lower() not in rules_ru and \
            req['request']['original_utterance'].split()[1].lower() not in rules_ru:
        # авторизация по логину и паролю
        authorization(req=req, sessionStorage=sessionStorage, user_id=user_id, res=res)
    else:
        # не поняла пользователя
        logging.info(f'Request: {request.json!r}')
        res['response']['text'] = 'Я вас не поняла, пожалуйста авторизуйтесь :('
        res['response']['tts'] = 'я вас не поняла пожалуйста авторизуйтесь'
        return


def get_buttons(obj: str):
    # формирование кнопок
    title = []
    if obj == 'rules':
        for i in rules_ru:
            title.append({
                "title": i.capitalize(),
                "hide": True
            })
    return title


def rules(rul: str):
    # правила
    text = []
    with open(f'./data/usage_rules/text/{rules_to_en[rul]}.txt', encoding='utf-8') as file:
        text.append(file.read())
    with open(f'./data/usage_rules/tts/{rules_to_en[rul]}.txt', encoding='utf-8') as file:
        text.append(file.read())
    return text


if __name__ == '__main__':
    app.run()
