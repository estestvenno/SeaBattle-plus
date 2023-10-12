import asyncio
import requests
import random
import sqlite3
from copy import deepcopy
from pprint import pprint

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import MessageNotModified, MessageCantBeEdited

from config import TOKEN
from func import check_and_add_user_from_db, need_a_hint, post_user_language, update_hint, about_the_user, \
    result_of_battle, changing_balance, check_user_from_db, sorting_by_criterion
from language.language_definition import getting_the_language_message, getting_the_language_call
from language.language import LANGUAGE

from creating_playing_field import CreatingField

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
loop = asyncio.get_event_loop()
TIMERS = {}
GAME_SEARCH = []
FRIEND_GAME_SEARCH = {}
PLAYERS_IN_GAME = {}
ACTIVE_GAMES = []
PROCESS_CREATING_FIELD = {}


# Класс описывающий игрока
class Player:
    WHOSE_MOVE = ['⬅️', '']
    CELL_TYPE = ["🌊", "⛵", "🚤", "⛴", "🚢", "⭕️", "❌", "✖️"]
    CELL_TYPE_RADAR = ["🟥", "🟧", "🟨", "🟩"]
    SHIP_SIZES = {6: [4, 3, 2, 1], 8: [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]}
    BIG_GUNS = {1: 50, 2: 125, 3: 125, 4: 275}

    def __init__(self, bot, dp: Dispatcher, con, player_call, state, board, user_id, hints):
        # Возможно уберу
        self.bot = bot
        self.dp = dp
        self.con = con
        # Последнее сообщение человека
        self.player_call = player_call
        # Последнее состояние человека
        self.player_state = state
        # Поле человека
        self.board = board
        # id юзера
        self.user_id = user_id
        # Общая игра
        self.game = None
        # Словарь для хранения кораблей
        self.ships = {}
        # Флаг, определяющий, ходит ли игрок в данный момент
        self.is_turn = 0
        # Размер поля
        self.size = 8
        # Живые корабли человека
        self.living_ships = self.SHIP_SIZES[self.size][:]
        # Нужда в подсказках
        self.hints = hints
        # Имя человека
        self.name = f'<a href="tg://user?id={player_call.from_user.id}">{player_call.from_user.first_name}</a>'
        # Реакция на нажатие кнопки\
        print('Новый игрок')
        self.dp.register_callback_query_handler(self.make_move, Text(startswith=f'fight_call{self.user_id}'))
        self.dp.register_callback_query_handler(self.super_weapon_menu, Text(startswith=f'big_guns{self.user_id}'))
        self.dp.register_callback_query_handler(self.super_weapon, Text(startswith=f'super_weapon{self.user_id}'))

    async def make_move(self, call: types.CallbackQuery, state: FSMContext):
        # Выполнение хода
        print(self, 'Второй игрок')
        if self.is_turn:
            print(self, 'Первый игрок')
            # Последнее сообщение человека
            self.player_call = call
            # Последнее состояние человека
            self.player_state = state
            x_y = call.data.split("_")
            x, y = int(x_y[2]), int(x_y[3])
            if len(x_y) == 5:
                print("супер")
                damage = await self.damage_handler(x, y, int(x_y[4]))
                await self.game.start_game(x, y, super_weapon=damage, super_weapon_type=int(x_y[4]))
                await call.answer()
            else:
                print("не супер")
                await self.game.start_game(x, y)
                await call.answer()
        else:
            lang_code = await getting_the_language_call(call, state, self.con)
            text = LANGUAGE[lang_code]['super_weapon']
            await call.answer(text[1], True)

    # Возвращает клетки подбитые супероружием
    async def damage_handler(self, x, y, type_of_weapon):
        damage = []
        print(type_of_weapon, "тип оружия")
        if type_of_weapon == 1:
            ...
        elif type_of_weapon == 2:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if 0 <= (x + i) < self.size and 0 <= (y + j) < self.size:
                        damage.append([x + i, y + j])
        elif type_of_weapon == 3:
            for i in range(-7, 8):
                if 0 <= (y + i) < self.size:
                    damage.append([x, y + i])
                if y + i > self.size:
                    break
        elif type_of_weapon == 4:
            for i in range(-2, 3):
                for j in range(-2, 3):
                    if 0 <= (x + i) < self.size and 0 <= (y + j) < self.size:
                        damage.append([x + i, y + j])
        return damage

    # Переключение очереди хода
    async def queue(self):
        # Переключение очереди хода
        self.is_turn = (self.is_turn + 1) % 2
        print("очередь:", self.is_turn)

    # Подключение к игре
    async def connecting_to_game(self, game):
        # Подключение к игре
        self.game = game

    # Отрисовка поля
    async def field_fight_rendering(self, enemy, your, last_move, difficulty=7, super_weapon=None, radar=False):
        call = self.player_call
        state = self.player_state
        # это выбор языка
        lang_code = await getting_the_language_call(call, state, self.con)
        # Не проиграл ли юзер?
        if self.living_ships:
            # Получение языка
            text = LANGUAGE[lang_code]['fight_menu']
            # Кто ходит?
            text_field = text[0].format(move1=self.WHOSE_MOVE[self.is_turn],
                                        move2=self.WHOSE_MOVE[self.is_turn - 1],
                                        name1=enemy[0], name2=your[0], move3=last_move)
            for i in range(self.size):
                text_field += "\n"
                for j in range(self.size):
                    text_field += self.CELL_TYPE[your[1][i][j]]

            # Радар
            # Создание поля для радара
            coefficient_field = []
            divider = 0
            max_coef = float('-inf')
            min_coef = float('inf')
            if radar:
                if difficulty == 7:
                    living_ships = self.game.players[self.game.current_player].living_ships
                else:
                    living_ships = self.game.algorithm_living_ships
                coefficient_field = await self.game.algorithm.creates_the_coefficient_field(enemy[1], living_ships,
                                                                                            True)
                for row in coefficient_field:
                    if not row:
                        continue  # Пропустить пустые строки

                    max_in_row = max(row)
                    if max_in_row > max_coef:
                        max_coef = max_in_row

                    non_zero_nums = [num for num in row if num != 0]
                    if non_zero_nums:
                        min_in_row = min(non_zero_nums)
                        if min_in_row < min_coef:
                            min_coef = min_in_row

                divider = (max_coef - min_coef) // 4

            # Добавление кнопок на которых можно ходить
            markup = types.InlineKeyboardMarkup()
            for i in range(self.size):
                buttons = []
                for j in range(self.size):
                    if super_weapon:
                        if radar:
                            if enemy[1][i][j] in [0, 1, 2, 3, 4]:
                                if coefficient_field[i][j] < (divider * 2 + min_coef):
                                    button = types.InlineKeyboardButton(text=self.CELL_TYPE_RADAR[0],
                                                                        callback_data=f"fight_call{self.user_id}_{i}_{j}")
                                elif (divider * 2 + min_coef) <= coefficient_field[i][j] < ((divider * 3) + min_coef):
                                    button = types.InlineKeyboardButton(text=self.CELL_TYPE_RADAR[1],
                                                                        callback_data=f"fight_call{self.user_id}_{i}_{j}")
                                elif ((divider * 3) + min_coef) <= coefficient_field[i][j] < ((divider * 4) + min_coef):
                                    button = types.InlineKeyboardButton(text=self.CELL_TYPE_RADAR[2],
                                                                        callback_data=f"fight_call{self.user_id}_{i}_{j}")
                                elif ((divider * 4) + min_coef) <= coefficient_field[i][j]:
                                    button = types.InlineKeyboardButton(text=self.CELL_TYPE_RADAR[3],
                                                                        callback_data=f"fight_call{self.user_id}_{i}_{j}")
                            else:
                                button = types.InlineKeyboardButton(text=self.CELL_TYPE[enemy[1][i][j]],
                                                                    callback_data=f"fight_call{self.user_id}_{i}_{j}")
                        else:
                            if enemy[1][i][j] in [0, 1, 2, 3, 4]:
                                button = types.InlineKeyboardButton(text=self.CELL_TYPE[0],
                                                                    callback_data=f"fight_call{self.user_id}_{i}_{j}_{super_weapon}")
                            else:
                                button = types.InlineKeyboardButton(text=self.CELL_TYPE[enemy[1][i][j]],
                                                                    callback_data=f"fight_call{self.user_id}_{i}_{j}_{super_weapon}")
                    else:
                        if enemy[1][i][j] in [0, 1, 2, 3, 4]:
                            button = types.InlineKeyboardButton(text=self.CELL_TYPE[0],
                                                                callback_data=f"fight_call{self.user_id}_{i}_{j}")
                        else:
                            button = types.InlineKeyboardButton(text=self.CELL_TYPE[enemy[1][i][j]],
                                                                callback_data=f"fight_call{self.user_id}_{i}_{j}")
                    buttons.append(button)
                markup.row(*buttons)
            # Добавляем оставшиеся кнопки на клавиатуру
            if difficulty < 4:
                # для боя с ботом бе оружия
                markup.row(types.InlineKeyboardButton(text=text[2], callback_data="deleting_all_sessions"))
            else:
                markup.row(types.InlineKeyboardButton(text=text[1], callback_data=f"big_guns{self.user_id}"),
                           types.InlineKeyboardButton(text=text[2], callback_data="deleting_all_sessions"))
            # Само сообщение
            try:
                print(self.is_turn, 'отрисовка', call.from_user.first_name)
                await call.message.edit_text(text_field, reply_markup=markup, parse_mode='HTML')
            except MessageNotModified:
                pass
        else:
            await self.game.logic_of_victory_and_defeat(self)

    # Меню выбора супероружия
    async def super_weapon_menu(self, call: types.CallbackQuery, state: FSMContext):
        lang_code = await getting_the_language_call(call, state, self.con)
        text = LANGUAGE[lang_code]['super_weapon']
        if self.is_turn:
            text = LANGUAGE[lang_code]['super_weapon_menu']
            markup = types.InlineKeyboardMarkup()
            markup.row(types.InlineKeyboardButton(text=text[1], callback_data=f"super_weapon{self.user_id}_1"))
            markup.row(types.InlineKeyboardButton(text=text[2], callback_data=f"super_weapon{self.user_id}_2"))
            markup.row(types.InlineKeyboardButton(text=text[3], callback_data=f"super_weapon{self.user_id}_3"))
            markup.row(types.InlineKeyboardButton(text=text[4], callback_data=f"super_weapon{self.user_id}_4"))
            markup.row(types.InlineKeyboardButton(text=text[5], callback_data=f"super_weapon{self.user_id}_5"))
            all_us = await about_the_user(call.from_user.id, con)
            balance = all_us[1][0]
            try:
                print(self.is_turn, 'отрисовка супера', call.from_user.first_name)
                await call.message.edit_text(text[0].format(balance=balance), reply_markup=markup)
            except MessageNotModified:
                pass
        else:
            await call.answer(text[1], True)

    # Распределение и логика использования супер оружия
    async def super_weapon(self, call: types.CallbackQuery, state: FSMContext):
        lang_code = await getting_the_language_call(call, state, self.con)
        text = LANGUAGE[lang_code]['super_weapon']
        if not self.game.algorithm_flag:
            player1 = self.game.players[self.game.current_player - 1 * self.is_turn]
            player1_name = f'<a href="tg://user?id={player1.player_call.from_user.id}' \
                           f'">{player1.player_call.from_user.first_name}</a>'
            player2_name = f'<a href="tg://user?id={self.player_call.from_user.id}' \
                           f'">{self.player_call.from_user.first_name}</a>'
            player1_field = self.game.player1_class.board
            player2_field = self.board
        else:
            player1_name = self.game.algorithm.name
            player2_name = f'<a href="tg://user?id={self.player_call.from_user.id}' \
                           f'">{self.player_call.from_user.first_name}</a>'
            player1_field = self.game.field_algorithm
            player2_field = self.board
        player1 = [player1_name, player1_field]
        player2 = [player2_name, player2_field]
        last_move = self.game.history[-1]
        if self.is_turn:
            definition_super_weapon = int(call.data.split("_")[2])
            if definition_super_weapon == 5:
                await self.field_fight_rendering(player1, player2, last_move)
            else:
                all_us = await about_the_user(call.from_user.id, con)
                balance = all_us[1][0]
                if balance < self.BIG_GUNS[definition_super_weapon]:
                    await call.answer(text[0], True)
                    await self.field_fight_rendering(player1, player2, last_move)
                else:
                    await changing_balance(call.from_user.id, self.BIG_GUNS[definition_super_weapon] * -1, self.con)
                    if definition_super_weapon == 1:
                        if self.game.algorithm_flag:
                            await self.field_fight_rendering(player1, player2, last_move, difficulty=6,
                                                             super_weapon=definition_super_weapon, radar=True)
                        else:
                            await self.field_fight_rendering(player1, player2, last_move, difficulty=7,
                                                             super_weapon=definition_super_weapon, radar=True)
                    else:
                        await call.answer(text[2], True)
                        await self.field_fight_rendering(player1, player2, last_move,
                                                         super_weapon=definition_super_weapon)
        else:
            await call.answer(text[1], True)
            await self.field_fight_rendering(player1, player2, last_move)

    # Проигрыш
    async def defeat(self, call: types.CallbackQuery = None, state: FSMContext = None, algorithm=False):
        if not call:
            call = self.player_call
        if not state:
            state = self.player_state
        # Получение языка игрока
        lang_code = await getting_the_language_call(call, state, self.con)
        text = deepcopy(LANGUAGE[lang_code]['victory_menu'])
        # Создание истории
        history = self.game.history
        for i in history:
            text[1] += i + '\n'
        # Создание кнопок для игрока
        markup = types.InlineKeyboardMarkup()
        # Кнопка возврата в меню для игрока
        # Возврат в меню
        markup.row(types.InlineKeyboardButton(text=text[2], callback_data=f"start_call"))
        # Изменение его статистики
        await result_of_battle(call.from_user.id, False, self.con, algorithm)
        # Отправление ему соболезнований
        await call.message.edit_text(text=text[1], reply_markup=markup, parse_mode='HTML')

    # Проигрыш без штрафов(нет противника)
    async def defeat_without_penalties(self, call: types.CallbackQuery = None, state: FSMContext = None):
        if not call:
            call = self.player_call
        if not state:
            state = self.player_state
            # Получение языка игрока
        lang_code = await getting_the_language_call(call, state, self.con)
        text = LANGUAGE[lang_code]['deleting_all_sessions']
        # Создание кнопок для игрока(удаляющего сессию)
        markup = types.InlineKeyboardMarkup()
        # Кнопка возврата в меню для игрока(удаляющего сессию)
        # Возврат в меню
        markup.row(types.InlineKeyboardButton(text=text[2], callback_data=f"start_call"))
        # Процесс удаления игрока из игры + составление статистики
        # удаление игрока из играющих игроков
        await call.message.edit_text(text=text[1], reply_markup=markup)

    # Выйграл
    async def victory(self, call: types.CallbackQuery = None, state: FSMContext = None, algorithm=False,
                      difficulty=None):
        if not call:
            call = self.player_call
        if not state:
            state = self.player_state
        # Получение языка игрока
        lang_code = await getting_the_language_call(call, state, self.con)
        text = deepcopy(LANGUAGE[lang_code]['victory_menu'])
        # Создание истории
        history = self.game.history
        for i in history:
            text[0] += i + '\n'
        # Создание кнопок для игрока
        markup = types.InlineKeyboardMarkup()
        # Кнопка возврата в меню для игрока
        # Возврат в меню
        markup.row(types.InlineKeyboardButton(text=text[2], callback_data=f"start_call"))
        # Изменение его статистики
        if algorithm:
            balance = difficulty * 5
            await result_of_battle(call.from_user.id, True, self.con, algorithm, balance)
        await result_of_battle(call.from_user.id, True, self.con, algorithm)
        # Отправление ему соболезнований
        await call.message.edit_text(text=text[0], reply_markup=markup, parse_mode='HTML')

    # Удаление игрока
    async def delete(self):
        dp.callback_query_handlers.unregister(self.make_move)
        dp.callback_query_handlers.unregister(self.super_weapon_menu)
        dp.callback_query_handlers.unregister(self.super_weapon)
        del self


