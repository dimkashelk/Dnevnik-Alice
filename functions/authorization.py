from dnevnik import DnevnikAPI, DnevnikError
from .subjects import get_subjects
from session import Session
from .phrases import get_random_phrases


def authorization(req: dict, sessionStorage: Session, user_id: str, res: dict):
    """Авторизация пользователя по логину и паролю"""
    dop = req['request']['original_utterance'].split()
    try:
        dn = DnevnikAPI(login=dop[0],
                        password=dop[1])
    except DnevnikError as e:
        res['response']['text'] = str(e)
        res['response']['tts'] = str(e).lower()
        return
    user = sessionStorage.get_user(user_id)
    # сохраняем токен
    print(dn.token)
    user.token = dn.token
    # теперь пользователь авторизован
    user.authorized = True
    # берем id школы
    user.school_id = dn.get_school()[0]['id']
    # получаем id образовательной группы
    user.edu_group = dn.get_edu_group()
    # получение персонального id
    user.person_id = dn.get_info_about_me()['personId']
    sessionStorage.commit()
    res['response']['text'] = res['response']['tts'] = get_random_phrases('authorization')
    return
