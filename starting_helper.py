import dbconnector
from dbconnector import Dbconnetor


def check_status(user, ref_key):
    dbconnector = Dbconnetor()
    if not user.isauth():
        lang = user.check_status_new_user(ref_key)
        if lang:
            """ Добавление пользователя в базу с полученным языком """
            """ Отправка первого вопроса """
            user.join_to_bot_users (lang=lang, ref_key=ref_key)
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


