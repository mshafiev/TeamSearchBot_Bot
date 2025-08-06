from aiogram.fsm.state import State, StatesGroup

class Registration(StatesGroup):
    first_name = State()
    last_name = State()
    middle_name = State()
    phone = State()
    age = State()
    city = State()
    status = State()
    goal = State()
    who_interested = State()
    description = State()
    date_of_birth = State()
    face_photo = State()
    photo = State()
    
    
class AddOlymp(StatesGroup):
    name = State()
    profile = State()
    year = State()
    result = State()