# Класс описывающий игру с человеком
class Game:
    ARSENAL = ["🔫", "📡", "💣", "🛩", "🚀"]

    def __init__(self, bot, dp, con, player1_class, algorithm, timer_time):
        # Короче обязательная херня
        self.bot = bot
        self.dp = dp
        self.con = con
        self.algorithm = algorithm
        # Игрок основавший игру
        self.player1_class = player1_class
        # Игрок второй
        self.player2_class = None
        # Список игроков
        self.players = [self.player1_class]
        # Время таймера
        self.timer_time = timer_time
        # Очередь хода
        self.current_player = 0
        # История боя
        self.history = ['']
        # флаг для определения игра с алгоритмом или нет
        self.algorithm_flag = False

        self.ignored = [0, 0]

    # Присоединяем к игре еще одного игрока
    async def joining_a_player_and_start_game(self, player2_class):
        global ACTIVE_GAMES
        global TIMERS
        ACTIVE_GAMES.append(self)
        # Тот самый игрок
        self.player2_class = player2_class
        # Добавляем его в список игроков
        self.players.append(self.player2_class)
        # Рандомно определить, кто ходит первым
        self.current_player = random.randint(0, 1)
        # Сообщаем пользователю что сейчас его ход
        await self.players[self.current_player].queue()
        user_id = self.players[self.current_player].player_call.from_user.id
        TIMERS[user_id] = asyncio.get_event_loop().call_later(self.timer_time, self.timeout, user_id)
        await self.drawing_field_for_players()

    # Сам процесс игры
    async def start_game(self, x, y, super_weapon=None, super_weapon_type=0):
        global TIMERS
        print(self.ignored)
        self.ignored[self.current_player] = 0
        print(1, "ACTIVE_GAMES")
        if self in ACTIVE_GAMES:
            print(2, "ACTIVE_GAMES")
            # Если это выстрел супер оружия то ход не засчитывается
            if super_weapon:
                # Проходим по всем клеткам пораженным супер оружием и отмечает их
                for i in super_weapon:
                    x, y = i
                    await self.check_field_and_adjust_needed(x, y)
                    # отрисовываю поле челу который стреляет
                    # ничего кроме отрисовки не происходит и юзер1 продолжает ходить
                self.current_player = (self.current_player + 1) % 2
                await self.player1_class.queue()
                await self.player2_class.queue()
                user_id_1 = self.players[self.current_player].player_call.from_user.id
                user_id_2 = self.players[self.current_player - 1].player_call.from_user.id
                TIMERS[user_id_1] = asyncio.get_event_loop().call_later(self.timer_time, self.timeout, user_id_1)
                TIMERS[user_id_2].cancel()
                del TIMERS[user_id_2]
                await self.drawing_field_for_players()
            else:
                if await self.check_field_and_adjust_needed(x, y):
                    # отрисовываю поле челу который стреляет
                    # тип если попал то ничего кроме отрисовки не происходит и юзер1 продолжает ходить
                    user_id_1 = self.players[self.current_player].player_call.from_user.id
                    TIMERS[user_id_1].cancel()
                    TIMERS[user_id_1] = asyncio.get_event_loop().call_later(self.timer_time, self.timeout, user_id_1)
                    await self.drawing_field_for_players()
                else:
                    self.current_player = (self.current_player + 1) % 2
                    await self.player1_class.queue()
                    await self.player2_class.queue()
                    user_id_1 = self.players[self.current_player].player_call.from_user.id
                    user_id_2 = self.players[self.current_player - 1].player_call.from_user.id
                    TIMERS[user_id_1] = asyncio.get_event_loop().call_later(self.timer_time, self.timeout, user_id_1)
                    TIMERS[user_id_2].cancel()
                    del TIMERS[user_id_2]
                    await self.drawing_field_for_players()

    async def swap(self):
        self.current_player = (self.current_player + 1) % 2
        await self.player1_class.queue()
        await self.player2_class.queue()
        user_id_1 = self.players[self.current_player].player_call.from_user.id
        user_id_2 = self.players[self.current_player - 1].player_call.from_user.id
        TIMERS[user_id_1] = asyncio.get_event_loop().call_later(self.timer_time, self.timeout, user_id_1)
        TIMERS[user_id_2].cancel()
        del TIMERS[user_id_2]
        await self.drawing_field_for_players()

    def timeout(self, user_id):
        global TIMERS
        self.ignored[self.current_player] += 1
        self.history.append(f'-(-;-) - {self.players[self.current_player].name}')
        if self.ignored[self.current_player] >= 3:
            del TIMERS[user_id]
            asyncio.get_event_loop().create_task(self.logic_of_victory_and_defeat(self.players[self.current_player]))
            return

        asyncio.get_event_loop().create_task(self.swap())

    # Изменение поля
    async def check_field_and_adjust_needed(self, x, y, super_weapon=None):
        board = self.players[self.current_player - 1].board
        # Если попал в воду
        if board[x][y] == 0:
            self.history.append(f'✖️({y + 1};{x + 1}) 🔫 {self.players[self.current_player].name}')
            board[x][y] = 7
            return False

        # Некоректный выстрел
        elif board[x][y] in [5, 6, 7]:
            return True

        # Поподание по кораблю
        elif board[x][y] in [1, 2, 3, 4]:
            # Погиб ли корабль
            flag = await self.checking_the_sinking(x, y, board)
            hints = self.players[self.current_player - 1].hints
            if flag:
                # Если погиб
                self.players[self.current_player - 1].living_ships.remove(board[x][y])
                board[x][y] = 6
                self.history.append(f'❌({y + 1};{x + 1}) 🔫 {self.players[self.current_player].name}')
                # Цикл уничтожения корабля
                await self.changing_the_circle(x, y, board, hints)
                return True
            # Если выжил то ранен
            board[x][y] = 5
            self.history.append(f'⭕️({y + 1};{x + 1}) 🔫 {self.players[self.current_player].name}')
            # Если есть подсказки то отмечаются места по которы содить нельзя
            if hints:
                for i in range(-1, 2, 2):
                    for j in range(-1, 2, 2):
                        board[x + i][y + j] = 7
            return True

    # Проверка погиб ли корабль
    async def checking_the_sinking(self, x, y, field):
        # Все возможные места корабля
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        size = len(field)
        for dx, dy in directions:
            for i in range(1, field[x][y]):
                nx, ny = x + i * dx, y + i * dy
                if not (0 <= nx < size and 0 <= ny < size):
                    break
                if field[nx][ny] == 0 or field[nx][ny] == 7:
                    break
                if field[nx][ny] in [2, 3, 4]:
                    return False
        return True

    # Полное уничтожение корабля
    async def changing_the_circle(self, x, y, field, hints):
        size = len(field)
        for i in range(-1, 2):
            for j in range(-1, 2):
                new_x = x + i
                new_y = y + j
                if 0 <= new_x < size and 0 <= new_y < size:
                    if field[new_x][new_y] == 5:
                        field[new_x][new_y] = 6
                        await self.changing_the_circle(new_x, new_y, field, hints)
                    if hints:
                        if field[new_x][new_y] == 0:
                            field[new_x][new_y] = 7

    # Логика поражения/победы
    # Поступает класс проигравшего =Ю второй игрок выигрывает
    async def logic_of_victory_and_defeat(self, player):
        if player == self.player1_class:
            if self.player2_class:
                await self.player2_class.victory()
                await self.player1_class.defeat()
            else:
                await self.player1_class.defeat_without_penalties()
        else:
            await self.player1_class.victory()
            await self.player2_class.defeat()

        global PLAYERS_IN_GAME
        global GAME_SEARCH
        global ACTIVE_GAMES
        for p in self.players:
            PLAYERS_IN_GAME.pop(p.user_id)
            if p.user_id in TIMERS:
                TIMERS[p.user_id].cancel()
                del TIMERS[p.user_id]
            await p.delete()
        if self in GAME_SEARCH:
            GAME_SEARCH.remove(self)
        if self in ACTIVE_GAMES:
            ACTIVE_GAMES.remove(self)

        await self.delete_game()

    # Отправляем команду о том что нужно нарисовать поле
    async def drawing_field_for_players(self):
        player1_name = f'<a href="tg://user?id={self.player1_class.player_call.from_user.id}">{self.player1_class.player_call.from_user.first_name}</a>'
        player2_name = f'<a href="tg://user?id={self.player2_class.player_call.from_user.id}">{self.player2_class.player_call.from_user.first_name}</a>'
        player1_field = self.player1_class.board
        player2_field = self.player2_class.board
        player1 = [player1_name, player1_field]
        player2 = [player2_name, player2_field]
        last_move = self.history[-1]
        await self.player1_class.field_fight_rendering(player2, player1, last_move, difficulty=7)
        await self.player2_class.field_fight_rendering(player1, player2, last_move, difficulty=7)

    # Считает количество активных игроков
    async def active_people(self):
        a = -1
        for i in self.players:
            if i:
                a += 1
        return a

    # Удаление игры
    async def delete_game(self):
        del self


