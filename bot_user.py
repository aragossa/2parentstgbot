import time

from dbconnector import Dbconnetor
from buttons_helper import select_language_keyboard, question_answers, additional_question_gender_answers, \
    additional_question_remove_keyboard, skip_game_question
import datetime


class Botuser():

    def __init__(self, uid, bot):
        self.uid = uid
        self.bot = bot
        self.dbconnector = Dbconnetor()

    def get_user_lang(self):
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
        lang = self.get_user_lang()
        if not lang:
            lang = 'rus'
        result = self.dbconnector.execute_select_query("""SELECT text FROM test_bot.messages
                                                       WHERE lang = '{0}'
                                                       AND message_index = '{1}'""".format(lang, message_index))
        if result:
            return str(result[0])

    def send_select_lang_message(self):
        text = self.select_message(message_index='START_MESSAGE')
        keyboard = select_language_keyboard()
        self.bot.send_message(chat_id=self.uid, text=text, reply_markup=keyboard)

    def send_message(self, message_index):
        text = self.select_message(message_index=message_index)
        self.bot.send_message(chat_id=self.uid, text=text)

    def select_question(self, question_num, test_type):
        lang = self.get_user_lang()
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
        if question_num == 10:
            question_num = 1
        new_state = ('{}_{}'.format(test_type, question_num))
        self.change_user_state(new_state)
        text = self.select_question(question_num=question_num, test_type=test_type)
        if question_num == 2:
            keyboard = additional_question_gender_answers(user=self)
        elif question_num == 3:
            keyboard = skip_game_question(user=self)
        elif question_num == 4:
            keyboard = skip_game_question(user=self)
        else:
            keyboard = additional_question_remove_keyboard()

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
                ( user_id, child_num ) VALUES ({0}, 1)
            ON CONFLICT ON CONSTRAINT idx_users_state_user_id
	        DO NOTHING;""".format(self.uid))

    def join_aggrbot(self, last_name, first_name, username, ref_key='Notset', lang='rus'):
        self.dbconnector.execute_insert_query("""
        INSERT INTO core.users
	        ( ref_id, lang, interface, user_id, last_name, first_name, username, aggregator_bot_join_date)
	    VALUES
	        ( '{0}', '{1}', 'TG', {2}, '{3}', '{4}', '{5}', current_timestamp )
	    ON CONFLICT ON CONSTRAINT idx_users
	    DO UPDATE SET aggregator_bot_join_date = current_timestamp;""".format(ref_key, lang, self.uid, last_name,
                                                                              first_name, username))

    def save_answer(self, question_num, answer, test_type):
        self.dbconnector.execute_insert_query("""
                INSERT INTO
                    test_bot.user_answers (user_id, answer, status, question_num, test_type, child_num)
	            VALUES ({}, '{}', 'ACTIVE', {} , '{}', (SELECT child_num FROM test_bot.users_state WHERE user_id = {}));""".format(
            self.uid, answer, question_num, test_type, self.uid))
        input_notification_datetime = datetime.datetime.now() + datetime.timedelta(minutes=30)
        self.dbconnector.execute_insert_query("""
                INSERT INTO test_bot.notifications
	            ( user_id, message_index, notification_datetime, notification_status) VALUES ( {}, 'REMINDE_TEST', '{}', 'NEW' )
                ON CONFLICT (user_id)
                DO UPDATE SET notification_datetime = '{}', message_index = 'REMINDE_TEST', notification_status = 'NEW';""".format(
            self.uid, input_notification_datetime, input_notification_datetime))

    def reset_results(self):
        self.dbconnector.execute_insert_query("""
                        UPDATE test_bot.user_answers SET status = 'DELETED' WHERE user_id = {};
                            """.format(self.uid))
        self.dbconnector.execute_insert_query("""
                        UPDATE test_bot.test_stat SET test_status = 'DELETED' WHERE user_id = {};
                            """.format(self.uid))
        self.dbconnector.execute_insert_query("""
                        UPDATE test_bot.users_state SET child_num = 1 WHERE user_id = {};
                            """.format(self.uid))

    def select_question_number_to_send(self):
        max_count = self.dbconnector.execute_select_query(
            """SELECT
                    question_num
               FROM
                    test_bot.user_answers
               WHERE
                    user_id = {}
               AND status = 'ACTIVE'
               AND test_type = 'MAIN_TEST'
               AND child_num = (SELECT child_num FROM test_bot.users_state WHERE user_id = {})
               ORDER BY question_num DESC LIMIT 1""".format(
                self.uid, self.uid))
        if max_count:
            return int(max_count[0]) + 1
        else:
            return 1

    def select_addtional_question_number_to_send(self):
        max_count = self.dbconnector.execute_select_query(
            """SELECT
                    question_num
                FROM
                    test_bot.user_answers
                WHERE user_id = {}
                AND status = 'ACTIVE'
                AND test_type = 'ADD_TEST'
                AND child_num = (SELECT child_num FROM test_bot.users_state WHERE user_id = {})
                ORDER BY question_num DESC LIMIT 1""".format(
                self.uid, self.uid))
        if max_count:
            return int(max_count[0]) + 1
        else:
            return 1

    def select_positive_answer(self):
        positive_answers = self.dbconnector.execute_select_query(
            """SELECT
                    COUNT(answer)
               FROM
                    test_bot.user_answers
               WHERE user_id = {}
               AND status = 'ACTIVE'
               AND test_type = 'MAIN_TEST'
               AND child_num = (SELECT child_num FROM test_bot.users_state WHERE user_id = {})
               AND answer = '1'""".format(
                self.uid, self.uid))
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

        query = """INSERT INTO test_bot.users_state
	        ( user_id,  user_state )
	    VALUES ( '{}', '{}' )
	    ON CONFLICT ON CONSTRAINT idx_users_state_user_id
	    DO UPDATE SET user_state = '{}';
        """.format(self.uid, user_state, user_state )
        self.dbconnector.execute_insert_query(query)

    def get_username(self):
        result = self.dbconnector.execute_select_many_query(
            "SELECT username, first_name, last_name from core.users WHERE user_id = {}".format(
                self.uid))
        if result[0] == 'None':
            return (result[1] + ' ' + result[2])
        else:
            return result[0]

    def send_message_to_all_users(self, text):
        result = self.dbconnector.execute_select_many_query(
            "SELECT user_id from core.users WHERE aggregator_bot_join_date IS NOT NULL")
        username = self.get_username()
        for user in result:
            send_msg = username + '\n' + text
            self.bot.send_message(chat_id=user, text=send_msg)
            time.sleep(1)

    def send_main_test_results(self, keyboard=None):
        dbconnector = Dbconnetor()
        positive_answer = self.select_positive_answer()
        all_questions = dbconnector.count_questions()
        percentage = int(round((positive_answer / all_questions) * 100, 0))
        user_lang = self.get_user_lang()
        if percentage == 0:
            sticker = open('imgs/{}_{}_percent.webp'.format(user_lang, percentage), 'rb')
            self.bot.send_sticker(self.uid, sticker)
            send_message =self.select_message(message_index='AGGR_BOT_GOOD')
            if keyboard:
                self.bot.send_message(chat_id=self.uid, text=send_message, reply_markup=keyboard)
            else:
                self.bot.send_message(chat_id=self.uid, text=send_message)
        else:
            sticker = open('imgs/{}_{}_percent.webp'.format(user_lang, percentage), 'rb')
            self.bot.send_sticker(self.uid, sticker)
            time.sleep(3)
            percentage = self.get_stats(percentage)
            if self.get_child_num() < 2:
                send_message = self.select_message(message_index='RESULT_MESSAGE_1').format(percentage)
            else:
                send_message = self.select_message(message_index='RESULT_MESSAGE_2').format(percentage)
            if keyboard:
                self.bot.send_message(chat_id=self.uid, text=send_message, reply_markup=keyboard)
            else:
                self.bot.send_message(chat_id=self.uid, text=send_message)

    def add_child(self):
        self.dbconnector.execute_insert_query("""
                UPDATE test_bot.users_state SET child_num = child_num + 1  WHERE user_id = {}""".format(self.uid))

    def send_invintation_to_aggr_bot(self):
        dbconnector = Dbconnetor()
        positive_answer = self.select_positive_answer()
        all_questions = dbconnector.count_questions()
        percentage = int(round((positive_answer / all_questions) * 100, 0))
        if percentage <= 22:
            self.send_message(message_index='AGGR_BOT_GOOD')
        else:
            stats = self.get_stats(percentage)
            send_text = (self.select_message('AGGR_BOT_BAD').format(stats))
            self.bot.send_message(chat_id=self.uid, text=send_text)

    def save_stats(self, test_result):
        self.dbconnector.execute_insert_query("""
                INSERT INTO test_bot.test_stat (user_id, test_result, child_num)
                VALUES ({}, {}, (SELECT child_num FROM test_bot.users_state WHERE user_id = {}))""".format(self.uid, test_result, self.uid))

    def get_stats(self, percentage):
        if percentage <= 77:
            test_result = 1
        else:
            test_result = 2
        all_answer = self.dbconnector.execute_select_query(
            "SELECT count(user_id) from test_bot.test_stat")
        bad_results = self.dbconnector.execute_select_query(
            "SELECT count(user_id) from test_bot.test_stat WHERE test_result = {}".format(test_result))
        percentage = round(bad_results[0]/all_answer[0] * 100, 0)
        return percentage

    def get_child_num(self):
        result = self.dbconnector.execute_select_query("""
            SELECT child_num FROM test_bot.users_state WHERE user_id = {};""".format(self.uid))
        if result:
            return result[0]

    def stop_notification(self):
        self.dbconnector.execute_insert_query("""
                UPDATE test_bot.notifications SET notification_status = 'CANCEL' WHERE user_id = {}""".format(self.uid))

    def set_thirty_sec_notification(self, notification_type):
        sticker = open('imgs/delimiter_bold.webp', 'rb')
        self.bot.send_sticker(self.uid, sticker)
        input_notification_datetime = datetime.datetime.now() + datetime.timedelta(seconds=30)
        self.dbconnector.execute_insert_query("""
                UPDATE test_bot.notifications
                SET
                    notification_status = 'NEW',
                    message_index = '{}', 
                    notification_datetime = '{}'
                    WHERE user_id = {}""".format(notification_type, input_notification_datetime, self.uid))

    def send_post_to_users(self, post_index):
        users = self.dbconnector.execute_select_many_query(
            "SELECT user_id from core.users WHERE test_bot_join_date IS NOT NULL")
        post = self.select_message(post_index)
        for user in users:
            self.bot.send_message(chat_id=user[0], text=post, parse_mode='Markdown')
            time.sleep(1)

