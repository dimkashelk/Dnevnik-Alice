import pymorphy2
from datetime import datetime


def get_subject(text):
    """Получение предмета из контекста диалога"""
    if ' по ' in text:
        ind = text.split().index('по') + 1
        morph = pymorphy2.MorphAnalyzer()
        p = morph.parse(text.split()[ind])[0]
        return p.normal_form
    return None


def check_subjects(word1, word2):
    """Сравнение двух слов"""
    morph = pymorphy2.MorphAnalyzer()
    word = morph.parse(word2)[0]
    try:
        if 'NOUN' in word.tag.POS:
            if word1 in [word.inflect({'nomn'}).word,
                         word.inflect({'nomn'}).word,
                         word.inflect({'gent'}).word,
                         word.inflect({'datv'}).word,
                         word.inflect({'accs'}).word,
                         word.inflect({'ablt'}).word,
                         word.inflect({'loct'}).word,
                         word.inflect({'nomn', 'plur'}).word,
                         word.inflect({'gent', 'plur'}).word,
                         word.inflect({'datv', 'plur'}).word,
                         word.inflect({'accs', 'plur'}).word,
                         word.inflect({'ablt', 'plur'}).word,
                         word.inflect({'loct', 'plur'}).word]:
                return True
    except Exception:
        pass
    dop, a, b = 0, {}, {}
    for i in word1:
        if i not in a.keys():
            a[i] = 1
        else:
            a[i] += 1
    for i in word2:
        if i not in b.keys():
            b[i] = 1
        else:
            b[i] += 1
    for i in a.keys():
        if i in b.keys():
            dop += min(a[i], b[i])
    return dop >= 3 * len(word1) / 4 and dop >= 3 * len(word2) / 4


def get_subjects(req, subject_id=False):
    """Формирование словаря предметов"""
    dop = {}
    if not subject_id:
        # id: subject
        for i in req:
            dop[i['id']] = i['name'].lower()
    else:
        # subject: id
        for i in req:
            dop[i['name'].lower()] = i['id']
    return dop
