from dbconnector import Dbconnetor
import time

def stating_handler(bot, user, message):
    if user.isauth():
        dbconnector = Dbconnetor()
        max_count_questions = dbconnector.count_questions()
        max_count_additional_questions = dbconnector.count_questions()
        question_to_send = user.select_question_number_to_send()
        additional_question_to_send = user.select_addtional_question_number_to_send()
        if question_to_send <= max_count_questions:
            user.send_question(question_num=question_to_send)
        elif additional_question_to_send <= max_count_additional_questions:
            user.send_additional_question(question_num=additional_question_to_send, test_type='ADD_TEST')
        else:
            user.send_message('GO_TO_AGGR')
    else:
        ref_key = message.text.replace('/start ', '')
        if ref_key == ('/start'):
            ref_key=None
        last_name = message.from_user.last_name
        first_name = message.from_user.first_name
        username = message.from_user.username
        check_status(user=user, ref_key=ref_key, last_name=last_name, first_name=first_name, username=username)

def check_status(user, ref_key, last_name, first_name, username):
    dbconnector = Dbconnetor()
    if not user.isauth():
        lang = user.check_status_new_user(ref_key)
        if lang:
            """ Добавление пользователя в базу с полученным языком """
            """ Отправка первого вопроса """
            user.join_to_bot_users(lang=lang, ref_key=ref_key, last_name=last_name, first_name=first_name, username=username)
            user.send_message(message_index='JOIN_MESSAGE')
            max_count_questions = dbconnector.count_questions()
            max_count_additional_questions = dbconnector.count_additional_questions()
            question_to_send = user.select_question_number_to_send()
            additional_question_to_send = user.select_addtional_question_number_to_send()
            if question_to_send <= max_count_questions:
                user.send_question(question_num=question_to_send)
            elif additional_question_to_send <= max_count_additional_questions:
                user.send_additional_question(question_num=additional_question_to_send, test_type='ADD_TEST')
            else:
                user.send_message(message_index='GO_TO_AGGR')

        else:
            user.send_select_lang_message()
    else:
        max_count_questions = dbconnector.count_questions()
        question_to_send = user.select_question_number_to_send()
        if question_to_send <= max_count_questions:

            user.send_question(question_num=question_to_send)
        else:
            user.send_message(message_index='GO_TO_AGGR')

def text_message_handler (bot, user, input_value):
    user_state = user.getstate()
    if user_state:
        if user_state.split('_')[2].isdigit():
            dbconnector = Dbconnetor()
            current_question = int(user_state.split('_')[2])
            question_to_send = current_question + 1
            user.save_answer(question_num=current_question, answer=input_value, test_type='ADD_TEST')
            max_count_additional_questions: int = dbconnector.count_additional_questions()
            if question_to_send <= max_count_additional_questions:
                user.send_additional_question(question_num=question_to_send, test_type='ADD_TEST')
            else:
                user.change_user_state('')
                user.send_message('GO_TO_AGGR')
        else:
            user.change_user_state('')
            user.send_message(message_index='HELLO_MESSAGE')

    else:
        user.send_message(message_index='HELLO_MESSAGE')

def language_selection_helper (call, user, bot):
    dbconnector = Dbconnetor()
    lang = call.data[5:]
    first_name = call.from_user.first_name
    username = call.from_user.username
    last_name = call.from_user.last_name
    user.join_to_bot_users(lang=lang, last_name=last_name, first_name=first_name, username=username)
    if not user.isauth():
        send_message = user.select_message('JOIN_MESSAGE')
    else:
        send_message = ('ok')
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=send_message)
    max_count_questions = dbconnector.count_questions()
    max_count_additional_questions = dbconnector.count_additional_questions()
    question_to_send = user.select_question_number_to_send()
    additional_question_to_send = user.select_question_number_to_send()
    if question_to_send <= max_count_questions:
        user.send_question(question_num=question_to_send)
    elif additional_question_to_send <= max_count_additional_questions:
        user.send_additional_question(question_num=question_to_send, test_type='ADD_TEST')
    else:
        user.send_message('GO_TO_AGGR')

def user_answer_handler (call, user, bot):
    dbconnector = Dbconnetor()
    data = call.data.split('_')
    answer = data[1]
    next_question_num = int(data[2])
    user.save_answer(question_num=next_question_num - 1, answer=answer, test_type='MAIN_TEST')
    max_count_questions = dbconnector.count_questions()
    edit_text = user.select_question(question_num=next_question_num - 1, test_type='MAIN_TEST')
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=edit_text)
    if next_question_num <= max_count_questions:
        user.send_question(question_num=next_question_num)
    else:
        user.send_main_test_results()
        time.sleep(5)
        user.send_message('ADD_TEST_START')
        user.send_additional_question(question_num=1, test_type='ADD_TEST')
