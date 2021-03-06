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
        'Взяла из вашего дневника:\n',
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
    ],
    'user_return': [
        'С возвращением!',
        'Я вас так ждала!',
        'Где вы были? Уже успела по вам соскучиться'
    ],
    'end_phrase': [
        'До скорой встречи!',
        'Я вышла из вашего аккаунта, пока'
    ],
    'not_authorized': [
        'Войдите в аккаунт',
        'Пока вы не вошли, я не смогу вам ответить',
        'Авторизуйтесь и спросите ещё раз',
        'Я вас не поняла, авторизуйтесь, пожалуйста'
    ],
    'rules': {
        'authorization': 'Просто нажмите на кнопку авторизации и дайте все разрешения',
        'exit': 'Если вы не планируете больше использовать навык, или вы используете чужое устройство, '
                'то перед завершением работы просим выйти из аккаунта. '
                'Скажите: "Выйди из аккаунта" или похожую фразу',
        'homework': 'Для получения домашнего задания, вам надо сообщить день, '
                    'который вы хотите (завтра, вчера, число текущего месяца)',
        'marks': 'Если вы хотите узнать ваши оценки, то есть 3 способа: \n'
                 '1) Попросите меня показать последние оценки '
                 '(в этом случае я покажу вам последние выставленные за сегодня оценки)\n'
                 '2) Попросите меня показать оценки на конкретное число '
                 '(в этом случае я покажу оценки, выставленные на эту дату)\n'
                 '3) Попросите показать итоговые оценки',
        'page_of_lesson': 'Если вам нужно открыть страницу урока, '
                          'то просто скажите номер урока и дату (если не скажете дату, то будет сегодняшний урок)',
        'schedule': 'Вы можете посмотреть расписание на любой день (если оно доступно), '
                    'для этого скажите: "Покажи расписание на завтра". Или используйте другую похожую фразу'
    },
    'text_for_buttons': {
        'homework': [
            'Что задали на завтра?',
            'Покажи домашку',
            'Какое у меня домашнее задание?',
        ],
        'marks': [
            'Что нового мне поставили?',
            'Какие новые оценки мне поставили?',
            'Что стоит у меня на сегодня?'
        ],
        'schedule': [
            'Покажи мое расписание',
            'Расписание на завтра',
            'Первый урок завтра',
            'Какое сегодня расписание?'
        ]
    }
}
