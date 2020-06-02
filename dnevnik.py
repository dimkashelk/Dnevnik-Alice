import requests
from datetime import datetime, timedelta


class DnevnikError(Exception):
    # ошибка дневника (дневник не доступен или неправильный логин/пароль)
    pass


class DnevnikBase:

    # класс с базовыми функциями

    def __init__(self, login: str = None, password: str = None, token: str = None):
        # создаем сессию для request
        self.session = requests.Session()
        self.host = "https://api.dnevnik.ru/v2/"
        self.token = self.get_token(login, password)
        self.session.headers = {"Access-Token": self.token}

    def get_token(self, login, password):
        # получение токена доступа (для каждого пользователя он свой)
        token = self.session.post(
            "https://api.dnevnik.ru/v2/authorizations/bycredentials",
            json={
                "client_id": "1d7bd105-4cd1-4f6c-9ecc-394e400b53bd",
                "client_secret": "5dcb5237-b5d3-406b-8fee-4441c3a66c99",
                "username": login,
                "password": password,
                "scope": "Schools,Relatives,EduGroups,Lessons,marks,EduWorks,Avatar,"
                         "EducationalInfo,CommonInfo,ContactInfo,FriendsAndRelatives,"
                         "Files,Wall,Messages",
            },
        )
        json_token = token.json()
        try:
            if json_token["type"] == "authorizationFailed":
                raise DnevnikError('Неверный логин или пароль')
        except KeyError:
            pass
        if token.status_code != 200:
            raise DnevnikError('Сервисы дневника временно не доступны')
        return json_token["accessToken"]

    @staticmethod
    def _check_response(response):
        # проверяем ответ дневника на корректность
        # и если что-то не так выкидываем ошибку
        if response.headers.get("Content-Type") == "text/html":
            error_html = response.content.decode()
            error_text = " ".join(
                word for word in error_html.split('<div class="error__description">'
                                                  )[-1].split("<p>")[1].strip()[:-4].split()
            )
            raise DnevnikError(error_text)
        json_response = response.json()
        try:
            if isinstance(json_response, dict):
                if json_response["type"] == "parameterInvalid":
                    raise DnevnikError(json_response["description"])
                if json_response["type"] == "apiServerError":
                    raise DnevnikError(
                        "Неизвестная ошибка в API, проверьте правильность параметров")
                if json_response["type"] == "apiUnknownError":
                    raise DnevnikError(
                        "Неизвестная ошибка в API, проверьте правильность параметров")
        except KeyError:
            pass

    def get(self, method: str, params=None, **kwargs):
        # осуществляем get запрос
        if params is None:
            params = {}
        response = self.session.get(self.host + method, params=params, **kwargs)
        self._check_response(response)
        return response.json()

    def post(self, method: str, data=None, **kwargs):
        # осуществляем post запрос
        if data is None:
            data = {}
        response = self.session.post(self.host + method, data=data, **kwargs)
        self._check_response(response)
        return response.json()

    def delete(self, method: str, params=None, **kwargs):
        # осуществляем delete запрос
        if params is None:
            params = {}
        response = self.session.delete(self.host + method, params=params, **kwargs)
        self._check_response(response)
        return response.json()

    def put(self, method: str, params=None, **kwargs):
        # осуществляем put запрос
        if params is None:
            params = {}
        response = self.session.put(self.host + method, data=params, **kwargs)
        self._check_response(response)
        return response.json()


class DnevnikAPI(DnevnikBase):

    # основной класс дневника

    def __init__(self, login: str = None, password: str = None, token: str = None):
        super().__init__(login, password, token)
        self.login = login
        self.password = password

    def get_school(self):
        """Получение школы пользователя"""
        school_id = self.get("schools/person-schools")
        return school_id

    def get_homework_by_id(self, homework_id: int):
        """Получение домашнего задания по его id"""
        homework = self.get(f"users/me/school/homeworks", params={"homeworkId": homework_id})
        return homework

    def get_school_homework(
            self,
            school_id: int,
            start_time: datetime = datetime(year=datetime.now().year, month=datetime.now().month,
                                            day=datetime.now().day) + timedelta(days=1),
            end_time: datetime = datetime(year=datetime.now().year, month=datetime.now().month,
                                          day=datetime.now().day) + timedelta(days=1),
    ):
        """Получение домашнего задания в заданный период"""
        homework = self.get(
            f"users/me/school/{school_id}/homeworks",
            params={"startDate": start_time, "endDate": end_time},
        )
        return homework

    def get_all_subjects(self, school_id: int):
        """Получение всех предметов ученика"""
        all_subjects = self.get(f'schools/{school_id}/subjects')
        return all_subjects

    def get_edu_groups(self):
        """Получение всех учебных групп"""
        edu_groups = self.get(f"users/me/edu-groups")
        return edu_groups

    def get_info_about_me(self):
        """Информация про ученика"""
        info = self.get("users/me")
        return info

    def get_group_marks(self, group_id: int):
        """Получение всех финальных оценок группы по всем предметам"""
        edu_groups_marks = self.get(f"edu-groups/{group_id}/final-marks")
        return edu_groups_marks

    def get_person_group_marks(self, person_id: int, group_id: int):
        """Получение всех финальных оценок ученика в группе"""
        person_marks_in_group = self.get(
            f"persons/{person_id}/edu-groups/{group_id}/final-marks"
        )
        return person_marks_in_group

    def get_group_subject_final_marks(self, group_id: int, subject_id: int):
        """Получение оценок всей группы по конретному предмету"""
        group_subject_marks = self.get(
            f"edu-groups/{group_id}/subjects/{subject_id}/final-marks"
        )
        return group_subject_marks

    def get_person(self, person_id: int):
        """Получение информации о персоне по id"""
        memberships = self.get(f"persons/{person_id}")
        return memberships

    def get_lesson(self, lesson_id: int):
        """Получение информации про урок по id"""
        lesson = self.get(f"lessons/{lesson_id}")
        return lesson

    def get_last_marks(self, person_id, group_id, **kwargs):
        """Получение последних оценок"""
        marks = self.get(f"persons/{person_id}/group/{group_id}/recentmarks", params=kwargs)
        return marks

    def get_work_types(self, school_id):
        """Получение всех типов работ в школе"""
        types = self.get(f"work-types/{school_id}")
        return types

    def get_marks_from_to(self,
                          person_id: int,
                          school_id: int,
                          from_time: datetime = datetime.now(),
                          to_time: datetime = datetime.now()):
        """Получение всех оценок в определенный период"""
        marks = self.get(
            f"persons/{person_id}/schools/{school_id}/marks/"
            f"{from_time}/"
            f"{to_time}"
        )
        return marks

    def get_subjects(self, edu_group_id: int):
        """Получение всех предметов"""
        subjects = self.get(f'edu-groups/{edu_group_id}/subjects')
        return subjects

    def get_schedules(self, person_id: int, group_id: int, params: dict):
        """Получение расписания на конкретную дату"""
        schedules = self.get(f'persons/{person_id}/groups/{group_id}/schedules', params=params)
        return schedules
