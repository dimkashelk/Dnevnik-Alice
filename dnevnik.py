import requests
from pprint import pprint
from datetime import datetime, timedelta


class DnevnikError(Exception):
    pass


class DnevnikBase:

    def __init__(self, login: str = None, password: str = None, token: str = None):
        self.session = requests.Session()
        self.host = "https://api.dnevnik.ru/v2/"
        if token is None:
            self.token = self.get_token(login, password)
        self.session.headers = {"Access-Token": self.token}

    def get_token(self, login, password):
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
                    raise DnevnikError("Неизвестная ошибка в API, проверьте правильность параметров")
                if json_response["type"] == "apiUnknownError":
                    raise DnevnikError("Неизвестная ошибка в API, проверьте правильность параметров")
        except KeyError:
            pass

    def get(self, method: str, params=None, **kwargs):
        if params is None:
            params = {}
        response = self.session.get(self.host + method, params=params, **kwargs)
        self._check_response(response)
        return response.json()

    def post(self, method: str, data=None, **kwargs):
        if data is None:
            data = {}
        response = self.session.post(self.host + method, data=data, **kwargs)
        self._check_response(response)
        return response.json()

    def delete(self, method: str, params=None, **kwargs):
        if params is None:
            params = {}
        response = self.session.delete(self.host + method, params=params, **kwargs)
        self._check_response(response)
        return response.json()

    def put(self, method: str, params=None, **kwargs):
        if params is None:
            params = {}
        response = self.session.put(self.host + method, data=params, **kwargs)
        self._check_response(response)
        return response.json()


class DnevnikAPI(DnevnikBase):

    def __init__(self, login: str = None, password: str = None, token: str = None):
        super().__init__(login, password, token)
        self.login = login
        self.password = password

    def get_school(self):
        school_id = self.get("schools/person-schools")
        return school_id

    def get_homework_by_id(self, homework_id: int):
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
        homework = self.get(
            f"users/me/school/{school_id}/homeworks",
            params={"startDate": start_time, "endDate": end_time},
        )
        return homework
