from config import LINK_TO_THE_CHAT

LANGUAGE = {
    "ru": {
        "menu": [
            "🏠 Меню"
            "\n⚓️ Готов начать бой? ⚓️"
            "\nПо всем вопросам и возникшим багам"
            f"\n<a href='{LINK_TO_THE_CHAT}'>Чатик о боте</a>",
            "📚 Правила игры",
            "⚙️ Настройки",
            "👤 Профиль",
            "🤖 Играть против бота",
            "🤝 Играть против друга",
            "🎮 Играть",
            "Вам было начислено 1000🪙",
            "🏆Топы игроков",
        ],
        "rules_menu": [
            "🏠 Меню // 📚 Правила"
            "\n⬇️ Правила этой игры ⬇️",
            "📗 Подготовка к игре",
            "📕 Ход игры",
            "📘 Обозначения",
            "🏠 Назад в меню"
        ],
        'rules': [
            "🏠 Меню // 📚 Правила // 📗 Подготовка к игре"
            "\n\n1) У каждого игрока одинаковое количество кораблей:"
            "\n   - 1 четырехпалубный"
            "\n   - 2 трехпалубных"
            "\n   - 3 двухпалубных"
            "\n   - 4 однопалубных"
            "\n2) Корабли не должны пересекаться или касаться друг друга."
            "\n3) Корабли не могут быть размещены по диагонали."
            "\n4) Если вы забросите уже начатую игру, вам будет засчитано поражение."
            "\n5) Если вы выйдете из процесса расстановки кораблей или забросите игру на этом"
            " этапе, поражение не будет засчитано."
            "\n6) В игре с другом вы не теряете рейтинг и не получаете монеты, так же как и в игре с ботом.",

            "🏠 Меню // 📚 Правила // 📕 Ход игры"
            "\n\n1) Игроки по очереди делают ходы, выбирая клетку, куда хотят выстрелить."
            "\n2) Если вы попали в клетку, где находится корабль, то корабль считается раненным."
            "\n3) Если вы попали в клетку, где находится корабль, то вы ходите еще раз."
            "\n4) Если все палубы корабля поражены, то корабль потоплен."
            "\n5) Игрок, потопивший все корабли противника, побеждает."
            "\n6) Вы не можете атаковать одну и ту же клетку дважды."
            "\n7) Игра считается заброшенной, если ход игрока длится больше минуты."
            "\n8) Если игра заброшена вами, то вам засчитывается поражение.",

            "🏠 Меню // 📚 Правила // 📘 Обозначения"
            "\n\nОбозначение кораблей:"
            "\n🚢 - четырехпалубный"
            "\n⛴ - трехпалубный"
            "\n🚤 - двухпалубный"
            "\n⛵️ - однопалубный"
            "\n\nОбозначение элементов поля:"
            "\n❗️ - Раненый корабль"
            "\n🌊 - Клетка моря"
            "\n❌ - Потопленный корабль"
            "\n✖️ - Промах",
            "📚 Назад в правила"],
        "settings": [
            "🏠 Меню // ⚙️ Настройки",
            "{name} Русский",
            "{name} English",
            "{name} Подсказки в бою",
            "🏠 Назад в меню"
        ],
        "profile": [
            "🏠 Меню // 👤 Профиль"
            "\n\n📌 Профиль пользователя:"
            "\n👤 Имя, отображаемое оппоненту: {name}"
            "\n🆔 ID пользователя: {id}"
            "\n💵 Баланс пользователя: {balance}🪙"
            "\n-------------------"
            "\n📊 Статистика пользователя:"
            "\n🏆 Побед: {wins} (📈 Доля побед: {share_of_wins}%)"
            "\n☹️ Поражений: {defeats}",
            "📖 Подробная статистика",
            "🏠 Назад в меню",
            "💳 Пополнение баланса"
        ],
        "statistics": [
            "🏠 Меню // 👤 Профиль // 📖 Подробная статистика"
            "\n\n📌 Профиль пользователя:"
            "\n👤 Имя, отображаемое оппоненту: {name}"
            "\n🆔 ID пользователя: {id}"
            "\n-------------------"
            "\n📊 Статистика пользователя в боях против людей:"
            "\n🏆 Побед: {victories_against_people}"
            "\n☹ Поражений: {defeats_against_people}"
            "\n🔢 Количество сыгранных игр: {playing_with_person}"
            "\n📊 Доля побед: {share_of_wins_against_people}%"
            "\n-------------------"
            "\n📊 Статистика пользователя в боях против бота:"
            "\n🏆 Побед: {victories_against_algorithm}"
            "\n☹ Поражений: {defeats_against_algorithm}"
            "\n🔢 Количество сыгранных игр: {playing_with_bot}"
            "\n📊 Доля побед: {share_of_wins_against_algorithm}%"
            "\n-------------------"
            "\n📊 Общая статистика пользователя:"
            "\n🏆 Побед: {wins}"
            "\n☹ Поражений: {defeats}"
            "\n🔢 Количество сыгранных игр: {total_games_played}"
            "\n📊 Доля побед: {share_of_wins}%",
            "👤 Назад в профиль"
        ],
        "difficulty_selection": [
            "🏠 Меню // 🦾 Выбор сложности",
            "🐟 Легкая",
            "🐬 Средняя",
            "🦈 Тяжелая",
            "🐍 Легкая(Крупный калибр)",
            "🐊 Средняя(Крупный калибр)",
            "🐉 Тяжелая(Крупный калибр)",
            "🏠 Назад в меню"
        ],
        "field_menu": [
            "🏠 Меню // ⛴ Поле размещения судов"
            "\nРазмещать корабли можно:"
            "\n✅ Вручную"
            "\n✅ Автоматически"
            "\n-------------------"
            "\n🚢 - Четырехпалубный (1 шт)"
            "\n⛴ - Трехпалубный (2 шт)"
            "\n🚤 - Двухпалубный (3 шт)"
            "\n⛵ - Однопалубный (4 шт)",
            "🤖 Авторазмещение судов",
            "🧹 Очистка поля",
            "⚔️ Готов к бою",
            "🦾 Выбрать сложность",
            "🏠 Назад в меню"
        ],
        "session_search_error": [
            "🏠 Меню // ⚠️ Ошибка сессии"
            "\n⚠️ У вас уже есть активная игра."
            "\n💡 Пожалуйста, завершите текущую игру, чтобы начать новую."
            "\n💬 Обратите внимание, что если вы принудительно завершите игровую сессию,"
            " это будет засчитано как поражение.",
            "🗑 Удалить все активные игры",
            "🏠 Назад в меню"
        ],
        "deleting_all_sessions": [
            "🏠 Меню // 🗑 Удаление сессий"
            "\n👍 Все игровые сессии были успешно удалены."
            "\nВам засчитано одно поражение, так как у вас была 1 активная игра."
            "\n⚔️ Теперь вы можете начать новую игру в любое время.",
            "🏠 Меню // 🗑 Удаление сессий"
            "\n👍 Все игровые сессии были успешно удалены."
            "\nВам не засчитывается поражение, так как для удаленной игры еще не был найден противник."
            "\n⚔️ Теперь вы можете начать новую игру в любое время.",
            "🏠 Назад в меню",
            "🏠 Меню // 🗑 Удаление сессий"
            "\n🏆 Ваш противник сдался. Поздравляем с победой!"
            "\n⚔️ Теперь вы можете начать новую игру в любое время."
        ],
        "field_menu_error": [
            "❗️ Корабли касаются друг друга",
            "❗️ Слишком много кораблей",
            "❗️ Слишком мало кораблей",
            "Ожидайте начала боя."
            "\nЕсли игрок-противник не будет найден, поиск автоматически завершится через 45 секунд.",
            "Завершить ожидание оппонента",
            "🤝 Ожидайте присоединение друга 🤝"
            "\nДля того чтобы ваш друг мог присоединиться к вам в игре, выполните следующие шаги:"
            "\n1) Отправьте другу следующую уникальную ссылку:"
            "\n{link}"
            ""
            "\n👥 Действия вашего друга:"
            "\n1) Перейдите по предоставленной ссылке."
            "\n2) Перейдите в раздел 'Бой с другом'."
            "\n"
            "\nПосле того, как ваш друг успешно выполнит эти действия, он присоединится к вам в игре"
            "\nЕсли друг не присоединится через 45 секунд, игра завершиться"],
        "fight_menu": [
            "🏠 Меню // ⛴ Поле боя"
            "\nПорядок хода:"
            "\n{name1}: {move1}"
            "\n{name2}: {move2}"
            "\n-------------------"
            "\nПоследний ход:"
            "\n{move3}"
            "\n-------------------"
            "\nВаше поле:"
            "\nПопадания врага будут отображаться на нем"
            "\n",
            "🚀 Меню крупнокалиберных орудий",
            "👎 Сдаться",
            "🕒 В настоящее время противник делает свой ход.",
            "Похоже, произошла непредвиденная ошибка. Пожалуйста, перезапустите бой."
        ],
        "victory_menu": [
            "\n🎉 Поздравляем, вы победили!"
            "\nВам будет засчитана одна победа."
            "\nПерейдите в рейтинг, возможно, он вас приятно удивит."
            "\nИстория вашего боя:",
            "😔 К сожалению, вы проиграли."
            "Вам будет засчитано одно поражение."
            "\nИстория вашего боя:",
            "🏠 Назад в меню"],
        "super_weapon_menu": [
            "\n⚡️ Меню ДЕЙСТВИТЕЛЬНО крупного оружия"
            "\nКаждое из этих оружий, используемое с умом, способно обеспечить вам победу,"
            " даже в самых сложных ситуациях."
            "\nОднако, помни, солдат, что любое использование таких мощностей обойдется тебе в копеечку."
            "\n💰 Текущий баланс: {balance} 🪙",
            "📡 Радар - 50 🪙",
            "💣 Бомбочка - 125 🪙",
            "🛩 Бомбардировщик - 125 🪙",
            "🚀 Атомная бомба - 275 🪙",
            "🏠 Назад в бой"
        ],
        "super_weapon": [
            "У тебя недостаточно монет для использования этого оружия.",
            "Сейчас не твой ход, подожди немного.",
            "Необходимо отдать команду о ведении огня."
        ],
        "replenishment_balance": [
            "🏠 Меню // 👤 Профиль // 💳 Пополнение баланса"
            "\n"
            "\nПригласи друга по этой ссылке"
            "\n{link}"
            "\nИ вы оба получите по 1000🪙 на баланс профиля",
            "👤 Назад в профиль"],
        "top": ["⭐️Топ-10 игроков {criterion}",
                "\n{rank}.  {name}      {wins}",
                "\n{rank}.  {name}      {wins} | {losses} | {score}",
                "\n\nВаше место в рейтинге"
                "\n{player_place}. {player_name}",
                "денюшка🪙",
                "человек⚡",
                "алгоритм🤖",
                "🏠 Назад в меню",
                "по денюшке🪙",
                "в боях с людьми⚡️",
                "в боях с алгоритмом🤖",
                "\nПобеды🏆|Поражения😓|Рейтинг📊\n",
                ],
        "message_error": ["Извините, но бот не понимает текстовых сообщений."
                          " Пожалуйста, используйте кнопки,"
                          " или если у вас есть вопросы, не стесняйтесь писать здесь."]
    },

    "en": {
        "menu": [
            "🏠 Menu"
            "\n⚓️ Ready to start a battle? ⚓️"
            "\nFor any questions and any bugs that arise "
            f"\n<a href='{LINK_TO_THE_CHAT}'>Bot Chat</a>",
            "📚 Game Rules",
            "⚙️ Settings",
            "👤 Profile",
            "🤖 Play against the bot",
            "🤝 Play against a friend",
            "🎮 Play",
            "You have been credited with 1000🪙.",
            "🏆Top Players"],
        "rules_menu": [
            "🏠 Menu // 📚 Rules"
            "\n⬇️ Rules of this game ⬇️",
            "📗 Game Preparation",
            "📕 Game Moves",
            "📘 Symbols",
            "🏠 Back to Menu"
        ],
        'rules': [
            "🏠 Menu // 📚 Rules // 📗 Game Preparation"
            "\n\n1) Each player has an equal number of ships:"
            "\n   - 1 four-deck ship"
            "\n   - 2 three-deck ships"
            "\n   - 3 two-deck ships"
            "\n   - 4 one-deck ships"
            "\n2) Ships must not overlap or touch each other."
            "\n3) Ships cannot be placed diagonally."
            "\n4) If you abandon a game that has already started, it will count as a loss for you."
            "\n5) If you exit the ship placement process or abandon the game at this stage,"
            " it will not count as a loss."
            "\n6) In a game with a friend, you do not lose rating or earn coins, just like in a game against a bot.",

            "🏠 Menu // 📚 Rules // 📕 Game Moves"
            "\n"
            "\n1) Players take turns making moves, choosing a cell to shoot at."
            "\n2) If you hit a cell where a ship is located, the ship is considered damaged."
            "\n3) If you hit a cell where a ship is located, you get an additional turn."
            "\n4) If all decks of a ship are damaged, the ship is sunk."
            "\n5) The player who sinks all of the opponent's ships wins."
            "\n6) You cannot attack the same cell twice."
            "\n7) The game is considered abandoned if a player's turn lasts more than a minute."
            "\n8) If you abandon the game, it will be counted as a loss for you.",

            "🏠 Menu // 📚 Rules // 📘 Symbols"
            "\n"
            "\nShip Symbols:"
            "\n🚢 - Four-deck ship"
            "\n⛴ - Three-deck ship"
            "\n🚤 - Two-deck ship"
            "\n⛵️ - One-deck ship"
            "\n"
            "\nField Symbols:"
            "\n❗️ - Damaged ship"
            "\n🌊 - Sea cell"
            "\n❌ - Sunk ship"
            "\n✖️ - Miss",
            "📚 Back to Rules"

        ],
        "settings": [
            "🏠 Menu // ⚙️ Settings",
            "{name} Russian",
            "{name} English",
            "{name} Battle Hints",
            "🏠 Back to Menu"
        ],
        "profile": [
            "🏠 Menu // 👤 Profile"
            "\n"
            "\n📌 User Profile:"
            "\n👤 Display Name: {name}"
            "\n🆔 User ID: {id}"
            "\n💵 User Balance: {balance}🪙"
            "\n-------------------"
            "\n📊 User Statistics:"
            "\n🏆 Wins: {wins} (📈 Win Percentage: {share_of_wins}%)"
            "\n☹️ Defeats: {defeats}",
            "📖 Detailed Statistics",
            "🏠 Back to Menu",
            "💳 Balance replenishment"
        ],
        "statistics": [
            "🏠 Menu // 👤 Profile // 📖 Detailed Statistics"
            "\n"
            "\n📌 User Profile:"
            "\n👤 Display Name: {name}"
            "\n🆔 User ID: {id}"
            "\n-------------------"
            "\n📊 User Statistics in Battles Against People:"
            "\n🏆 Wins: {victories_against_people}"
            "\n☹ Defeats: {defeats_against_people}"
            "\n🔢 Number of Games Played: {playing_with_person}"
            "\n📊 Win Percentage: {share_of_wins_against_people}%"
            "\n-------------------"
            "\n📊 User Statistics in Battles Against the Algorithm:"
            "\n🏆 Wins: {victories_against_algorithm}"
            "\n☹ Defeats: {defeats_against_algorithm}"
            "\n🔢 Number of Games Played: {playing_with_bot}"
            "\n📊 Win Percentage: {share_of_wins_against_algorithm}%"
            "\n-------------------"
            "\n📊 Overall User Statistics:"
            "\n🏆 Wins: {wins}"
            "\n☹ Defeats: {defeats}"
            "\n🔢 Number of Games Played: {total_games_played}"
            "\n📊 Win Percentage: {share_of_wins}%",
            "👤 Back to Profile"],
        "difficulty_selection": [
            "🏠 Menu // 🦾 Difficulty Selection",
            "🐟 Easy",
            "🐬 Medium",
            "🦈 Hard",
            "🐍 Easy (Heavy Caliber)",
            "🐊 Medium (Heavy Caliber)",
            "🐉 Hard (Heavy Caliber)",
            "🏠 Back to Menu"
        ],
        "field_menu": [
            "🏠 Menu // ⛴ Ship Placement Field"
            "\nYou can place ships:"
            "\n✅ Manually"
            "\n✅ Automatically"
            "\n-------------------"
            "\n🚢 - Four-deck (1 piece)"
            "\n⛴ - Three-deck (2 pieces)"
            "\n🚤 - Two-deck (3 pieces)"
            "\n⛵ - One-deck (4 pieces)",
            "🤖 Auto Ship Placement",
            "🧹 Clear the Field",
            "⚔️ Ready for Battle",
            "🦾 Choose Difficulty",
            "🏠 Back to Menu"
        ],
        "session_search_error": [
            "🏠 Menu // ⚠️ Session Error"
            "⚠️ You already have an active game."
            "💡 Please finish your current game to start a new one."
            "💬 Please note that forcibly ending a game session will be counted as a defeat.",
            "🗑 Delete all active games",
            "🏠 Back to Menu"],
        "deleting_all_sessions": [
            "🏠 Menu // 🗑 Deleting Sessions"
            "\n👍 All game sessions have been successfully deleted."
            "\nYou have been counted with one defeat, as you had 1 active game."
            "\n⚔️ Now you can start a new game at any time.",
            "🏠 Menu // 🗑 Deleting Sessions"
            "\n👍 All game sessions have been successfully deleted."
            "\nYou are not counted with a defeat, as no opponent was found for the removed game."
            "\n⚔️ Now you can start a new game at any time.",
            "🏠 Back to Menu",
            "🏠 Menu // 🗑 Deleting Sessions"
            "\n🏆 Your opponent has surrendered. Congratulations on your victory!"
            "\n⚔️ Now you can start a new game at any time."],
        "field_menu_error": [
            "❗️ Ships are touching each other",
            "❗️ Too many ships",
            "❗️ Too few ships",
            "Wait for the battle to begin.",
            "End waiting for the opponent",
            "🤝 Wait for a friend to join 🤝"
            "\nTo allow your friend to join your game, follow these steps:"
            "\n1) Send your friend the following unique link:"
            "\n{link}"
            ""
            "\n👥 Your friend's actions:"
            "\n1) Follow the provided link."
            "\n2) Go to the 'Battle with a Friend' section."
            "\n"
            "\nOnce your friend successfully completes these steps, they will join your game."],
        "fight_menu": [
            "🏠 Menu // ⛴ Battlefield"
            "\nTurn Order:"
            "\n{name1}: {move1}"
            "\n{name2}: {move2}"
            "\n-------------------"
            "\nLast Move:"
            "\n{move3}"
            "\n-------------------"
            "\nYour Field:"
            "\nEnemy hits will be displayed here"
            "\n",
            "🚀 Heavy Artillery Menu",
            "👎 Surrender",
            "🕒 Currently, the opponent is making their move.",
            "An unexpected error occurred. Please restart the battle."
        ],
        "victory_menu": [
            "\n🎉 Congratulations, you won!"
            "\nYou will be credited with one victory."
            "\nCheck the rankings; you might be pleasantly surprised."
            "\nYour Battle History:",

            "\n😔 Unfortunately, you lost."
            "\nYou will be credited with one defeat."
            "\nYour Battle History:",

            "🏠 Back to Menu"],
        "super_weapon_menu": [
            "⚡️ Truly Powerful Weapons Menu"
            "\nEach of these weapons, when used wisely, can secure victory for you even in the toughest situations."
            "\nHowever, remember, soldier, that any use of such firepower will cost you a pretty penny."
            "\n💰 Current Balance: {balance} 🪙",
            "📡 Radar - 50 🪙",
            "💣 Bomb - 125 🪙",
            "🛩 Bomber - 125 🪙",
            "🚀 Atomic Bomb - 275 🪙",
            "🏠 Back to Battle"
        ],
        "super_weapon": [
            "You don't have enough coins to use this weapon.",
            "It's not your turn right now; please wait a bit.",
            "You need to issue a fire command."

        ],
        "replenishment_balance": [
            "🏠 Menu // 👤 Profile // 💳 Balance Replenishment"
            "\n"
            "\nInvite a friend using this link"
            "\n{link}"
            "\nAnd both of you will receive 1000🪙 in your profile balance",
            "👤 Back to profile"],
        "top": ["⭐️Top 10 players {criterion}",
                "\n{rank}. {name} {wins}",
                "\n{rank}. {name} {wins} | {losses} | {score}",
                "\n\nYour place in the ranking"
                "\n{player_place}. {player_name}",
                "coins🪙",
                "human⚡",
                "algorithm🤖",
                "🏠 Back to menu",
                "by coins🪙",
                "in battles against humans⚡️",
                "in battles against the algorithm🤖",
                "\nWins🏆|Losses😓|Rating📊\n",
                ],
        "message_error": ["Sorry, but the bot doesn't understand text messages."
                          " Please use the buttons, or if you have questions, feel free to type here."]

    }

}
