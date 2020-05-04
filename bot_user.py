import datetime

from dbconnector import Dbconnetor
from buttons_helper import select_language_keyboard, question_answers, additional_question_gender_answers, \
    additional_question_remove_keyboard


class Botuser():

    def __init__(self, uid, bot):
        self.uid = uid
        self.bot = bot
        self.dbconnector = Dbconnetor()

    def isauth(self):
        lang = self.dbconnector.execute_select_query(
            "SELECT lang from core.users WHERE users.user_id = {}".format(self.uid))
        if lang:
            return lang[0]

    def check_status_new_user(self, ref_key):
        result = self.dbconnector.execute_select_query(
            "SELECT lang FROM core.ref_keys WHERE ref_keys.ref_id = '{}' and ref_keys.interface = 'TG'".format(ref_key))
        if result:
            return result[0]

    def check_status_exist_user(self):
        pass

    def select_message(self, message_index):
        lang = self.isauth()
        if not lang:
            lang = 'rus'
        result = self.dbconnector.execute_select_query("""SELECT text FROM test_bot.messages
                                                       WHERE lang = '{0}'
                                                       AND message_index = '{1}'""".format(lang, message_index))
        if result:
            return result[0]

    def send_select_lang_message(self):
        text = self.select_message(message_index='START_MESSAGE')
        keyboard = select_language_keyboard()
        self.bot.send_message(chat_id=self.uid, text=text, reply_markup=keyboard)

    def send_message(self, message_index):
        text = self.select_message(message_index=message_index)
        self.bot.send_message(chat_id=self.uid, text=text)

    def select_question(self, question_num, test_type):
        lang = self.isauth()
        if not lang:
            lang = 'rus'
        result = self.dbconnector.execute_select_query("""SELECT text FROM test_bot.test_questions 
                                                       WHERE (lang = '{0}') 
                                                       AND (num = {1})
                                                       AND (test_type = '{2}')""".format(lang, question_num, test_type))
        if result:
            return result[0]

    def send_question(self, question_num, test_type='MAIN_TEST'):
        text = self.select_question(question_num=question_num, test_type=test_type)
        keyboard = question_answers(user=self, question_num=question_num)
        self.bot.send_message(chat_id=self.uid, text=text, reply_markup=keyboard)

    def send_additional_question(self, question_num, test_type='ADD_TEST'):
        text = self.select_question(question_num=question_num, test_type=test_type)
        if question_num == 2:
            keyboard = additional_question_gender_answers(user=self)
        else:
            keyboard = additional_question_remove_keyboard()
        self.change_user_state('{}_{}'.format(test_type, question_num))
        self.bot.send_message(chat_id=self.uid, text=text, reply_markup=keyboard)

    def join_to_bot_users(self, lang, last_name, first_name, username, ref_key='Notset'):
        self.dbconnector.execute_insert_query("""
        INSERT INTO core.users
	        ( ref_id, lang, interface, user_id, last_name, first_name, username, test_bot_join_date)
	    VALUES
	        ( '{0}', '{1}', 'TG', {2}, '{3}', '{4}', '{5}', current_timestamp )
	    ON CONFLICT ON CONSTRAINT idx_users
	    DO UPDATE SET lang = '{1}';""".format(ref_key, lang, self.uid, last_name, first_name, username))

        self.dbconnector.execute_insert_query("""
            INSERT INTO test_bot.users_state 
                ( user_id ) VALUES ({0})
            ON CONFLICT ON CONSTRAINT idx_users_state_user_id
	        DO NOTHING;""".format(self.uid))

    def join_aggrbot(self, last_name, first_name, username, ref_key='Notset', lang='rus' ):
        self.dbconnector.execute_insert_query("""
        INSERT INTO core.users
	        ( ref_id, lang, interface, user_id, last_name, first_name, username, aggregator_bot_join_date)
	    VALUES
	        ( '{0}', '{1}', 'TG', {2}, '{3}', '{4}', '{5}', current_timestamp )
	    ON CONFLICT ON CONSTRAINT idx_users
	    DO UPDATE SET aggregator_bot_join_date = current_timestamp;""".format(ref_key, lang, self.uid, last_name, first_name, username))

    def save_answer(self, question_num, answer, test_type):
        self.dbconnector.execute_insert_query("""
                INSERT INTO
                    test_bot.user_answers (user_id, answer, status, question_num, test_type)
	            VALUES ({}, '{}', 'ACTIVE', {} , '{}');""".format(self.uid, answer, question_num, test_type))

    def reset_results(self):
        self.dbconnector.execute_insert_query("""
                        UPDATE test_bot.user_answers SET status = 'DELETED' WHERE user_id = {};
                            """.format(self.uid))

    def select_question_number_to_send(self):
        max_count = self.dbconnector.execute_select_query(
            """SELECT question_num FROM test_bot.user_answers WHERE user_id = {} AND status = 'ACTIVE' AND test_type = 'MAIN_TEST' ORDER BY question_num DESC LIMIT 1""".format(
                self.uid))
        if max_count:
            return int(max_count[0]) + 1
        else:
            return 1

    def select_addtional_question_number_to_send(self):
        max_count = self.dbconnector.execute_select_query(
            """SELECT question_num FROM test_bot.user_answers WHERE user_id = {} AND status = 'ACTIVE' AND test_type = 'ADD_TEST' ORDER BY question_num DESC LIMIT 1""".format(
                self.uid))
        if max_count:
            return int(max_count[0]) + 1
        else:
            return 1

    def select_positive_answer(self):
        positive_answers = self.dbconnector.execute_select_query(
            """SELECT COUNT(answer) FROM test_bot.user_answers WHERE user_id = {} AND status = 'ACTIVE' AND test_type = 'MAIN_TEST' AND answer = '1'""".format(
                self.uid))
        if positive_answers:
            return int(positive_answers[0])
        else:
            return 0


    def getstate(self):
        status = self.dbconnector.execute_select_query(
            "SELECT user_state from test_bot.users_state WHERE user_id = {}".format(self.uid))
        if status:
            return status[0]

    def change_user_state(self, user_state):
        self.dbconnector.execute_insert_query("""
            UPDATE test_bot.users_state SET user_state = '{1}'
            WHERE user_id = {0};
        """.format(self.uid, user_state))

    def send_main_test_results(self):
        dbconnector = Dbconnetor()
        summ = 0
        result = self.dbconnector.execute_select_many_query(
            "SELECT answer from test_bot.user_answers WHERE user_id = {} AND test_type = 'MAIN_TEST' AND status = 'ACTIVE'".format(
                self.uid))
        for row in result:
            summ += int(row[0])
        print (summ)
        if summ <= 2:
            message_index = 'RESULT_MESSAGE_1'
        elif summ <= 4:
            message_index = 'RESULT_MESSAGE_2'
        elif summ <= 7:
            message_index = 'RESULT_MESSAGE_3'
        else:
            message_index = 'RESULT_MESSAGE_4'
        result_template = self.select_message(message_index=message_index)
        send_text = ('=============================\n\n')
        send_text += result_template
        positive_answer = self.select_positive_answer()
        all_questions = dbconnector.count_questions()
        percentage = int(round((positive_answer/all_questions) * 100, 0))
        send_text += ('\n\n=============================\n')
        send_text += self.select_message(message_index='SEND_PERCENTAGE').format(percentage)
        send_text += ('\n=============================\n')
        self.bot.send_message(chat_id=self.uid, text=send_text)

