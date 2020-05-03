from flask import Flask, request
import logging
import json
from data.const import *
from dnevnik import DnevnikAPI, DnevnikError

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
            'authorized': False
        }
        res['response']['text'] = 'Привет! Я - твой личный помощник с Дневником. ' \
                                  'Пожалуйста ознакомься с инструкцией, чтобы избежать недопонимай в разговоре'
        res['response']['ttx'] = 'привет я твой личный помощник с дневником ' \
                                 'пожалуйста ознакомься с инструкцией чтобы избежать недопоним+аний в разговоре'
        return
    if any(i in req['request']['original_utterance'].lower()
           for i in ['инструкц', 'правила']):
        # пользователь просит инструкцию
        dop = ''
        for i, val in enumerate(rules_ru):
            dop += f'{i + 1}) {val.title()}\n'
        dop = dop.strip()
        res['response']['text'] = 'У меня очень много правил, но они все маленькие и простые. ' \
                                  'Из-за их количества пришлось разбить их на отдельные категории:\n' + dop
        res['response']['ttx'] = 'у меня очень много правил но они все маленькие и простые ' \
                                 'изза их количества пришлось разб+ить их на отдельные катег+ории просто ' \
                                 'выберите из предложенного что вас больше всего интересует'
        res['response']['buttons'] = get_buttons('rules')
    elif req['request']['original_utterance'].lower() in rules_ru:
        # пользователь выбрал конкретный пункт правил
        dop = rules(req['request']['original_utterance'].lower())
        res['response']['text'] = dop[0]
        res['response']['ttx'] = dop[1]
    elif sessionStorage[user_id]['authorized']:
        # блок если наш пользователь авторизован, пытаем чего он хочет дальше
        # пока стоит заглушка
        sessionStorage[user_id]['authorized'] = True
        res['response']['text'] = 'Вы авторизовались и я подключена к дневнику!'
        res['response']['ttx'] = 'вы авторизов+ались и я подключена к дневнику'
    elif sessionStorage[user_id]['authorized'] is False and len(req['request']['original_utterance'].split()) == 2 and \
            req['request']['original_utterance'].split()[0].lower() not in rules_ru and \
            req['request']['original_utterance'].split()[1].lower() not in rules_ru:
        # авторизация по логину и паролю
        dop = req['request']['original_utterance'].split()
        try:
            sessionStorage[user_id]['dnevnik'] = DnevnikAPI(login=dop[0],
                                                            password=dop[1])
        except DnevnikError as e:
            res['response']['text'] = str(e)
            res['response']['ttx'] = str(e).lower()
            return
        res['response']['text'] = 'Вы авторизовались и я подключена к дневнику!'
        res['response']['ttx'] = 'вы авторизов+ались и я подключена к дневнику'
    else:
        res['response']['text'] = 'Я вас не поняла :('
        res['response']['ttx'] = 'я вас не поняла'


def get_buttons(obj: str):
    title = []
    if obj == 'rules':
        for i in rules_ru:
            title.append({
                "title": i.title(),
                "hide": True
            })
    return title


def rules(rul: str):
    text = []
    with open(f'./data/usage_rules/text/{rules_to_en[rul]}', encoding='utf-8') as file:
        text.append(file.read())
    with open(f'./data/usage_rules/ttx/{rules_to_en[rul]}', encoding='utf-8') as file:
        text.append(file.read())
    return text


if __name__ == '__main__':
    app.run()
