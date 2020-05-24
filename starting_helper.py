from buttons_helper import select_next_step, take_test_again,  \
    select_next_step_additional_question
from dbconnector import Dbconnetor
import time


def stating_handler(bot, user, message):
    if user.get_user_lang():
        dbconnector = Dbconnetor()
        max_count_questions = dbconnector.count_questions()
        max_count_additional_questions = dbconnector.count_additional_questions()
        question_to_send = user.select_question_number_to_send()
        additional_question_to_send = user.select_addtional_question_number_to_send()
        if question_to_send <= max_count_questions:
            user.send_question(question_num=question_to_send)
        elif additional_question_to_send <= max_count_additional_questions:
            user.send_additional_question(question_num=question_to_send, test_type='ADD_TEST')
        else:
            user.send_invintation_to_aggr_bot()
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
    if not user.get_user_lang():
        lang = user.check_status_new_user(ref_key)
        if lang:
            """ Добавление пользователя в базу с полученным языком """
            """ Отправка первого вопроса """
            user.join_to_bot_users(lang=lang, ref_key=ref_key, last_name=last_name, first_name=first_name, username=username)
            max_count_questions = dbconnector.count_questions()
            max_count_additional_questions = dbconnector.count_additional_questions()
            question_to_send = user.select_question_number_to_send()
            additional_question_to_send = user.select_addtional_question_number_to_send()
            if question_to_send == 1:
                if ref_key == None:
                    user.send_message(message_index='HELLO_MESSAGE')
                else:
                    user.send_message(message_index='HELLO_MESSAGE_NOURL')
                time.sleep(3)
                user.send_question(question_num=question_to_send)
            elif question_to_send <= max_count_questions:
                user.send_question(question_num=question_to_send)
            elif additional_question_to_send <= max_count_additional_questions:
                user.send_additional_question(question_num=additional_question_to_send, test_type='ADD_TEST')
            else:
                user.send_invintation_to_aggr_bot()

        else:
            user.send_select_lang_message()
    else:
        max_count_questions = dbconnector.count_questions()
        question_to_send = user.select_question_number_to_send()
        if question_to_send <= max_count_questions:

            user.send_question(question_num=question_to_send)
        else:
            user.send_invintation_to_aggr_bot()


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
                user.stop_notification()
                user.change_user_state('')
                send_thnx_message_text = user.select_message('THANKS_MESSAGE')
                keyboard = select_next_step_additional_question(user=user)
                user.bot.send_message(chat_id=user.uid, text=send_thnx_message_text, reply_markup=keyboard)




def language_selection_helper (call, user, bot):
    dbconnector = Dbconnetor()
    lang = call.data[5:]
    first_name = call.from_user.first_name
    username = call.from_user.username
    last_name = call.from_user.last_name
    user.join_to_bot_users(lang=lang, last_name=last_name, first_name=first_name, username=username)
    max_count_questions = dbconnector.count_questions()
    max_count_additional_questions = dbconnector.count_additional_questions()
    question_to_send = user.select_question_number_to_send()
    additional_question_to_send = user.select_question_number_to_send()
    if question_to_send <= 1:
        send_message = user.select_message('HELLO_MESSAGE')
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=send_message)
        time.sleep(3)
        user.send_question(question_num=question_to_send)
    elif question_to_send <= max_count_questions:
        user.send_question(question_num=question_to_send)
    elif additional_question_to_send <= max_count_additional_questions:
        user.send_additional_question(question_num=question_to_send, test_type='ADD_TEST')


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
        user.stop_notification()
        positive_answer = user.select_positive_answer()
        all_questions = dbconnector.count_questions()
        if positive_answer/all_questions <= 0.22:
            user.save_stats(0)
        elif positive_answer/all_questions <= 0.78:
            user.save_stats(1)
        elif positive_answer/all_questions > 0.78:
            user.save_stats(2)
        keyboard = select_next_step(user)
        user.send_main_test_results(keyboard=keyboard)

def additional_question_inline_handler(call, user, bot):
    dbconnector = Dbconnetor()
    data = call.data.split('_')
    answer = data[2]
    if answer == 'male' or answer == 'female':
        next_question_num = 3
        user.save_answer(question_num=next_question_num - 1, answer=answer, test_type='ADD_TEST')
        edit_text = user.select_question(question_num=next_question_num - 1, test_type='ADD_TEST')
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=edit_text)
        user.send_additional_question(question_num=next_question_num)
    elif answer == 'unknown':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text)
        user.save_answer(question_num=4, answer=answer, test_type='ADD_TEST')
        user.stop_notification()
        user.change_user_state('')
        send_thnx_message_text = user.select_message('THANKS_MESSAGE')
        keyboard = select_next_step_additional_question(user=user)
        user.bot.send_message(chat_id=user.uid, text=send_thnx_message_text, reply_markup=keyboard)




def main_test_complite_handler(call, user, bot):
    user_selection = call.data.split('_')[1]
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text)
    if user_selection == 'result':
        user.send_main_test_results()
        time.sleep(3)
        #user.set_thirty_sec_notification(notification_type='SEND_AGGR')
        bot.send_message(chat_id=user.uid, text=user.select_message('ONE_MORE_TEST'), reply_markup=take_test_again(user=user))
    elif user_selection == 'questions':
        user.send_additional_question(question_num=1, test_type='ADD_TEST')


def one_more_test_handler(call, user, bot):
    user.stop_notification()
    user_selection = call.data.split('_')[1]
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text)
    if user_selection == 'yes':
        user.add_child()
        time.sleep(3)
        user.send_question(question_num=1)
    elif user_selection == 'no':
        user.send_invintation_to_aggr_bot()


def send_continue_test(user):
    user.stop_notification()
    max_count_questions = user.dbconnector.count_questions()
    max_count_additional_questions = user.dbconnector.count_additional_questions()
    question_to_send = user.select_question_number_to_send()
    additional_question_to_send = user.select_addtional_question_number_to_send()
    if question_to_send <= max_count_questions:
        user.send_question(question_num=question_to_send)
    elif additional_question_to_send <= max_count_additional_questions:
        user.send_additional_question(question_num=additional_question_to_send, test_type='ADD_TEST')