# Класс описывающий алгоритм
class Algorithm:
    CELL_TYPE = ["🟦", "⛵", "🚤", "⛴", "🚢", "⭕️", "❌", "✖️"]

    def __init__(self, size=8):
        self.size = size
        self.field = []
        self.name = '<a href="https://t.me/Im_a_real_bot">Bot</a>'

    async def algorithm_motion(self, field, living_ships, complexity, size):
        x, y = -1, -1
        self.size = size
        if complexity == 1 or complexity == 4:
            for i in range(8):
                for j in range(8):
                    if field[i][j] == 5:
                        for z in range(-1, 2, 2):
                            if field[i + z][j] < 5 and (i + z) < 8 and j < 8:
                                return i + z, j
                            if field[i][j + z] < 5 and (j + z) < 8 and i < 8:
                                return i, j + z

            while True:
                x, y = random.randint(0, 7), random.randint(0, 7)
                if field[x][y] in [0, 1, 2, 3, 4]:
                    break

        elif complexity == 2 or complexity == 5:
            x, y = await self.difficult_move(field, living_ships, False)

        elif complexity == 3 or complexity == 6:
            x, y = await self.difficult_move(field, living_ships)
        return x, y

    async def difficult_move(self, field, living_ships, complexity=True):
        weight = await self.creates_the_coefficient_field(field, living_ships, complexity)
        max_cell = await self.cell_selection(weight)
        for x, y in max_cell:
            if field[x][y] in [5, 6, 7]:
                continue
            print(x, y)
            return x, y

    async def cell_selection(self, weight):
        cells = {}
        max_cells = 0
        for x in range(self.size):
            for y in range(self.size):
                if weight[x][y] > max_cells:
                    max_cells = weight[x][y]
                cells.setdefault(weight[x][y], []).append((x, y))
        return cells[max_cells]

    async def creates_the_coefficient_field(self, field, living_ships, complexity):
        weight = [[1 for _ in range(self.size)] for _ in range(self.size)]
        for x in range(self.size):
            for y in range(self.size):
                if field[x][y] == 5:
                    if complexity:
                        for ship in living_ships:
                            await self.will_it_fit(ship, x, y, field, weight, complexity)
                    weight[x][y] = 0
                    for i in range(max(0, x - 1), min(x + 2, self.size)):
                        for j in range(max(0, y - 1), min(y + 2, self.size)):
                            if i == x and j == y:
                                continue
                            if i != x and j != y:
                                weight[i][j] = 0
                            else:
                                weight[i][j] *= 500
                elif field[x][y] == 6:
                    x_min = max(x - 1, 0)
                    x_max = min(x + 1, self.size - 1)
                    y_min = max(y - 1, 0)
                    y_max = min(y + 1, self.size - 1)

                    for i in range(x_min, x_max + 1):
                        for j in range(y_min, y_max + 1):
                            weight[i][j] = 0

        for ship in living_ships:
            hits = [5, 6, 7]
            for y in range(self.size):
                for x in range(self.size):
                    if field[x][y] in hits:
                        weight[x][y] = 0
                    else:
                        await self.will_it_fit(ship, x, y, field, weight, complexity)
        return weight

    async def will_it_fit(self, ship, x, y, field, weight, complexity):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dx, dy in directions:
            ship_length = 0
            for i in range(ship):
                nx, ny = x + i * dx, y + i * dy
                if not (0 <= nx < self.size and 0 <= ny < self.size):
                    break
                if field[nx][ny] in [5, 6, 7]:
                    break
                if weight[nx][ny] <= 0:
                    break
                ship_length += 1
            if ship_length == ship:
                if complexity:
                    for i in range(ship):
                        nx, ny = x + i * dx, y + i * dy
                        weight[nx][ny] += 1
                else:
                    weight[x][y] += 1

        # Возвращает клетки подбитые супероружием

    async def damage_algorithm_handler(self, type_of_weapon, field):
        damage = []
        if type_of_weapon == 2:
            max_count = 0
            # Ищем подматрицу 3x3 с максимальным количеством чисел от 0 до 4 включительно
            for i in range(6):
                for j in range(6):
                    submatrix = [row[j:j + 3] for row in field[i:i + 3]]
                    submatrix_count = sum(1 for row in submatrix for num in row if 0 <= num <= 4)
                    if submatrix_count > max_count:
                        max_count = submatrix_count
                        damage = [(i + k, j + l) for k in range(3) for l in range(3)]

        elif type_of_weapon == 3:
            where_to_hit = []
            for i in field:
                a = 0
                for j in i:
                    if j in [0, 1, 2, 3, 4]:
                        a += 1
                where_to_hit.append(a)
            max_value = max(where_to_hit)
            max_index = where_to_hit.index(max_value)
            x, y = max_index, 0
            for i in range(-8, 8):
                if 0 <= (y + i) < self.size:
                    damage.append([x, y + i])
                if y + i > self.size:
                    break

        elif type_of_weapon == 4:
            max_count = 0
            # Ищем подматрицу 5x5 с максимальным количеством чисел от 0 до 4 включительно
            for i in range(4):
                for j in range(4):
                    submatrix = [row[j:j + 5] for row in field[i:i + 5]]
                    submatrix_count = sum(1 for row in submatrix for num in row if 0 <= num <= 4)
                    if submatrix_count > max_count:
                        max_count = submatrix_count
                        damage = [(i + k, j + l) for k in range(5) for l in range(5)]

        return damage


