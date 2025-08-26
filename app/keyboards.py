from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


start_without_all_fields = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='дозаполнить анкету')],
                                     ], resize_keyboard=True, input_field_placeholder="заполни анкету до конца")

start_reg = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='создать профиль')],
                                     ], resize_keyboard=True, input_field_placeholder="создай анкету для использования бота")

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='🚀'), KeyboardButton(text='👤'), KeyboardButton(text='✏️')],
                                     ], resize_keyboard=True)


wife_status = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="свободен(а)🔓")],
            [KeyboardButton(text="в отношениях 🔐")],
        ],
        resize_keyboard=True,
    )


goal = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="совместный бот 📚")],
            [KeyboardButton(text="общение 💬")],
            [KeyboardButton(text="поиск команды 👥")],
            [KeyboardButton(text="отношения 💞")],
        ],
        resize_keyboard=True,
    )

who_interested = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="девушки 💋")],
            [KeyboardButton(text="парни 🎩")],
            [KeyboardButton(text="все")],
        ],
        resize_keyboard=True,
    )


gender = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="парень")],
            [KeyboardButton(text="девушка")],
        ],
        resize_keyboard=True,
    )

olymp_result = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="победитель🥇")],
            [KeyboardButton(text="призер🥈")],
            [KeyboardButton(text="финалист")],
            [KeyboardButton(text="Участник")],
        ],
        resize_keyboard=True,
    )

my_profile_main = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="редактировать профиль", callback_data="update_profile")],
        [InlineKeyboardButton(text="редактировать достижения", callback_data="update_olymps")],
        [InlineKeyboardButton(text="удалить аккаунт ❌", callback_data="delete_account")],
                     ])

my_profile_edit_profile = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="имя", callback_data="update_profile_update_first_name")],
        [InlineKeyboardButton(text="фамилия", callback_data="update_profile_update_last_name")],
        [InlineKeyboardButton(text="отчество", callback_data="update_profile_update_middle_name")],
        [InlineKeyboardButton(text="возраст", callback_data="update_profile_update_age")],
        [InlineKeyboardButton(text="город", callback_data="update_profile_update_city")],
        [InlineKeyboardButton(text="статус", callback_data="update_profile_update_status")],
        [InlineKeyboardButton(text="цель", callback_data="update_profile_update_goal")],
        [InlineKeyboardButton(text="кто интересен", callback_data="update_profile_update_who_interested")],
        [InlineKeyboardButton(text="описание профиля", callback_data="update_profile_update_description")],
        [InlineKeyboardButton(text="дата рождения", callback_data="update_profile_update_date_of_birth")],
        [InlineKeyboardButton(text="селфи (фото лица)", callback_data="update_profile_update_face_photo")],
        [InlineKeyboardButton(text="доп. фото", callback_data="update_profile_update_photo")],
        [InlineKeyboardButton(text="Назад", callback_data="update_back")],
    ]
)

my_profile_edit_olymps = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="добавить РСОШ 📄 (авто) ", callback_data="update_olymps_add_auto")],
        [InlineKeyboardButton(text="добавить другое достижение🏅", callback_data="update_olymps_add_other")],
        [InlineKeyboardButton(text="изменить видимость достижений👁", callback_data="update_olymps_update_visibility")],
        [InlineKeyboardButton(text="Назад", callback_data="update_back")],
                     ])

rating_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="❤️"), KeyboardButton(text="👎"), KeyboardButton(text="💬"),  KeyboardButton(text="главное меню")]
    ],
    resize_keyboard=True
)

incoming_likes_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Показать, кому я понравился(ась) ❤️")],
        [KeyboardButton(text="Назад в меню")]
    ],
    resize_keyboard=True
)

incoming_like_reaction_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💋"), KeyboardButton(text="👎")]
    ],
    resize_keyboard=True
)