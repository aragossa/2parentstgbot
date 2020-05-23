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
    male = types.InlineKeyboardButton(text=user.select_message ('GENDER_MALE'), callback_data='add_quest_male')
    female = types.InlineKeyboardButton(text=user.select_message ('GENDER_FEMALE'), callback_data='add_quest_female')
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(male, female)
    return keyboard

def skip_game_question(user):
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text=user.select_message ('SKIP_QUESTION'), callback_data='add_quest_unknown')
    keyboard.add(btn1)
    return keyboard


def select_next_step(user):
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text=user.select_message ('GO_TO_AGGR'), url="t.me/ToParents_bot")
    keyboard.add(btn1)
    btn2 = types.InlineKeyboardButton(text=user.select_message ('ANSWER_QUESTIONS'), callback_data='nextstep_questions')
    keyboard.add(btn2)
    btn3 = types.InlineKeyboardButton(text=user.select_message ('ONE_MORE_TIME'), callback_data='onemore_yes')
    keyboard.add(btn3)
    return keyboard


def select_next_step_additional_question(user):
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text=user.select_message ('GO_TO_AGGR'), url="t.me/ToParents_bot")
    keyboard.add(btn1)
    btn2 = types.InlineKeyboardButton(text=user.select_message ('ONE_MORE_TIME'), callback_data='onemore_yes')
    keyboard.add(btn2)
    return keyboard


def take_test_again(user):
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text=user.select_message ('YES_ANSWER'), callback_data='onemore_yes')
    btn2 = types.InlineKeyboardButton(text=user.select_message ('NO_ANSWER'), callback_data='onemore_no')
    keyboard.add(btn1, btn2)
    return keyboard


def continue_test(user):
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text=user.select_message ('CONTINUE_TEST_BUTTON'), callback_data='continue')
    keyboard.add(btn1)
    return keyboard