# Класс описывающий игру с ботом
class GameAlgorithm(Game):
    SHIP_SIZES = {6: [4, 3, 2, 1], 8: [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]}

    def __init__(self, bot, dp, con, player1_class, algorithm, difficulty, field_algorithm):
        super().__init__(bot, dp, con, player1_class, algorithm, 60)  # Вызов конструктора суперкласса
        global ACTIVE_GAMES
        self.difficulty = int(difficulty)
        difficulty_to_time = {
            1: 60,
            2: 30,
            3: 10,
            4: 60,
            5: 30,
            6: 10,
        }
        self.timer_time = difficulty_to_time[self.difficulty]
        print(self.timer_time)
        self.field_algorithm = deepcopy(field_algorithm)
        self.size = 8
        self.current_player = 1
        self.algorithm_flag = True
        self.algorithm_living_ships = deepcopy(self.SHIP_SIZES[self.size])
        self.ignored = 0
        ACTIVE_GAMES.append(self)
        user_id = self.player1_class.player_call.from_user.id
        TIMERS[user_id] = asyncio.get_event_loop().call_later(self.timer_time, self.timeout, user_id)
        print(TIMERS, 'глав Таймер')
        print(self.SHIP_SIZES)
        pprint(self.field_algorithm)
        print('Обновление игры')

    # Сам процесс игры
    async def start_game(self, x, y, super_weapon=None, super_weapon_type=0):
        # Если это выстрел супер оружия то ход не засчитывается
        self.ignored = 0
        print("ignored:", self.ignored)
        if super_weapon:
            # Проходим по всем клеткам пораженным супер оружием и отмечает их
            for i in super_weapon:
                x, y = i
                if await self.check_field_and_adjust_needed_for_algorithm(x, y, super_weapon_type):
                    # отрисовываю поле челу который стреляет
                    # тип если попал то ничего кроме отрисовки не происходит и юзер1 продолжает ходить
                    if not self.algorithm_living_ships:
                        await self.logic_of_victory_and_defeat(self.algorithm)
            if self.algorithm_living_ships:
                self.current_player = (self.current_player + 1) % 2
                await self.player1_class.queue()
                user_id_1 = self.player1_class.player_call.from_user.id
                TIMERS[user_id_1].cancel()
                del TIMERS[user_id_1]
                await self.drawing_field_for_players()
                # цикл опроса бота
                # и как раз тут по идее должен быть опрос противника
                # функция должна возвращать х и у кнопки противника и при этом надо вернуть попал ли противник
                while True:
                    if self in ACTIVE_GAMES:
                        if self.current_player or not self.player1_class.living_ships:
                            break
                        player_field = self.player1_class.board
                        living_player_ships = self.player1_class.living_ships
                        await asyncio.sleep(2)
                        if not random.randint(0, 10 - self.difficulty) and self.difficulty > 3:
                            super_weapon_type = random.randint(2, 4)
                            damage = await self.algorithm.damage_algorithm_handler(super_weapon_type, player_field)
                            for i in damage:
                                x, y = i
                                await self.check_field_and_adjust_needed_for_algorithm(x, y, super_weapon_type)
                            self.current_player = (self.current_player + 1) % 2
                            await self.player1_class.queue()
                            if self in ACTIVE_GAMES:
                                print(TIMERS, 'Таймер переход')
                                user_id_1 = self.player1_class.player_call.from_user.id
                                TIMERS[user_id_1] = asyncio.get_event_loop().call_later(self.timer_time, self.timeout,
                                                                                        user_id_1)
                                await self.drawing_field_for_players()
                            break
                        else:
                            x, y = await self.algorithm.algorithm_motion(player_field, living_player_ships,
                                                                         self.difficulty, self.size)

                            if await self.check_field_and_adjust_needed_for_algorithm(x, y):
                                if self in ACTIVE_GAMES:
                                    await self.drawing_field_for_players()
                            else:
                                # если не попал
                                self.current_player = (self.current_player + 1) % 2
                                await self.player1_class.queue()
                                if self in ACTIVE_GAMES:
                                    print(TIMERS, 'Таймер переход')
                                    user_id_1 = self.player1_class.player_call.from_user.id
                                    TIMERS[user_id_1] = asyncio.get_event_loop().call_later(self.timer_time,
                                                                                            self.timeout, user_id_1)
                                    await self.drawing_field_for_players()
                                    break

                    else:
                        break
        else:
            user_id_1 = self.player1_class.player_call.from_user.id
            TIMERS[user_id_1].cancel()
            del TIMERS[user_id_1]
            if await self.check_field_and_adjust_needed_for_algorithm(x, y):
                # отрисовываю поле челу который стреляет
                # тип если попал то ничего кроме отрисовки не происходит и юзер1 продолжает ходить
                if self.algorithm_living_ships:
                    print(TIMERS, 'Таймер новый ход')
                    TIMERS[user_id_1] = asyncio.get_event_loop().call_later(self.timer_time, self.timeout, user_id_1)
                    await self.drawing_field_for_players()
                else:
                    print(TIMERS, 'Таймер ход алго')
                    await self.logic_of_victory_and_defeat(self.algorithm)
            else:
                self.current_player = (self.current_player + 1) % 2
                await self.player1_class.queue()
                await self.drawing_field_for_players()
                # цикл опроса бота
                # и как раз тут по идее должен быть опрос противника
                # функция должна возвращать х и у кнопки противника и при этом надо вернуть попал ли противник
                while True:
                    if self in ACTIVE_GAMES:
                        if self.current_player or not self.player1_class.living_ships:
                            break
                        player_field = self.player1_class.board
                        living_player_ships = self.player1_class.living_ships
                        await asyncio.sleep(2)
                        if not random.randint(0, 10 - self.difficulty) and self.difficulty > 3:
                            super_weapon_type = random.randint(2, 4)
                            damage = await self.algorithm.damage_algorithm_handler(super_weapon_type, player_field)
                            for i in damage:
                                x, y = i
                                await self.check_field_and_adjust_needed_for_algorithm(x, y, super_weapon_type)
                            self.current_player = (self.current_player + 1) % 2
                            await self.player1_class.queue()
                            if self in ACTIVE_GAMES:
                                user_id_1 = self.player1_class.player_call.from_user.id
                                TIMERS[user_id_1] = asyncio.get_event_loop().call_later(self.timer_time,
                                                                                        self.timeout, user_id_1)
                                await self.drawing_field_for_players()
                            break
                        else:
                            x, y = await self.algorithm.algorithm_motion(player_field, living_player_ships,
                                                                         self.difficulty, self.size)

                            if await self.check_field_and_adjust_needed_for_algorithm(x, y):
                                if self in ACTIVE_GAMES:
                                    print(TIMERS)
                                    await self.drawing_field_for_players()
                            else:
                                # если не попал
                                self.current_player = (self.current_player + 1) % 2
                                await self.player1_class.queue()
                                if self in ACTIVE_GAMES:
                                    user_id_1 = self.player1_class.player_call.from_user.id
                                    TIMERS[user_id_1] = asyncio.get_event_loop().call_later(self.timer_time,
                                                                                            self.timeout, user_id_1)

                                    await self.drawing_field_for_players()
                                    break
                    else:
                        break

    async def swap(self):
        self.current_player = (self.current_player + 1) % 2
        await self.player1_class.queue()
        await self.drawing_field_for_players()
        user_id_1 = self.player1_class.player_call.from_user.id
        TIMERS[user_id_1].cancel()
        del TIMERS[user_id_1]
        while True:
            if self in ACTIVE_GAMES:
                if self.current_player or not self.player1_class.living_ships:
                    break
                player_field = self.player1_class.board
                living_player_ships = self.player1_class.living_ships
                await asyncio.sleep(2)
                if not random.randint(0, 10 - self.difficulty) and self.difficulty > 3:
                    super_weapon_type = random.randint(2, 4)
                    damage = await self.algorithm.damage_algorithm_handler(super_weapon_type, player_field)
                    for i in damage:
                        x, y = i
                        await self.check_field_and_adjust_needed_for_algorithm(x, y, super_weapon_type)
                    self.current_player = (self.current_player + 1) % 2
                    await self.player1_class.queue()
                    if self in ACTIVE_GAMES:
                        await self.drawing_field_for_players()
                    break
                else:
                    x, y = await self.algorithm.algorithm_motion(player_field, living_player_ships,
                                                                 self.difficulty, self.size)

                    if await self.check_field_and_adjust_needed_for_algorithm(x, y):
                        if self in ACTIVE_GAMES:
                            print(TIMERS)
                            await self.drawing_field_for_players()
                    else:
                        # если не попал
                        self.current_player = (self.current_player + 1) % 2
                        await self.player1_class.queue()
                        if self in ACTIVE_GAMES:
                            user_id_1 = self.player1_class.player_call.from_user.id
                            TIMERS[user_id_1] = asyncio.get_event_loop().call_later(self.timer_time,
                                                                                    self.timeout, user_id_1)

                            await self.drawing_field_for_players()
                            break
            else:
                break

    def timeout(self, user_id):
        global TIMERS
        self.ignored += 1
        self.history.append(f'-(-;-) - {self.player1_class.name}')
        # даём возможность алгоритму разбить наше поле, даже если мы полностью его игнорим (более 3 раз подряд)
        # if self.ignored >= 3:
        #     del TIMERS[user_id]
        #     asyncio.get_event_loop().create_task(self.logic_of_victory_and_defeat(self.player1_class))
        #     return

        asyncio.get_event_loop().create_task(self.swap())

    async def check_field_and_adjust_needed_for_algorithm(self, x, y, super=0):
        if self.current_player:
            board = self.field_algorithm
            # Если попал в воду
            if board[x][y] == 0:
                self.history.append(f'✖️({y + 1};{x + 1}) {self.ARSENAL[super]} {self.player1_class.name}')
                board[x][y] = 7
                return False

            # Некоректный выстрел
            elif board[x][y] in [5, 6, 7]:
                return True

            # Поподание по кораблю
            elif board[x][y] in [1, 2, 3, 4]:
                # Погиб ли корабль
                flag = await self.checking_the_sinking(x, y, board)
                hints = self.player1_class.hints
                if flag:
                    # Если погиб
                    self.algorithm_living_ships.remove(board[x][y])
                    board[x][y] = 6
                    self.history.append(f'❌({y + 1};{x + 1}) {self.ARSENAL[super]} {self.player1_class.name}')
                    # Цикл уничтожения корабля
                    await self.changing_the_circle(x, y, board, hints)
                    return True
                # Если выжил то ранен
                board[x][y] = 5
                self.history.append(f'⭕️({y + 1};{x + 1}) {self.ARSENAL[super]} {self.player1_class.name}')
                # Если есть подсказки то отмечаются места по которы содить нельзя
                if hints:
                    for i in range(-1, 2, 2):
                        for j in range(-1, 2, 2):
                            board[x + i][y + j] = 7
                return True
        else:
            board = self.player1_class.board
            # Если попал в воду
            if board[x][y] == 0:
                self.history.append(f'✖️({y + 1};{x + 1}) {self.ARSENAL[super]} {self.algorithm.name}')
                board[x][y] = 7
                return False

            # Некоректный выстрел
            elif board[x][y] in [5, 6, 7]:
                return True

            # Поподание по кораблю
            elif board[x][y] in [1, 2, 3, 4]:
                # Погиб ли корабль
                flag = await self.checking_the_sinking(x, y, board)
                hints = True
                if flag:
                    # Если погиб
                    self.player1_class.living_ships.remove(board[x][y])
                    board[x][y] = 6
                    self.history.append(f'❌({y + 1};{x + 1}) {self.ARSENAL[super]} {self.algorithm.name}')
                    # Цикл уничтожения корабля
                    await self.changing_the_circle(x, y, board, hints)
                    return True
                # Если выжил то ранен
                board[x][y] = 5
                self.history.append(f'⭕️({y + 1};{x + 1}) {self.ARSENAL[super]} {self.algorithm.name}')
                # Если есть подсказки то отмечаются места по которы содить нельзя
                if hints:
                    for i in range(-1, 2, 2):
                        for j in range(-1, 2, 2):
                            board[x + i][y + j] = 7
                return True

    async def drawing_field_for_players(self):
        player1_name = f'<a href="tg://user?id={self.player1_class.player_call.from_user.id}' \
                       f'">{self.player1_class.player_call.from_user.first_name}</a>'
        player2_name = self.algorithm.name
        player1_field = self.player1_class.board
        player2_field = self.field_algorithm
        player1 = [player1_name, player1_field]
        player2 = [player2_name, player2_field]
        last_move = self.history[-1]
        await self.player1_class.field_fight_rendering(player2, player1, last_move, self.difficulty)

    async def logic_of_victory_and_defeat(self, player):
        if player == self.player1_class:
            await self.player1_class.defeat(algorithm=True)
        else:
            await self.player1_class.victory(algorithm=True, difficulty=self.difficulty)

        global PLAYERS_IN_GAME
        global ACTIVE_GAMES
        global TIMERS
        user_id = self.player1_class.user_id
        if user_id in TIMERS:
            TIMERS[user_id].cancel()
            del TIMERS[user_id]
        ACTIVE_GAMES.remove(self)
        for p in self.players:
            PLAYERS_IN_GAME.pop(p.user_id)
            await p.delete()

        await self.delete_algorithm_game()

    async def active_people(self):
        a = 0
        return a

    # Удаление игры с алгоритмом
    async def delete_algorithm_game(self):
        del self


