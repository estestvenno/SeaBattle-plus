from aiogram import types
from aiogram.dispatcher import FSMContext

from func import get_user_language, post_user_language


# Получение языка при отправке сообщения
async def getting_the_language_message(message: types.Message, state: FSMContext, con):
    data = await state.get_data()
    lang_code = data.get('lang')
    if lang_code is None:
        # Если значение языка не сохранено в словаре, получаем его из базы данных
        lang_code = await get_user_language(message.from_user.id, con)
        if not lang_code:
            lang_code = 'ru'
            await post_user_language(message.from_user.id, lang_code, con)
        await state.update_data(lang=lang_code)
    return lang_code


# Получение языка при нажатии кнопки
async def getting_the_language_call(call: types.CallbackQuery, state: FSMContext, con):
    data = await state.get_data()
    lang_code = data.get('lang')
    if lang_code is None:
        # Если значение языка не сохранено в словаре, получаем его из базы данных
        lang_code = await get_user_language(call.from_user.id, con)
        if not lang_code:
            lang_code = 'en'
            await post_user_language(call.from_user.id, lang_code, con)
        await state.update_data(lang=lang_code)
    return lang_code
