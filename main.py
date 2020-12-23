import subprocess
from flask import Flask, request, send_file
import logging
import json
from functions.schedule import *
from functions.homework import *
from functions.marks import *
from requests import post
from functions.authorization import *
from functions.page_of_lesson import *
from functions.phrases import *
from session import Session
from pprint import pprint
import pymorphy2
from datetime import date

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, filename='app.log')

sessionStorage = Session()


@app.route('/log')
def get_log():
    return send_file('app.log')


@app.route('/update')
def update():
    process = subprocess.Popen('/bin/bash update_from_git.sh'.split())
    return 'request accepted'


@app.route('/authorization')
def authorization_url():
    code = request.args.get('code')
    state = request.args.get('state')
    token = post('https://api.dnevnik.ru/v2/authorizations', data={
        "code": code,
        "client_id": "1d7bd105-4cd1-4f6c-9ecc-394e400b53bd",
        "client_secret": "5dcb5237-b5d3-406b-8fee-4441c3a66c99",
        "grant_type": "AuthorizationCode"
    })
    access_token = token.json()['accessToken']
    authorization(sessionStorage=sessionStorage, user_id=state, token=access_token)
    return 'Success'


@app.route('/', methods=['POST'])
def main():
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False,
        }
    }
    handle_dialog(request.json, response)
    logging.info(f'Response:  {response!r}')
    return json.dumps(response)


def handle_dialog(req, res):
    # заменили user_id на application_id, по документации это одно и тоже
    # не user -> user_id, потому что пользователь может быть не авторизован в яндекс аккаунт.
    # теперь привязка будет к конкретному устройству.
    user_id = get_user_id(req)
    if req['session']['new'] and sessionStorage.get_user(user_id) is None:
        new_user(res=res, user_id=user_id, sessionStorage=sessionStorage)
        return
    # update_access_token(user_id)
    if req['session']['new']:
        res['response']['text'] = res['response']['tts'] = get_random_phrases('user_return')
        return
    authorized_user(res=res, req=req, user_id=user_id)


def new_user(res, user_id, sessionStorage):
    res['response']['text'] = res['response']['tts'] = get_random_phrases('begin_phrase')
    res['response']['buttons'] = get_buttons('authorization', user_id=user_id)
    sessionStorage.insert_new_user(user_id)


def authorized_user(res, req, user_id):
    res['response']['buttons'] = get_buttons('buttons', user_id=get_user_id(request.json))
    if any(i in req['request']['original_utterance'].lower()
           for i in ['инструкц', 'правила']):
        # пользователь просит инструкцию
        logging.info(f'Request: {request.json!r}')
        dop = ''
        for i, val in enumerate(rules_ru):
            dop += f'{i + 1}) {val.capitalize()}\n'
        dop = dop.strip()
        res['response']['text'] = 'У меня очень много правил, но они все маленькие и простые.\n' + dop
        res['response']['tts'] = 'У меня очень много правил, но они все маленькие и простые.'
        res['response']['buttons'] = get_buttons('rules')
    elif req['request']['original_utterance'].lower() in rules_ru:
        # пользователь выбрал конкретный пункт правил
        logging.info(f'Request: {request.json!r}')
        res['response']['text'] = res['response']['tts'] = rules(req['request']['original_utterance'].lower())
    elif sessionStorage.get_user(user_id).authorized:
        # блок если наш пользователь авторизован, пытаем чего он хочет дальше
        logging.info(f'Request: {request.json!r}')
        dop = what_user_want(req)
        if dop == 'schedule':
            # пользователь требует расписание
            schedule(req=req, user_id=user_id, res=res, sessionStorage=sessionStorage)
            return
        elif dop == 'page_of_lesson':
            # пользователь требует конкретный урок
            lesson(req=req,
                   sessionStorage=sessionStorage,
                   user_id=user_id,
                   res=res)
            return
        elif dop == 'homework':
            # пользователь требует свою домашку
            homework(req=req, sessionStorage=sessionStorage, user_id=user_id, res=res)
            return
        elif dop == 'marks':
            # пользователь хочет увидеть оценки
            marks(req=req, sessionStorage=sessionStorage, user_id=user_id, res=res)
            return
        elif dop == 'go_out':
            # выходим из аккаунта
            res['response']['text'] = res['response']['tts'] = get_random_phrases('end_phrase')
            res['response']['end_session'] = True
            return
        elif dop == 'skills':
            res['response']['text'] = res['response']['tts'] = get_random_phrases('skills')
            return
        # не поняла пользователя
        res['response']['text'] = res['response']['tts'] = get_random_phrases('not_understand')
        return
    elif req['request']['original_utterance'] == 'Авторизация':
        # авторизация по логину и паролю
        res['response']['text'] = res['response']['tts'] = get_random_phrases('authorization')
    else:
        # не поняла пользователя
        logging.info(f'Request: {request.json!r}')
        res['response']['text'] = res['response']['tts'] = get_random_phrases('not_authorized')
        res['response']['buttons'] = get_buttons('authorization', user_id=user_id)
        return


def get_buttons(obj: str, user_id=0):
    # формирование кнопок
    title = []
    if obj == 'rules':
        for i in rules_ru:
            title.append({
                "title": i.capitalize(),
                "hide": True
            })
    elif obj == 'buttons':
        user = sessionStorage.get_user(user_id)
        if not user.authorized:
            return
        for i in get_random_phrases_for_buttons(user.authorized, user_id=user_id):
            title.append({
                "title": i.capitalize(),
                "hide": True
            })
    elif obj == 'authorization':
        title.append({
            "title": "Авторизация",
            "url": f"https://login.dnevnik.ru/oauth2?"
                   f"response_type=code&"
                   f"client_id=1d7bd105-4cd1-4f6c-9ecc-394e400b53bd&"
                   f"scope=CommonInfo,ContactInfo,FriendsAndRelatives,EducationalInfo,SocialInfo,Files,Wall,Messages&"
                   f"redirect_uri=https://b9bc09d90b99.ngrok.io/authorization&"
                   f"state={user_id}",
            "hide": False
        })
    return title


def rules(rul: str):
    # правила
    rul = rules_to_en[rul]
    return get_rules(rul)


def get_user_id(req):
    if req['session'].get('user', False):
        return req['session']['user']['user_id']
    return req['session']['application']['application_id']


def what_user_want(req):
    tokens = req['request']['nlu']['tokens']
    morph = pymorphy2.MorphAnalyzer()
    for i, v in enumerate(tokens):
        tokens[i] = morph.parse(v)[0].normal_form
    if any(i in tokens for i in
           ['расписание']):
        return 'schedule'
    elif any(i in tokens for i in
             ['урок', 'кабинет']):
        return 'page_of_lesson'
    elif any(i in tokens for i in
             ['дз', 'домашка', 'домашний', 'задание', 'задать']):
        return 'homework'
    elif any(i in tokens for i in
             ['оценка', 'поставить']):
        return 'marks'
    elif any(i in tokens for i in
             ['выход', 'выйти']):
        return 'go_out'
    elif any(i in tokens for i in
             ['уметь', 'мочь']):
        return 'skills'
    pprint(req)
    print(tokens)


def update_access_token(user_id):
    user = sessionStorage.get_user(user_id)
    date_token = date(*map(int, user.date_token.split('-')))
    if (date.today() - date_token).days > 20:
        dn = DnevnikAPI(token=user.token)
        dn.update_token()


if __name__ == '__main__':
    app.run()