# Стартовое меню Стартовое меню Стартовое меню Стартовое меню
# Стартовое меню Стартовое меню Стартовое меню Стартовое меню
# Стартовое меню Стартовое меню Стартовое меню Стартовое меню
# Стартовое меню по команде
@dp.message_handler(commands=['start'])
async def menu_by_command(message: types.Message, state: FSMContext):
    is_new_user = await check_user_from_db(message.from_user.id, con)
    # проверка на наличие юзера в бд и добавление его туда
    await check_and_add_user_from_db(message.from_user.id, "en", con)
    # получение языка пользователя
    lang_code = await getting_the_language_message(message, state, con)
    # Доп функции по ссылке
    print(f"Start pressed by user {message.from_user.id}")
    link = message.text.replace('/start', '')
    if link:
        print(f"It is deeplink")
        link_inf = link.split('_')
        if link_inf[0] == ' replenishment' and is_new_user:
            text_menu = LANGUAGE[lang_code]['menu']
            await changing_balance(message.from_user.id, 1000, con)
            await changing_balance(link_inf[1], 1000, con)
            await bot.send_message(message.from_user.id, text_menu[7])
            await bot.send_message(link_inf[1], text_menu[7])
        elif link_inf[0] == ' battle':
            try:
                friend_id = int(link_inf[1])
            except ValueError:
                pass
            else:
                await state.update_data(friend=friend_id)

    text_menu = LANGUAGE[lang_code]['menu'][0].format(name=message.from_user.first_name)
    text = LANGUAGE[lang_code]['menu']
    # добавление кнопок навигации в меню
    markup = types.InlineKeyboardMarkup()
    # Правила
    markup.row(types.InlineKeyboardButton(text=text[1], callback_data=f"rules_call"))
    # Настройки
    markup.row(types.InlineKeyboardButton(text=text[2], callback_data=f"settings_call"))
    # Профиль
    markup.row(types.InlineKeyboardButton(text=text[3], callback_data=f"profile_call"))
    # топы
    markup.row(types.InlineKeyboardButton(text=text[8], callback_data=f"top_human"))
    # Выбор режима боя с ботом, а именно выбор сложности
    markup.row(types.InlineKeyboardButton(text=text[4], callback_data=f"difficulty_selection_call"))
    # Игра против друга
    markup.row(types.InlineKeyboardButton(text=text[5], callback_data=f"fight_with_friend_call"))
    # Игра со случайным пользователем
    markup.row(types.InlineKeyboardButton(text=text[6], callback_data=f"fight_with_man_call"))
    # ответ пользователю
    await bot.send_message(message.from_user.id, text=text_menu, reply_markup=markup)


