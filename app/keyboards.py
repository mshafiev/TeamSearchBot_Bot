from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


start_without_all_fields = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Дозаполнить анкету')],
                                     ], resize_keyboard=True, input_field_placeholder="Заполните анкету до конца")

start_reg = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Заполнить анкету')],
                                     ], resize_keyboard=True, input_field_placeholder="Заполните анкету для использования бота")

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Смотреть анкеты 🚀'), KeyboardButton(text='2 👤'), KeyboardButton(text='3 ✏️')],
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

my_profile_edit_profile = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Имя", callback_data="update_profile_update_first_name")],
        [InlineKeyboardButton(text="Фамилия", callback_data="update_profile_update_last_name")],
        [InlineKeyboardButton(text="Отчество", callback_data="update_profile_update_middle_name")],
        [InlineKeyboardButton(text="Телефон", callback_data="update_profile_update_phone")],
        [InlineKeyboardButton(text="Возраст", callback_data="update_profile_update_age")],
        [InlineKeyboardButton(text="Город", callback_data="update_profile_update_city")],
        [InlineKeyboardButton(text="Статус", callback_data="update_profile_update_status")],
        [InlineKeyboardButton(text="Цель", callback_data="update_profile_update_goal")],
        [InlineKeyboardButton(text="Кто интересен", callback_data="update_profile_update_who_interested")],
        [InlineKeyboardButton(text="Описание", callback_data="update_profile_update_description")],
        [InlineKeyboardButton(text="Дата рождения", callback_data="update_profile_update_date_of_birth")],
        [InlineKeyboardButton(text="Селфи (фото лица)", callback_data="update_profile_update_face_photo")],
        [InlineKeyboardButton(text="Доп. фото", callback_data="update_profile_update_photo")],
        [InlineKeyboardButton(text="Назад", callback_data="update_back")],
    ]
)

my_profile_edit_olymps = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Добавить РСОШ/ВСОШ (авто)", callback_data="update_olymps_add_auto")],
        [InlineKeyboardButton(text="Добавить другую олимпиаду", callback_data="update_olymps_add_other")],
        [InlineKeyboardButton(text="Изменить видимость олимпиад", callback_data="update_olymps_update_visibility")],
        [InlineKeyboardButton(text="Назад", callback_data="update_back")],
                     ])