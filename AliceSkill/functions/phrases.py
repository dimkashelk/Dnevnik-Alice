from .const import *
from random import randrange, randint, shuffle


def get_random_phrases(type_phrases):
    return text_phrases[type_phrases][randrange(0, len(text_phrases[type_phrases]))]


def get_rules(category):
    return text_phrases['rules'][category]


def get_random_phrases_for_buttons(authorized, user_id=0):
    if not authorized:
        return [{
            "title": "Авторизация",
            "url": f"https://login.dnevnik.ru/oauth2?"
                   f"response_type=code&"
                   f"client_id=1d7bd105-4cd1-4f6c-9ecc-394e400b53bd&"
                   f"scope=CommonInfo,ContactInfo,FriendsAndRelatives,EducationalInfo,SocialInfo,Files,Wall,Messages&"
                   f"redirect_uri=https://7d29eccdbbf3.ngrok.io/authorization&"
                   f"state={user_id}",
            "hide": True
        }]
    type_phrases = list(text_phrases['text_for_buttons'].keys())
    ans = []
    for i in type_phrases[:randint(1, len(type_phrases))]:
        for j in range(2):
            dop = text_phrases['text_for_buttons'][i][randint(0, len(text_phrases['text_for_buttons'][i]) - 1)]
            while dop in ans:
                dop = text_phrases['text_for_buttons'][i][randint(0, len(text_phrases['text_for_buttons'][i]) - 1)]
            ans.append(dop)
    shuffle(ans)
    return ans