# Стартовое меню по кнопке
@dp.callback_query_handler(Text(startswith='start_call'))
async def menu_by_button(call: types.CallbackQuery, state: FSMContext):
    # получение языка пользователя
    lang_code = await getting_the_language_call(call, state, con)
    text_menu = LANGUAGE[lang_code]['menu'][0].format(name=call.from_user.first_name)
    text = LANGUAGE[lang_code]['menu']
    # добавление кнопок навигации в меню
    markup = types.InlineKeyboardMarkup()
    # Правила
    markup.row(types.InlineKeyboardButton(text=text[1], callback_data=f"rules_call"))
    # Настройки
    markup.row(types.InlineKeyboardButton(text=text[2], callback_data=f"settings_call"))
    # Профиль
    markup.row(types.InlineKeyboardButton(text=text[3], callback_data=f"profile_call"))
    # топы
    markup.row(types.InlineKeyboardButton(text=text[8], callback_data=f"top_human"))
    # Выбор режима боя с ботом, а именно выбор сложности
    markup.row(types.InlineKeyboardButton(text=text[4], callback_data=f"difficulty_selection_call"))
    # Игра против друга
    markup.row(types.InlineKeyboardButton(text=text[5], callback_data=f"fight_with_friend_call"))
    # Игра со случайным пользователем
    markup.row(types.InlineKeyboardButton(text=text[6], callback_data=f"fight_with_man_call"))
    # ответ пользователю
    await call.message.edit_text(text=text_menu, reply_markup=markup)


# Переходник для удаления игрока нажавшего возврат в меню
@dp.callback_query_handler(Text(startswith='start_adapter_call'))
async def adapter_for_removing_player(call: types.CallbackQuery, state: FSMContext):
    game = PLAYERS_IN_GAME[call.from_user.id].game
    if await PLAYERS_IN_GAME[call.from_user.id].game.active_people():
        await game.delete_game()
        await PLAYERS_IN_GAME[call.from_user.id].delete()
        PLAYERS_IN_GAME.pop(call.from_user.id)
        await menu_by_button(call, state)
    else:
        if game in GAME_SEARCH:
            GAME_SEARCH.remove(game)
        await game.delete_game()
        await PLAYERS_IN_GAME[call.from_user.id].delete()
        PLAYERS_IN_GAME.pop(call.from_user.id)
        await menu_by_button(call, state)


# Правила Правила Правила Правила
# Правила Правила Правила Правила
# Правила Правила Правила Правила
# Меню правил по кнопке
@dp.callback_query_handler(text='rules_call')
async def rules_by_button(call: types.CallbackQuery, state: FSMContext):
    # получение языка пользователя
    lang_code = await getting_the_language_call(call, state, con)
    text_menu = LANGUAGE[lang_code]['rules_menu'][0]
    text = LANGUAGE[lang_code]['rules_menu']
    # создание кнопок
    markup = types.InlineKeyboardMarkup()
    # Правила: Подготовка к игре
    markup.row(types.InlineKeyboardButton(text=text[1], callback_data=f"call_rules_0"))
    # Правила: Ход игры
    markup.row(types.InlineKeyboardButton(text=text[2], callback_data=f"call_rules_1"))
    # Правила: Обозначения
    markup.row(types.InlineKeyboardButton(text=text[3], callback_data=f"call_rules_2"))
    # Назад в меню
    markup.row(types.InlineKeyboardButton(text=text[4], callback_data=f"start_call"))
    await call.message.edit_text(text=text_menu, reply_markup=markup)


# Общее меню для всех вкладок правил
@dp.callback_query_handler(Text(startswith='call_rules'))
async def rules_of_preparation(call: types.CallbackQuery, state: FSMContext):
    # все вкладки правил
    lang_code = await getting_the_language_call(call, state, con)
    text = LANGUAGE[lang_code]['rules']
    # создание кнопок
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(text=text[3], callback_data=f"rules_call"))
    # ответ в зависимости от нажатой кнопки
    await call.message.edit_text(text=text[int(call.data.split("_")[2])], reply_markup=markup)


# Настройки Настройки Настройки Настройки
# Настройки Настройки Настройки Настройки
# Настройки Настройки Настройки Настройки
# Меню настроек
@dp.message_handler(commands=['settings'])
async def settings_command(message: types.Message, state: FSMContext):
    # получение инфы о подсказках из бд
    hint = await need_a_hint(message.from_user.id, con)
    # определение языка
    lang_code = await getting_the_language_message(message, state, con)
    text = LANGUAGE[lang_code]['settings']
    # Создание текста кнопок под настройки
    if lang_code == 'en':
        text_ru = LANGUAGE[lang_code]['settings'][1].format(name='☑️')
        text_en = LANGUAGE[lang_code]['settings'][2].format(name='✅')
    else:
        text_ru = LANGUAGE[lang_code]['settings'][1].format(name='✅')
        text_en = LANGUAGE[lang_code]['settings'][2].format(name='☑️')

    if hint:
        text_hint = LANGUAGE[lang_code]['settings'][3].format(name='✅')
    else:
        text_hint = LANGUAGE[lang_code]['settings'][3].format(name='☑️')

    # Создание кнопок
    markup = types.InlineKeyboardMarkup()
    # Выбор языка
    markup.row(types.InlineKeyboardButton(text=text_ru, callback_data=f"settings_call_ru"),
               types.InlineKeyboardButton(text=text_en, callback_data=f"settings_call_en"))
    # Выбор подсказок
    markup.row(types.InlineKeyboardButton(text=text_hint, callback_data=f"settings_call_hint_on_off"))
    markup.row(types.InlineKeyboardButton(text=text[4], callback_data=f"start_call"))
    try:
        try:
            await message.edit_text(text[0], reply_markup=markup)
        except MessageNotModified:
            ...
    except MessageCantBeEdited:
        await message.answer(text[0], reply_markup=markup)


# Меню настроек по кнопке
@dp.callback_query_handler(Text(startswith='settings_call'))
async def settings_by_button(call: types.CallbackQuery, state: FSMContext):
    hint = await need_a_hint(call.from_user.id, con)
    # Обнавление языка
    if call.data == "settings_call_ru":
        lang_code = 'ru'
        await state.update_data(lang=lang_code)
        await post_user_language(call.from_user.id, lang_code, con)
    elif call.data == "settings_call_en":
        lang_code = 'en'
        await state.update_data(lang=lang_code)
        await post_user_language(call.from_user.id, lang_code, con)
    # ОБновление подсказок
    elif call.data == "settings_call_hint_on_off":
        if hint:
            hint = False
            await update_hint(call.from_user.id, hint, con)
        else:
            hint = True
            await update_hint(call.from_user.id, hint, con)
    # Определение языка
    lang_code = await getting_the_language_call(call, state, con)
    text = LANGUAGE[lang_code]['settings']
    # Создание текста кнопок под настройки
    if lang_code == 'en':
        text_ru = LANGUAGE[lang_code]['settings'][1].format(name='☑️')
        text_en = LANGUAGE[lang_code]['settings'][2].format(name='✅')
    else:
        text_ru = LANGUAGE[lang_code]['settings'][1].format(name='✅')
        text_en = LANGUAGE[lang_code]['settings'][2].format(name='☑️')
    if hint:
        text_hint_on_off = LANGUAGE[lang_code]['settings'][3].format(name='✅')
    else:
        text_hint_on_off = LANGUAGE[lang_code]['settings'][3].format(name='☑️')
    # Создание кнопок
    markup = types.InlineKeyboardMarkup()
    # Выбор языка
    markup.row(types.InlineKeyboardButton(text=text_ru, callback_data=f"settings_call_ru"),
               types.InlineKeyboardButton(text=text_en, callback_data=f"settings_call_en"))
    # Выбор подсказок
    markup.row(types.InlineKeyboardButton(text=text_hint_on_off, callback_data=f"settings_call_hint_on_off"))
    markup.row(types.InlineKeyboardButton(text=text[4], callback_data=f"start_call"))
    try:
        await call.message.edit_text(text[0], reply_markup=markup)
    except MessageNotModified:
        ...


