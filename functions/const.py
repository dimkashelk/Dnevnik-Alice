# файл с константами
# при добавлении новых функций достаточно внести их в словари
# и Алиса начнет их упоминать в диалоге
rules_ru = ['авторизация', 'домашнее задание', 'оценки', 'расписание', 'страница урока', 'выход']
rules_to_en = {
    'авторизация': 'authorization',
    'домашнее задание': 'homework',
    'оценки': 'marks',
    'расписание': 'schedule',
    'выход': 'exit',
    'страница урока': 'page_of_lesson'
}

text_phrases = {
    'authorization': [
        'Вы авторизовались и я подключена к дневнику!',
        'Ура! Я подключилась к вашему дневнику',
        'Подключение прошло успешно',
        'Что дальше?'
    ],
    'no_homework': [
        'Заданий нет!',
        'Можешь отдыхать, ничего не задали',
        'Можешь погулять, на завтра нет заданий'
    ],
    'homework': [
        'Ваши задания:\n',
        'Вот что вам задали:\n',
        'Не бойтесь, все решаемо:\n',
        'Придется делать, сама не рада:\n',
        'Взяла из Вашего дневника:\n',
    ],
    'not_understand': [
        'Что вы сказали?',
        'Я вас не поняла',
        'Давайте говорить понятно',
        'Попробуйте перефразировать, используя правила',
        'Неожиданный факт: когда я не понимаю, я не отвечаю',
        'Зачем строить наши отношения на догадках? Ведь, мы можем общаться понятным друг другу языком',
        'Можете ещё раз повторить? Не расслышала',
    ],
    'new_marks': [
        'Вот что вам поставили:\n',
        'Новые оценки:\n',
        'Новые оценочки:\n',
        'Довольно не плохо, но можно лучше:\n',
        'Стараешься?\n',
        'Взяла из Вашего дневника:\n',
    ],
    'nothing_is_exposed': [
        'Сегодня ничего не поставили :(',
        'Ничего не выставили',
        'Ничего нового, попробуйте позже'
    ],
    'no_marks': [
        'Оценок нет :(',
        'Ничего не нашлось',
        'Никаких оценок нет...'
    ],
    'marks': [
        'Ваши оценки:\n',
        'Вот что вам поставили:\n',
        'Ваши оценочки:\n',
        'Взяла из Вашего дневника:\n',
    ],
    'not_understand_subject': [
        'Я не поняла предмет :(',
        'Можете ещё раз повторить? Не расслышала',
        'Какой-то неизвестный мне предмет вы сказали.',
        'Зачем строить наши отношения на догадках? Ведь, мы можем общаться понятным друг другу языку',
    ],
    'no_lessons': [
        'Уроков нет',
        'Отдыхай, уроков нет',
    ],
    'no_lesson': [
        'Не смогла найти такой урок',
        'Такого урока нет',
        'Очень странно, но мне кажется, что такого урока не существует',
        'Урок не найден',
    ],
    'page_lesson': [
        'Вот что мне удалось найти',
        'Страница урока',
        'Краткая информация',
        'Взяла из Вашего дневника',
    ],
    'schedule': [
        'Ваше расписание:\n',
        'Расписание уроков:\n'
    ],
    'schedule_is_not_available': [
        'Расписание не доступно',
        'Расписание уроков не доступно'
    ],
    'begin_phrase': [
        'Привет! Я - твой личный помощник с Дневником. Авторизуйся и пользуйся!',
    ]
}
