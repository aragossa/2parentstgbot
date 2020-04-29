import datetime

from dbconnector import Dbconnetor
from buttons_helper import select_language_keyboard, question_answers


class Botuser():

    def __init__(self, uid, bot):
        self.uid = uid
        self.bot = bot
        self.dbconnector = Dbconnetor()

    def isauth(self):
        lang = self.dbconnector.execute_select_query("SELECT lang from core.users WHERE users.id = {}".format(self.uid))
        if lang:
            return lang[0]

    def check_status_new_user(self, ref_key):
        result = self.dbconnector.execute_select_query(
            "SELECT lang FROM core.ref_keys WHERE ref_keys.ref_id = '{}' and ref_keys.interface = 'TG'".format(ref_key))
        if result:
            return result[0]

    def select_message(self, message_index):
        lang = self.isauth()
        if not lang:
            lang = 'rus'
        result = self.dbconnector.execute_select_query("SELECT text FROM test_bot.messages "
                                                       "WHERE lang = '{0}' "
                                                       "AND message_index = '{1}'".format(lang, message_index))
        if result:
            return result[0]

    def send_select_lang_message(self):
        text = self.select_message(message_index='START_MESSAGE')
        keyboard = select_language_keyboard()
        self.bot.send_message(chat_id=self.uid, text=text, reply_markup=keyboard)

    def send_message(self, message_index):
        text = self.select_message(message_index=message_index)
        self.bot.send_message(chat_id=self.uid, text=text)

    def select_question(self, question_num):
        lang = self.isauth()
        if not lang:
            lang = 'rus'
        result = self.dbconnector.execute_select_query("SELECT text FROM test_bot.test_questions "
                                                       "WHERE lang = '{0}' "
                                                       "AND num = '{1}'".format(lang, question_num))
        if result:
            return result[0]

    def send_question(self, question_num):
        text = self.select_question(question_num=question_num)
        keyboard = question_answers(user=self, question_num=question_num)
        self.bot.send_message(chat_id=self.uid, text=text, reply_markup=keyboard)

    def join_to_bot_users(self, lang, ref_key='Notset'):
        self.dbconnector.execute_insert_query("""
        INSERT INTO core.users
	    ( ref_id, lang, interface, id, test_bot_join_date)
	    VALUES ( '{0}', '{1}', 'TG', {2}, '{3}')
	    ON CONFLICT ON CONSTRAINT pk_users_id
	    DO UPDATE SET lang = '{1}';
            """.format(ref_key, lang, self.uid, datetime.datetime.now()))

    def join_aggrbot (self, lang, ref_key='Notset'):
        self.dbconnector.execute_insert_query("""
        INSERT INTO core.users
	    ( ref_id, lang, interface, id, test_bot_join_date)
	    VALUES ( 'Notset', 'rus', 'TG', {0}, '{1}')
	    ON CONFLICT ON CONSTRAINT pk_users_id
	    DO UPDATE SET aggregator_bot_join_date = '{1}';
            """.format(self.uid, datetime.datetime.now()))

    def save_answer(self, question_num, answer):
        self.dbconnector.execute_insert_query("""
                INSERT INTO
                    test_bot.user_answers (user_id, answer, status, question_num)
	            VALUES ({}, {}, 'ACTIVE', {} );""".format(self.uid, answer, question_num))

    def reset_results(self):
        self.dbconnector.execute_insert_query("""
                        DELETE FROM test_bot.user_answers WHERE user_id = {};
                            """.format(self.uid))

    def select_last_question(self):
        max_count = self.dbconnector.execute_select_query("""select question_num from test_bot.user_answers where user_id = {} order by question_num desc limit 1""".format(self.uid))
        if max_count:
            return int(max_count[0]) + 1
        else:
            return 1