# Профиль Профиль Профиль Профиль
# Профиль Профиль Профиль Профиль
# Профиль Профиль Профиль Профиль
# Профиль игрока
@dp.callback_query_handler(text='profile_call')
async def profile(call: types.CallbackQuery, state: FSMContext):
    kills_death = 0

    # определение языка
    lang_code = await getting_the_language_call(call, state, con)
    text = LANGUAGE[lang_code]['profile']

    # Создание кнопок с возможностями статистики
    markup = types.InlineKeyboardMarkup()
    # Пополнение баланса
    markup.row(types.InlineKeyboardButton(text=text[3], callback_data=f"replenishment_balance"))
    # Детальная статистика
    markup.row(types.InlineKeyboardButton(text=text[1], callback_data=f"detailed_statistics_call"))
    # Возврат в меню
    markup.row(types.InlineKeyboardButton(text=text[2], callback_data=f"start_call"))

    # получение  инфы о юзере
    all_us = await about_the_user(call.from_user.id, con)
    balance = all_us[1][0]
    all_us = all_us[0]
    # Создание рейтинга
    if all_us[2] or all_us[4]:
        kills_death = int(((all_us[2] + all_us[4]) / (all_us[1] + all_us[3])) * 100)
    text_osn = LANGUAGE[lang_code]['profile'][0].format(
        name=f'<a href="tg://user?id={call.from_user.id}">{call.from_user.first_name}</a>',
        id=call.from_user.id,
        share_of_wins=kills_death,
        wins=all_us[2] + all_us[4],
        defeats=all_us[1] + all_us[3] - all_us[2] - all_us[4],
        balance=balance)
    await call.message.edit_text(text=text_osn, reply_markup=markup, parse_mode='HTML')


# Детальная статистика
@dp.callback_query_handler(text='detailed_statistics_call')
async def detailed_statistics(call: types.CallbackQuery, state: FSMContext):
    # определение языка
    lang_code = await getting_the_language_call(call, state, con)
    text = LANGUAGE[lang_code]['statistics']

    # Возврат к профилю
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(text=text[1], callback_data=f"profile_call"))

    # получение  инфы о юзере
    kills_death = 0
    kills_death_people = 0
    kills_death_algorithm = 0
    all_us = await about_the_user(call.from_user.id, con)
    all_us = all_us[0]
    if all_us[2] or all_us[4]:
        kills_death = int(((all_us[2] + all_us[4]) / (all_us[1] + all_us[3])) * 100)
    if all_us[2]:
        kills_death_people = int((all_us[2] / all_us[1]) * 100)
    if all_us[3]:
        kills_death_algorithm = int((all_us[4] / all_us[3]) * 100)
    text_osn = LANGUAGE[lang_code]['statistics'][0].format(
        name=f'<a href="tg://user?id={call.from_user.id}">{call.from_user.first_name}</a>',
        id=call.from_user.id,
        victories_against_people=all_us[2],
        defeats_against_people=all_us[1] - all_us[2],
        playing_with_person=all_us[1],
        share_of_wins_against_people=kills_death_people,
        victories_against_algorithm=all_us[4],
        defeats_against_algorithm=all_us[3] - all_us[4],
        playing_with_bot=all_us[3],
        share_of_wins_against_algorithm=kills_death_algorithm,
        wins=all_us[2] + all_us[4],
        defeats=all_us[1] + all_us[3] - all_us[2] - all_us[4],
        total_games_played=all_us[1] + all_us[3],
        share_of_wins=kills_death)
    await call.message.edit_text(text=text_osn, reply_markup=markup, parse_mode='HTML')


# Пополнение баланса
# Детальная статистика
@dp.callback_query_handler(text='replenishment_balance')
async def replenishment_balance(call: types.CallbackQuery, state: FSMContext):
    # создание ссылки
    link = f"<code>https://t.me/OceanicBattleBot?start=replenishment_{call.from_user.id}</code>"
    # определение языка
    lang_code = await getting_the_language_call(call, state, con)
    text = LANGUAGE[lang_code]['replenishment_balance']
    text_osn = text[0].format(link=link)
    # Возврат к профилю
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(text=text[1], callback_data=f"profile_call"))
    await call.message.edit_text(text=text_osn, reply_markup=markup, parse_mode="HTML")


# Бой Бой Бой Бой Бой Бой Бой Бой
# Бой Бой Бой Бой Бой Бой Бой Бой
# Бой Бой Бой Бой Бой Бой Бой Бой
# Запуск боя с Человеком
@dp.callback_query_handler(Text(startswith='fight_with_man_call'))
async def fight_with_human(call: types.CallbackQuery, state: FSMContext):
    global PROCESS_CREATING_FIELD

    if call.from_user.id in PROCESS_CREATING_FIELD:
        init_field = PROCESS_CREATING_FIELD[call.from_user.id]
        await init_field.deleting_creation_process()
        del PROCESS_CREATING_FIELD[call.from_user.id]
    init_field = CreatingField(dp, con, "human")
    PROCESS_CREATING_FIELD[call.from_user.id] = init_field
    await init_field.working_with_field(call, state)


# Кнопка готовности к бою с человеком
@dp.callback_query_handler(text='ready_to_fight_human')
async def ready_to_fight_with_human(call: types.CallbackQuery, state: FSMContext):
    # Получение языка
    lang_code = await getting_the_language_call(call, state, con)
    text = LANGUAGE[lang_code]['field_menu_error']
    # Проверка на валидность поля
    if call.from_user.id not in PROCESS_CREATING_FIELD:
        await session_search_error(call, state)
        return
    init_field = PROCESS_CREATING_FIELD[call.from_user.id]
    placement_error = await init_field.checking_validity_field()
    if placement_error:
        # Сообщение при ошибке
        await call.answer(text[placement_error - 1], show_alert=True)
    else:
        # Создание копии поля и отправление его в функцию боя
        field = deepcopy(init_field.field)
        # Проверка на возможность боя
        # Проверка на возможность боя
        if call.from_user.id in PLAYERS_IN_GAME:
            await init_field.deleting_creation_process()
            del PROCESS_CREATING_FIELD[call.from_user.id]
            await session_search_error(call, state)
        else:
            # Получение всей информации о предстоящем бое
            # Карта игрока
            field = field
            # Создание объекта игрока для игры
            hint = await need_a_hint(call.from_user.id, con)
            player = Player(bot, dp, con, call, state, field, call.from_user.id, hint)
            await init_field.deleting_creation_process()
            del PROCESS_CREATING_FIELD[call.from_user.id]
            PLAYERS_IN_GAME[call.from_user.id] = player
            # Если есть активные игры
            if GAME_SEARCH:
                # Присоединяемся к активной игре
                await player.connecting_to_game(GAME_SEARCH[0])
                await GAME_SEARCH[0].joining_a_player_and_start_game(player)
                GAME_SEARCH.pop(0)
            else:
                # Если нету то создаем активную игру и ждем желающих сыграть
                game = Game(bot, dp, con, player, init_algorithm, 30)
                await player.connecting_to_game(game)
                GAME_SEARCH.append(game)
                markup = types.InlineKeyboardMarkup()
                markup.row(types.InlineKeyboardButton(text=text[4], callback_data="deleting_all_sessions"))
                await call.message.edit_text(text[3], reply_markup=markup)


# Получение сложности алгоритма
@dp.callback_query_handler(text='difficulty_selection_call')
async def difficulty_selection(call: types.CallbackQuery, state: FSMContext):
    # Получение языка
    lang_code = await getting_the_language_call(call, state, con)
    text = LANGUAGE[lang_code]['difficulty_selection']
    # Создание кнопок
    markup = types.InlineKeyboardMarkup()
    # 1 сложность
    markup.row(types.InlineKeyboardButton(text=text[1], callback_data=f"fight_with_algorithm_call_1"))
    # 2 сложность
    markup.row(types.InlineKeyboardButton(text=text[2], callback_data=f"fight_with_algorithm_call_2"))
    # 3 сложность
    markup.row(types.InlineKeyboardButton(text=text[3], callback_data=f"fight_with_algorithm_call_3"))
    # 4 сложность
    markup.row(types.InlineKeyboardButton(text=text[4], callback_data=f"fight_with_algorithm_call_4"))
    # 5 сложность
    markup.row(types.InlineKeyboardButton(text=text[5], callback_data=f"fight_with_algorithm_call_5"))
    # 6 сложность
    markup.row(types.InlineKeyboardButton(text=text[6], callback_data=f"fight_with_algorithm_call_6"))
    # возврат в меню
    markup.row(types.InlineKeyboardButton(text=text[7], callback_data=f"start_call"))
    await call.message.edit_text(text=text[0], reply_markup=markup)


# Запуск боя с Алгоритмом
@dp.callback_query_handler(Text(startswith='fight_with_algorithm_call'))
async def fight_with_algorithm(call: types.CallbackQuery, state: FSMContext):
    global PROCESS_CREATING_FIELD

    if call.from_user.id in PROCESS_CREATING_FIELD:
        init_field = PROCESS_CREATING_FIELD[call.from_user.id]
        await init_field.deleting_creation_process()
        del PROCESS_CREATING_FIELD[call.from_user.id]
    init_field = CreatingField(dp, con, "algorithm")
    PROCESS_CREATING_FIELD[call.from_user.id] = init_field
    await state.update_data(difficulty=call.data.split("_")[4])
    await init_field.working_with_field(call, state)


