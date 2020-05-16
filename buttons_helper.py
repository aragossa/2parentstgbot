from telebot import types


def select_language_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='🇷🇺 Русский', callback_data='lang_rus')
    btn2 = types.InlineKeyboardButton(text='🇺🇸 English', callback_data='lang_eng')
    keyboard.add(btn1, btn2)
    return keyboard


def question_answers(user, question_num):
    next_question_num = question_num + 1
    keyboard = types.InlineKeyboardMarkup()
    yes_answer = user.select_message ('YES_ANSWER')
    no_answer = user.select_message('NO_ANSWER')
    btn1 = types.InlineKeyboardButton(text= yes_answer, callback_data='answer_1_{}'.format(next_question_num))
    btn2 = types.InlineKeyboardButton(text= no_answer, callback_data='answer_0_{}'.format(next_question_num))
    keyboard.add(btn1, btn2)
    return keyboard

def additional_question_remove_keyboard():
    keyboard = types.ReplyKeyboardRemove()
    return keyboard

def additional_question_gender_answers(user):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    male = types.KeyboardButton(user.select_message ('GENDER_MALE'))
    female = types.KeyboardButton(user.select_message ('GENDER_FEMALE'))
    keyboard.add(male, female)
    return keyboard