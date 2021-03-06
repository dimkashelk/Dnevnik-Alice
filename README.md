# Dnevnik&Alice
Я решил сделать проект, который совмещает образовательную платформу Дневник.ру и Алису. Чтобы с помощью голоса можно было узнать свое дз на завтра или оценки за домашку. Проект создан для упрощения взаимодействия с дневником. Почему именно эта платформа? В моем регионе используется эта платформа. Если вы не имеете аккаунта в дневнике, то прошу оценивать проект по видео (на видео я проведу некоторые действия, для демонстрации возможностей и обрежу момент авторизации, для сохранения анонимности). 

Сначала немного об общении с навыком.
Чтобы авторизоваться необходимо ввести два слова: логин и пароль. Логин и пароль не сохраняются в файле логов. 
Реализованные функции: домашка, расписание, оценки, страница урока. Короче все, что нужно от дневника. 

Теперь про запуск и работу. Необходимо создать новый навык Алисы (как это сделать описывается в учебнике). Рекомендую использовать ngrok для создания тоннеля и временной ссылки. Запускать необходимо файл main, который лежит в корне проекта. После запуска main создается сервер. По умолчанию используется 5000 порт. Все правила использования описаны, просто попроси навык сказать о них (скажи: "правила", "инструкция" или в другом контексте). 

Возможная ошибка: навык не ответил за определенное время, связана с задержкой между компьютером, на котором запускается сервер и сайтом диалогов. При возникновении попробуйте ещё раз или обеспечьте максимальную пропускную способность сети. 

Возможные вопросы: 

-Почему нет авторизации по кнопке на сайте дневника? Ответ: проект не согласован с владельцами платформы Дневник.ру, они не знают о навыке, поэтому такой функции нет (Для ее реализации необходимо регистровать как юр. лицо. 

-Почему такой малый функционал? Ответ: функционал достаточный для получения основной и необходимой информации, плюс api дневника не позволяет реализовавывать больше. Есть возможность сделать рейтинг, но его нет для избежания буллинга.

-Безопасность личных данных. Ответ: ответ диалогов с вашими личными данными (логин и пароль от системы) не сохраняется в логах. Все остальные данные фактически находятся в свободном доступе (благодаря api дневника можно узнать все оценки любого ученика школы). Поэтому подвергаются заносу в логи.

-Выход из аккаунта. Ответ: смотри правила в навыке.

Желаю удачи с проверкой.

Скрины работы для тех, у кого нет дневника.

![1 скрин](https://sun1-85.userapi.com/Rn-r25phab7P_Wypp6xykhSoN_6Bkl1LBajAlg/M8RQwveDjuU.jpg)
![2 скрин](https://sun1-25.userapi.com/zz_jGS5sjlHUz_-qDsvSGQ_aVcSUwUzcgvCllQ/7PfblfsP9-Y.jpg)
![3 скрин](https://sun1-16.userapi.com/weJuO7r511lenAn5bLoCRWWUxtTrxixcO4ZRlg/QirS0k4Tw_w.jpg)
![4 скрин](https://sun1-23.userapi.com/pdoIcI3FYW7n-rdVAhyyATcFdCO60K76xgqdzw/h0jjFivqBX4.jpg)
![5 скрин](https://sun1-95.userapi.com/u-Zm4veQ2MN7D0MfF-djinJc2eYnBkned0z1dA/EixXUFUgaUw.jpg)
![6 скрин](https://sun1-17.userapi.com/F3g8wjVCxznkfkQLQCFLIbwRoLb9SqpxNnAgmw/L5QuWAttcgQ.jpg)
![7 скрин](https://sun1-89.userapi.com/QeBY9L3wtW7GYUTMu7lYUN_jb2OauaDqAn7vBQ/F0zUr6faIvM.jpg)
![8 скрин](https://sun1-99.userapi.com/hQipTBQp9z7qApkp-e-gmti5N567xD9JkiShYw/xQsA_3HErOM.jpg)

Пояснение к 8 скрину: по умолчанию используется текущий год, поэтому считается 14 декабря 2020 года, на это число пока нет расписания, так как оно не составлено.

![9 скрин](https://sun1-92.userapi.com/wdxwTiiP8K68soctAp7WYvyn_QDzDPfxaoGPbg/ZYFZwSeKycU.jpg)

Пояснение: "правило дат" (используется текущий год) работает везде в проекте.

![10 скрин](https://sun1-27.userapi.com/w-z-MyrFXujklNzoDaxzVjMJXwqluPmSfm1bMg/ZhciFdf-wIY.jpg)
![11 скрин](https://sun9-42.userapi.com/fUhp6wYkM1BdZkBWBNgo-Dlz_lVoU_y9yW6ycA/m6ebCy-u4mo.jpg)
![12 скрин](https://sun1-89.userapi.com/Xx-L55HKlG3W1Plrt4ebDZDqga6f3qXCplu0ow/_HCaW01vgN8.jpg)

Пояснение: в первом случае неизвестно на какой день пользователь хочет получить расписание, во втором нет расписания, потому что его нет в дневнике, ввиду каникул. 

![13 скрин](https://sun1-14.userapi.com/oHXeQPFn6RtlZagLKPuMO1sDHV3tmTsfUbDlAQ/UDBLgy0Iuic.jpg)
![14 скрин](https://sun1-87.userapi.com/iJhv-8PgLuZbgnZNLXPQWqB3H6EtYCSQfb_jrg/D1bi-67UmsA.jpg)

Не думай, что я хочу оценками похвастаться) Это все для проекта)
