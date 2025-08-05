from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


start_without_all_fields = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Дозаполнить анкету')],
                                     ], resize_keyboard=True, input_field_placeholder="Заполните анкету до конца")

start_reg = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Заполнить анкету')],
                                     ], resize_keyboard=True, input_field_placeholder="Заполните анкету для использования бота")

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Смотреть анкеты 🚀')],
                                     ], resize_keyboard=True)

get_number = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Отправить телефон', request_contact=True)],
                                     ], resize_keyboard=True)

wife_status = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Нет отношений")],
            [KeyboardButton(text="Влюблен")],
            [KeyboardButton(text="В отношениях")],
        ],
        resize_keyboard=True,
    )


goal = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Совместный бот")],
            [KeyboardButton(text="Общение")],
            [KeyboardButton(text="Поиск команды")],
            [KeyboardButton(text="Отношения")],
        ],
        resize_keyboard=True,
    )

who_interested = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Женщины")],
            [KeyboardButton(text="Мужчины")],
            [KeyboardButton(text="Все")],
        ],
        resize_keyboard=True,
    )

my_profile_main = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Редактировать профиль", callback_data="update_profile")],
        [InlineKeyboardButton(text="Редактировать олимпиады", callback_data="update_olymps")],
                     ])