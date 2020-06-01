from dnevnik import DnevnikAPI, DnevnikError
from .subjects import get_subjects


def authorization(req, sessionStorage, user_id, res):
    dop = req['request']['original_utterance'].split()
    try:
        sessionStorage[user_id]['dnevnik'] = DnevnikAPI(login=dop[0],
                                                        password=dop[1])
    except DnevnikError as e:
        res['response']['text'] = str(e)
        res['response']['tts'] = str(e).lower()
        return
    sessionStorage[user_id]['authorized'] = True
    sessionStorage[user_id]['school_id'] = \
        sessionStorage[user_id]['dnevnik'].get_school()[0]['id']
    sessionStorage[user_id]['edu_group'] = \
        sessionStorage[user_id]['dnevnik'].get_edu_groups()[1]
    sessionStorage[user_id]['person_id'] = \
        sessionStorage[user_id]['dnevnik'].get_info_about_me()['personId']
    dop = sessionStorage[user_id]['dnevnik'].get_subjects(
        sessionStorage[user_id]['edu_group'])
    sessionStorage[user_id]['id-subject'] = get_subjects(dop)
    sessionStorage[user_id]['subject-id'] = get_subjects(dop, subject_id=True)
    res['response']['text'] = 'Вы авторизовались и я подключена к дневнику!'
    res['response']['tts'] = 'вы авторизов+ались и я подключена к дневнику'
    return
