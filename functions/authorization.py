from dnevnik import DnevnikAPI, DnevnikError
from .subjects import get_subjects
from session import Session
from .phrases import get_random_phrases


def authorization(sessionStorage: Session, user_id: str, token: str):
    """Авторизация пользователя по логину и паролю"""
    try:
        dn = DnevnikAPI(token=token)
    except DnevnikError as e:
        return str(e)
    user = sessionStorage.get_user(user_id)
    # сохраняем токен
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
    return 'Success'