# Кнопка готовности к бою с алгоритмом
@dp.callback_query_handler(text='ready_to_fight_algorithm')
async def ready_to_fight_with_algorithm(call: types.CallbackQuery, state: FSMContext):
    # Получение языка
    lang_code = await getting_the_language_call(call, state, con)
    text = LANGUAGE[lang_code]['field_menu_error']
    # Проверка на валидность поля
    if call.from_user.id not in PROCESS_CREATING_FIELD:
        await session_search_error(call, state)
        return
    init_field = PROCESS_CREATING_FIELD[call.from_user.id]
    placement_error = await init_field.checking_validity_field()
    if placement_error:
        # Сообщение при ошибке
        await call.answer(text[placement_error - 1], show_alert=True)
    else:
        # Проверка на возможность боя
        if call.from_user.id in PLAYERS_IN_GAME:
            await init_field.deleting_creation_process()
            del PROCESS_CREATING_FIELD[call.from_user.id]
            await session_search_error(call, state)
        else:
            print('Готов к бою с алгоритмом')
            # Получение всей информации о предстоящем бое
            # Создание копии поля и отправление его в функцию боя
            field = deepcopy(init_field.field)
            # Карта алгоритма
            field_algorithm = deepcopy(await init_field.get_valid_field(8))
            # Получение сложности алгоритма
            data = await state.get_data()
            difficulty = data.get('difficulty')
            # Подсказки для игрока
            hint = await need_a_hint(call.from_user.id, con)
            player = Player(bot, dp, con, call, state, field, call.from_user.id, hint)
            PLAYERS_IN_GAME[call.from_user.id] = player
            game = GameAlgorithm(bot, dp, con, player, init_algorithm, difficulty, field_algorithm)
            await init_field.deleting_creation_process()
            del PROCESS_CREATING_FIELD[call.from_user.id]
            await player.connecting_to_game(game)
            await player.queue()
            await game.drawing_field_for_players()


# Запуск боя с другом
@dp.callback_query_handler(Text(startswith='fight_with_friend_call'))
async def fight_with_friend(call: types.CallbackQuery, state: FSMContext):
    global PROCESS_CREATING_FIELD

    if call.from_user.id in PROCESS_CREATING_FIELD:
        init_field = PROCESS_CREATING_FIELD[call.from_user.id]
        await init_field.deleting_creation_process()
        del PROCESS_CREATING_FIELD[call.from_user.id]
    init_field = CreatingField(dp, con, "friend")
    PROCESS_CREATING_FIELD[call.from_user.id] = init_field
    await init_field.working_with_field(call, state)


# Кнопка готовности к бою с другом
@dp.callback_query_handler(text='ready_to_fight_friend')
async def ready_to_fight_with_friend(call: types.CallbackQuery, state: FSMContext):
    # Получение языка
    lang_code = await getting_the_language_call(call, state, con)
    text = LANGUAGE[lang_code]['field_menu_error']
    # Проверка на валидность поля
    if call.from_user.id not in PROCESS_CREATING_FIELD:
        await session_search_error(call, state)
        return
    init_field = PROCESS_CREATING_FIELD[call.from_user.id]
    placement_error = await init_field.checking_validity_field()
    if placement_error:
        # Сообщение при ошибке
        await call.answer(text[placement_error - 1], show_alert=True)
    else:
        # Создание копии поля и отправление его в функцию боя
        field = deepcopy(init_field.field)
        # Проверка на возможность боя
        # Проверка на возможность боя
        if call.from_user.id in PLAYERS_IN_GAME:
            await init_field.deleting_creation_process()
            del PROCESS_CREATING_FIELD[call.from_user.id]
            await session_search_error(call, state)
        else:
            # Получение всей информации о предстоящем бое
            # Карта игрока
            field = field
            # Создание объекта игрока для игры
            hint = await need_a_hint(call.from_user.id, con)
            player = Player(bot, dp, con, call, state, field, call.from_user.id, hint)
            await init_field.deleting_creation_process()
            del PROCESS_CREATING_FIELD[call.from_user.id]
            PLAYERS_IN_GAME[call.from_user.id] = player
            # Если есть активные игры
            data = await state.get_data()
            friend_code = data.get('friend')
            if friend_code in FRIEND_GAME_SEARCH:
                await player.connecting_to_game(FRIEND_GAME_SEARCH[friend_code])
                await FRIEND_GAME_SEARCH[friend_code].joining_a_player_and_start_game(player)
                FRIEND_GAME_SEARCH.pop(friend_code)
                await state.update_data(friend=0)
            else:
                # Если нету то создаем активную игру и предлагаем позвать друга
                game = Game(bot, dp, con, player, init_algorithm, 60)
                await player.connecting_to_game(game)
                FRIEND_GAME_SEARCH[call.from_user.id] = game
                text_a = text[5].format(link="<code>https://t.me/OceanicBattleBot?start=battle_"
                                             f"{call.from_user.id}</code>")
                markup = types.InlineKeyboardMarkup()
                markup.row(types.InlineKeyboardButton(text=text[4], callback_data="deleting_all_sessions"))
                await call.message.edit_text(text_a, reply_markup=markup, parse_mode="HTML")


# Сообщение если у пользователя есть активные сессии боя а он хочет начать новую
async def session_search_error(call: types.CallbackQuery, state: FSMContext):
    # Получение языка
    lang_code = await getting_the_language_call(call, state, con)
    text = LANGUAGE[lang_code]['session_search_error']
    # Создание кнопок
    markup = types.InlineKeyboardMarkup()
    # кнопока удаление всех сессий
    markup.row(types.InlineKeyboardButton(text=text[1], callback_data=f"deleting_all_sessions"))
    # Возвращение в меню
    markup.row(types.InlineKeyboardButton(text=text[2], callback_data=f"start_call"))
    await call.message.edit_text(text=text[0], reply_markup=markup)


# Процесс удаления всех сессий боя
@dp.callback_query_handler(text='deleting_all_sessions')
async def deleting_all_sessions(call: types.CallbackQuery, state: FSMContext):
    # Получение его объекта класса
    await PLAYERS_IN_GAME[call.from_user.id].game.logic_of_victory_and_defeat(PLAYERS_IN_GAME[call.from_user.id])


@dp.callback_query_handler(Text(startswith='top_'))
async def top_menu(call: types.CallbackQuery, state: FSMContext):
    # Определение языка и текстов
    lang_code = await getting_the_language_call(call, state, con)
    text = LANGUAGE[lang_code]['top']
    text_osn = deepcopy(text[0])
    criteria = call.data.split("_")[1]

    # Функция для создания кнопок статистики
    def create_stat_buttons():
        buttons = [
            types.InlineKeyboardButton(text=text[i], callback_data=f"top_{text[i].lower()}")
            for i in range(4, 8)
        ]
        return buttons

    # Создание кнопок с возможностями статистики
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton(text=text[4], callback_data=f"top_balance"),
        types.InlineKeyboardButton(text=text[5], callback_data=f"top_human"),
        types.InlineKeyboardButton(text=text[6], callback_data=f"top_alg"),
    )
    markup.row(
        types.InlineKeyboardButton(text=text[7], callback_data=f"start_call"),
    )

    if criteria == "balance":
        text_osn = text_osn.format(criterion=text[8])
    elif criteria == "human":
        text_osn = text_osn.format(criterion=text[9])
        text_osn += text[11]
    else:
        text_osn = text_osn.format(criterion=text[10])
        text_osn += text[11]

    # Получение данных о пользователях
    top_10, player_place = await sorting_by_criterion(call.from_user.id, criteria, con)
    user_ids = [name_u for rank_u, (name_u, _, _, _) in enumerate(top_10, start=1)]
    user_data = await get_user_data(user_ids)

    # Формирование текста статистики
    for rank_u, (name_u, wins_u, losses_u, score_u) in enumerate(top_10, start=1):
        user_info = user_data.get(name_u, {})
        user_first_name = user_info.get('first_name', "")

        if criteria == "balance":
            text_u = text[1].format(rank=rank_u, name=f'<a href="tg://user?id={name_u}">{user_first_name}</a>',
                                    wins=wins_u)
        else:
            score_u = "{:.2f}".format(score_u)
            text_u = text[2].format(rank=rank_u, name=f'<a href="tg://user?id={name_u}">{user_first_name}</a>',
                                    wins=wins_u, losses=losses_u, score=score_u)
        text_osn += text_u

    # Добавление информации о текущем пользователе
    text_osn += text[3].format(player_place=player_place,
                               player_name=f'<a href="tg://user?id={call.from_user.id}">{call.from_user.first_name}</a>')

    await call.message.edit_text(text=text_osn, reply_markup=markup, parse_mode='HTML')

async def get_user_data(user_ids):
    user_data = {}
    for user_id in user_ids:
        user = await bot.get_chat(user_id)
        if user:
            user_data[user_id] = {'first_name': user.first_name, 'last_name': user.last_name}
    return user_data


async def on_startup(db):
    print("Bot started")

    global con, init_field, init_algorithm
    con = sqlite3.connect('.\db\sea_battle.db')

    if con:
        print("Database successfully connected")
    else:
        print("Database not connected")
        exit(0)

    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user (
            user_id  STRING  PRIMARY KEY,
            language STRING,
            hint     BOOLEAN,
            balance  INTEGER DEFAULT (1000) 
        );
    """)
    con.commit()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS detailed_statistics (
            user_id                 STRING  NOT NULL PRIMARY KEY,
            games_against_people    INTEGER DEFAULT (0),
            wins_over_the_people    INTEGER DEFAULT (0),
            games_against_algorithm INTEGER DEFAULT (0),
            wins_over_the_algorithm INTEGER DEFAULT (0) 
        );
    """)
    con.commit()

    init_algorithm = Algorithm()


async def on_shutdown(dp):
    print("Bot stoped")


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
