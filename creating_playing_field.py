import random
from copy import deepcopy

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram import types

from language.language import LANGUAGE
from language.language_definition import getting_the_language_call


class CreatingField:
    CELL_TYPE = ["🟦", "⛵", "🚤", "⛴", "🚢"]
    SHIP_SIZES = {"6x6": [4, 3, 2, 1], "8x8": [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]}
    NUMBER_SHIP_CELLS = {"6x6": {4: 4, 3: 3, 2: 2, 1: 1}, "8x8": {4: 4, 3: 6, 2: 6, 1: 4}}

    def __init__(self, dp, con, type_of_battle):
        self.dp = dp
        self.con = con
        self.field = []
        self.size = 8
        self.type_of_battle = type_of_battle
        self.dp.register_callback_query_handler(self.reaction_clicking_field, Text(startswith='field_call'))
        self.dp.register_callback_query_handler(self.auto_working_with_field, Text(startswith='auto_field_call'))
        self.dp.register_callback_query_handler(self.cleaning, Text(startswith='cleaning'))

    async def working_with_field(self, call: types.CallbackQuery, state: FSMContext):
        self.field = [[0 for _ in range(self.size + 1)] for _ in range(self.size + 1)]
        await self.field_rendering(call, state)

    async def field_rendering(self, call: types.CallbackQuery, state: FSMContext):
        lang_code = await getting_the_language_call(call, state, self.con)
        text = LANGUAGE[lang_code]['field_menu']
        text_messages = text[0]

        markup = types.InlineKeyboardMarkup()
        for i in range(self.size):
            auxiliary_row = [
                types.InlineKeyboardButton(text=self.CELL_TYPE[self.field[i][j]],
                                           callback_data=f"field_call_{i}_{j}") for j in range(self.size)]
            markup.row(*auxiliary_row)
        markup.row(types.InlineKeyboardButton(text=text[1], callback_data=f"auto_field_call"))
        markup.row(types.InlineKeyboardButton(text=text[2], callback_data=f"cleaning"))
        if self.type_of_battle == "algorithm":
            markup.row(types.InlineKeyboardButton(text=text[3], callback_data=f"ready_to_fight_algorithm"))
            markup.row(types.InlineKeyboardButton(text=text[4], callback_data=f"difficulty_selection_call"))
        elif self.type_of_battle == "friend":
            markup.row(types.InlineKeyboardButton(text=text[3], callback_data=f"ready_to_fight_friend"))
            markup.row(types.InlineKeyboardButton(text=text[5], callback_data=f"start_call"))
        else:
            markup.row(types.InlineKeyboardButton(text=text[3], callback_data=f"ready_to_fight_human"))
            markup.row(types.InlineKeyboardButton(text=text[5], callback_data=f"start_call"))
        await call.message.edit_text(text_messages, reply_markup=markup)

    async def reaction_clicking_field(self, call: types.CallbackQuery, state: FSMContext):
        x_y = call.data.split("_")
        x, y = int(x_y[2]), int(x_y[3])
        possibility_change = await self.cell_analysis(x, y)
        if possibility_change:
            pass
        else:
            await self.field_changes(x, y)
            await self.field_rendering(call, state)

    async def cell_analysis(self, x: int, y: int):
        cell = self.field[x][y]
        try:
            # проверка на то что на ней нет крестика
            if cell == 5:
                return True

            # проверка на то что по диагонали ничего нет
            for i in range(-1, 2, 2):
                for j in range(-1, 2, 2):
                    if self.field[x + i][y + j] in [1, 2, 3, 4]:
                        return True

            # проверка на то что это не продолжение четерехпалубного корабля
            sum_of_neighbors, number_neighbors = await self.all_about_the_neighbors(x, y)
            if cell == 0 and sum_of_neighbors > 3:
                return True

            return False
        except IndexError:
            pass

    async def all_about_the_neighbors(self, x: int, y: int):
        sum_of_neighbors = 0
        number_neighbors = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                try:
                    if i == j == 0:
                        continue
                    else:
                        val = self.field[x + i][y + j]
                        if val:
                            sum_of_neighbors += val
                            number_neighbors += 1
                except IndexError:
                    pass
        return sum_of_neighbors, number_neighbors

    async def field_changes(self, x: int, y: int):
        sum_of_neighbors, number_neighbors = await self.all_about_the_neighbors(x, y)
        if self.field[x][y] in [1, 2, 3, 4]:
            if number_neighbors == 1:
                await self.adding_adjustment_ship(x, y, [2, 3, 4], 1, 1)
                await self.adding_adjustment_ship(x, y, [2, 3, 4], -1, 1)
            else:
                try:
                    if sum_of_neighbors == 6:
                        for i in range(-1, 2):
                            for j in range(-1, 2):
                                if self.field[x + i][y + j] == 3:
                                    self.field[x + i][y + j] = 1
                                    self.field[x - i][y - j] = 1
                                    break

                    elif sum_of_neighbors == 8:
                        for i in range(-1, 2):
                            for j in range(-1, 2):
                                if self.field[x + i][y + j] == 4:
                                    sum_of_neighbors_for_neighbor, number_neighbors_for_neighbor \
                                        = await self.all_about_the_neighbors(x + i, y + j)
                                    if number_neighbors_for_neighbor == 1:
                                        self.field[x + i][y + j] = 1
                                        self.field[x - i][y - j] = 2
                                        self.field[x - (i * 2)][y - (j * 2)] = 2
                                    else:
                                        self.field[x - i][y - j] = 1
                                        self.field[x + i][y + j] = 2
                                        self.field[x + (i * 2)][y + (j * 2)] = 2
                                    break
                except IndexError:
                    pass
            self.field[x][y] = 0

        elif self.field[x][y] == 0:
            if number_neighbors != 2:
                if await self.adding_adjustment_ship(x, y, [1, 2, 3], 1):
                    return
                elif await self.adding_adjustment_ship(x, y, [1, 2, 3], -1):
                    return
                else:
                    self.field[x][y] = 1

            else:
                try:
                    if sum_of_neighbors == 2:
                        for i in range(-1, 2):
                            for j in range(-1, 2):
                                if self.field[x + i][y + j] == 1:
                                    self.field[x + i][y + j] = 3
                                    self.field[x - i][y - j] = 3
                                    self.field[x][y] = 3
                                    break

                    elif sum_of_neighbors == 3:
                        for i in range(-1, 2):
                            for j in range(-1, 2):
                                if self.field[x + i][y + j] == 1:
                                    self.field[x][y] = 4
                                    self.field[x + i][y + j] = 4
                                    self.field[x - i][y - j] = 4
                                    self.field[x - (i * 2)][y - (j * 2)] = 4
                                    break
                                elif self.field[x + i][y + j] == 2:
                                    self.field[x][y] = 4
                                    self.field[x - i][y - j] = 4
                                    self.field[x + i][y + j] = 4
                                    self.field[x + (i * 2)][y + (j * 2)] = 4
                                    break
                except IndexError:
                    pass

    async def adding_adjustment_ship(self, x, y, list_features, direction, deletion_rate=0):
        try:
            if self.field[x + direction][y] in list_features:
                idx = list_features.index(self.field[x + direction][y]) + 2
                for i in range(deletion_rate, idx):
                    self.field[x + (i * direction)][y] = idx - deletion_rate
                return True
        except IndexError:
            pass

        try:
            if self.field[x][y + direction] in list_features:
                idx = list_features.index(self.field[x][y + direction]) + 2
                for i in range(deletion_rate, idx):
                    self.field[x][y + (i * direction)] = idx - deletion_rate
                return True
        except IndexError:
            pass

        return False

    async def auto_working_with_field(self, call: types.CallbackQuery, state: FSMContext):
        field = await self.get_valid_field(self.size)
        self.field = deepcopy(field)
        await self.field_rendering(call, state)

    async def get_valid_field(self, size):
        while True:
            try:
                field = await self.generate_field(size)
            except IndexError:
                pass
            else:
                return field

    async def generate_field(self, size):
        """
        Генерирует поле заданного размера со случайно размещенными кораблями заданных размеров.
        """
        field = [[0 for _ in range(size + 1)] for _ in range(size + 1)]
        for ship_size in self.SHIP_SIZES[f"{size}x{size}"]:
            await self.place_ship(ship_size, field, size)
        return field

    async def place_ship(self, ship_len, field, size):
        """
        Размещает корабль заданной длины на поле.
        """
        count = 0
        while True:
            count += 1
            direction = random.choice(['horizontal', 'vertical'])
            if direction == 'horizontal':
                row = random.randint(0, size - 1)
                col = random.randint(0, size - ship_len)
                if await self.is_valid_location(row, col, ship_len, direction, field, size):
                    for i in range(col, col + ship_len):
                        field[row][i] = ship_len
                    break
            else:
                row = random.randint(0, size - ship_len)
                col = random.randint(0, size - 1)
                if await self.is_valid_location(row, col, ship_len, direction, field, size):
                    for i in range(row, row + ship_len):
                        field[i][col] = ship_len
                    break
            if count > 30:
                raise IndexError

    async def is_valid_location(self, row, col, length, direction, field, size):
        """
        Проверяет, можно ли разместить корабль заданной длины в заданном месте на поле.
        """
        if direction == 'horizontal':
            if col + length > size:
                return False
            for i in range(col - 1, col + length + 1):
                if i < 0 or i >= size:
                    continue
                if row - 1 >= 0 and field[row - 1][i] != 0:
                    return False
                if row + 1 < size and field[row + 1][i] != 0:
                    return False
            for i in range(col - 1, col + length + 1):
                if i < 0 or i >= size:
                    continue
                if field[row][i] != 0:
                    return False
        else:
            if row + length > size:
                return False
            for i in range(row - 1, row + length + 1):
                if i < 0 or i >= size:
                    continue
                if col - 1 >= 0 and field[i][col - 1] != 0:
                    return False
                if col + 1 < size and field[i][col + 1] != 0:
                    return False
            for i in range(row - 1, row + length + 1):
                if i < 0 or i >= size:
                    continue
                if field[i][col] != 0:
                    return False
        return True

    async def cleaning(self, call: types.CallbackQuery, state: FSMContext):
        self.field = [[0 for _ in range(self.size + 1)] for _ in range(self.size + 1)]
        await self.field_rendering(call, state)

    async def checking_validity_field(self):
        size = self.size
        ship = deepcopy(self.NUMBER_SHIP_CELLS[f"{size}x{size}"])
        for x, row in enumerate(self.field):
            for y, cell in enumerate(row):
                if cell != 0:
                    neighbors = set()
                    for i in range(-1, 2):
                        for j in range(-1, 2):
                            if 0 <= (x + i) < size and 0 <= (y + j) < size and self.field[x + i][y + j] != 0:
                                neighbors.add(self.field[x + i][y + j])
                    if any(cell != i and i in neighbors for i in range(1, 5)):
                        return 1
                    ship[cell] -= 1

        if any(ship[i] < 0 for i in range(1, 5)):
            return 2
        elif any(ship[i] > 0 for i in range(1, 5)):
            return 3
        return False

    async def deleting_creation_process(self):
        self.dp.callback_query_handlers.unregister(self.reaction_clicking_field)
        self.dp.callback_query_handlers.unregister(self.auto_working_with_field)
        self.dp.callback_query_handlers.unregister(self.cleaning)
        del self
