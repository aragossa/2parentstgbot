from dbconnector import Dbconnetor


def check_status(user, ref_key):
    dbconnector = Dbconnetor()
    if not user.isauth():
        lang = user.check_status_new_user(ref_key)
        if lang:
            """ Добавление пользователя в базу с полученным языком """
            """ Отправка первого вопроса """
            user.join_to_bot_users (lang=lang, ref_key=ref_key)
            user.send_message('JOIN_MESSAGE')
            max_count_questions = dbconnector.count_questions()
            question_to_send = user.select_last_question()
            if question_to_send <= max_count_questions:

                user.send_question(question_num=question_to_send)
            else:
                user.send_message('GO_TO_AGGR')

        else:
            user.send_select_lang_message()
    else:
        max_count_questions = dbconnector.count_questions()
        question_to_send = user.select_last_question()
        if question_to_send <= max_count_questions:

            user.send_question(question_num=question_to_send)
        else:
            user.send_message('GO_TO_AGGR')



