from aiogram.dispatcher import FSMContext


# Получение языка
async def get_language(uid: int, state: FSMContext, con):
    data = await state.get_data()
    lang_code = data.get('lang')
    if lang_code is None:
        # Если значение языка не сохранено в словаре, получаем его из базы данных
        print(uid)
        lang_code = await get_user_language(uid, con)
        if not lang_code:
            lang_code = 'en'
            await post_user_language(uid, lang_code, con)
        await state.update_data(lang=lang_code)
    return lang_code


# Проверка есть ли юзер в бд и добавление его туда
async def check_and_add_user_from_db(user_id, language, con):
    cur = con.cursor()
    user = cur.execute("""SELECT * FROM user WHERE user_id = ?""", (user_id,)).fetchone()
    if user:
        return
    cur.execute("""INSERT INTO user (user_id, language, hint) VALUES (?, ?, ?)""", (user_id, language, False,))
    cur.execute("""INSERT INTO detailed_statistics (user_id) VALUES (?)""", (user_id,))
    con.commit()


# Проверка есть ли юзер в бд
async def check_user_from_db(user_id, con):
    cur = con.cursor()
    user = cur.execute("""SELECT * FROM user WHERE user_id = ?""", (user_id,)).fetchone()
    if user:
        return False
    return True


# Подсказки во время игры True/False
async def need_a_hint(user_id, con):
    cur = con.cursor()
    hint = cur.execute("""SELECT hint FROM user WHERE user_id = ?""", (user_id,)).fetchone()
    return hint[0]


# Обновление языка пользователя для бд
async def post_user_language(user_id, language, con):
    cur = con.cursor()
    cur.execute("""UPDATE user SET language=? WHERE user_id=?""", (language, user_id,))
    con.commit()


# Получение языка пользователя
async def get_user_language(user_id, con):
    cur = con.cursor()
    print(user_id)
    language = cur.execute("""SELECT language FROM user WHERE user_id = ?""", (str(user_id),)).fetchone()
    return language[0]


# Обновление подсказок во время игры
async def update_hint(user_id, hint, con):
    cur = con.cursor()
    cur.execute("""UPDATE user SET hint=? WHERE user_id=?""", (hint, user_id,))
    con.commit()


# Краткая сводка о игроке
async def about_the_user(user_id, con):
    cur = con.cursor()
    balance = cur.execute("""SELECT balance FROM user WHERE user_id = ?""", (user_id,)).fetchone()
    user = cur.execute("""SELECT * FROM detailed_statistics WHERE user_id = ?""", (user_id,)).fetchone()
    return user, balance


# Засчитывание поражения\победы
async def result_of_battle(user_id, victory, con, algorithm=False, balance=20):
    cur = con.cursor()
    if algorithm:
        text = 'algorithm'
    else:
        text = 'people'

    if victory:
        print(balance, 'баланс в функции')
        cur.execute(f"""UPDATE user SET balance = balance + ? WHERE user_id=?""", (balance, user_id,)).fetchone()
        cur.execute(f"""UPDATE detailed_statistics SET
                                         games_against_{text} = games_against_{text} + 1,
                                         wins_over_the_{text} = wins_over_the_{text} + 1
                                         WHERE user_id=?""", (user_id,)).fetchone()
    else:
        cur.execute(f"""UPDATE detailed_statistics SET
                                         games_against_{text} = games_against_{text} + 1
                                         WHERE user_id=?""", (user_id,)).fetchone()
    con.commit()


# Списание баланса
async def changing_balance(user_id, balance, con):
    cur = con.cursor()
    cur.execute(f"""UPDATE user SET balance = balance + ? WHERE user_id=?""", (balance, user_id,)).fetchone()
    con.commit()


# Асинхронная функция для вычисления Score игрока
def calculate_score(player_data):
    user_id, wins, total_games = player_data
    if total_games == 0:
        return user_id, wins, 0, 0  # Игрок без игр, Score и поражения None
    losses = total_games - wins
    r = (wins + 1) / (losses + 1) * total_games
    return user_id, wins, losses, r


# Сортировка для топов
async def sorting_by_criterion(id_user, criterion, con):
    cursor = con.cursor()


    # Получаем данные о победах и общем количестве игр игроков из базы данных
    if criterion == "balance":
        cursor.execute("SELECT user_id, balance, hint, language FROM user ORDER BY balance DESC LIMIT 10")
        top_users = cursor.fetchall()

        # Найдите позицию пользователя по ID в отсортированной таблице по балансу
        your_user_id = 123  # Замените 123 на ID пользователя, которого вы хотите найти
        cursor.execute("SELECT COUNT(*) + 1 FROM user WHERE balance > (SELECT balance FROM user WHERE user_id = ?)",
                       (your_user_id,))
        user_position = cursor.fetchone()[0]
        return top_users, user_position
    else:
        if criterion == "human":
            cursor.execute('SELECT user_id, wins_over_the_people, games_against_people FROM detailed_statistics')
        else:
            cursor.execute('SELECT user_id, wins_over_the_algorithm, games_against_algorithm FROM detailed_statistics')
        players_data = cursor.fetchall()

        # Создаем список кортежей с данными о игроках и None вместо Score
        players_with_score = [(user_id, wins, None) for user_id, wins, _ in players_data]

        # Вычисляем Score для игроков асинхронно
        players_with_score = [calculate_score(player_data) for player_data in players_data]

        # Сортируем игроков по Score в убывающем порядке
        sorted_players = sorted(players_with_score, key=lambda x: x[3], reverse=True)

        # Находим место игрока с заданным ID
        player_place = next((i + 1 for i, (user_id, _, _, _) in enumerate(sorted_players) if user_id == id_user), None)

        # Возвращаем топ-10 игроков и место игрока
        top_10_players = sorted_players[:10]
        return top_10_players, player_place


