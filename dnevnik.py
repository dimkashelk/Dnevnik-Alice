import requests
from pprint import pprint


class Dnevnik:

    def __init__(self, login: str = None, password: str = None, token: str = None):
        self.session = requests.Session()
        self.host = "https://api.dnevnik.ru/v2/"
        if token is None:
            self.token = self.get_token(login, password)

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
        pprint(json_token)
        try:
            if json_token["type"] == "authorizationFailed":
                print('No :(')
                return
        except KeyError:
            pass
        if token.status_code != 200:
            print('No :(')
            return
        return json_token["accessToken"]

