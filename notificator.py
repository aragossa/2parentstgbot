import time

from bot_user import Botuser
from buttons_helper import continue_test
from dbconnector import Dbconnetor


class Notificator ():

    def __init__(self, bot):
        self.bot = bot
        self.dbconnector = Dbconnetor()

    def get_active_notifications(self):
        while True:

            self.dbconnector.execute_insert_query("SET TIME ZONE 'Europe/Moscow';")
            notifications = self.dbconnector.execute_select_many_query(
                """SELECT user_id, message_index
                   FROM test_bot.notifications
                   WHERE notification_status = 'NEW'
                   AND notification_datetime < current_timestamp""")
            for notification in notifications:
                user = Botuser(uid=notification[0], bot=self.bot)
                notification_type = notification[1]
                user.stop_notification()
                if notification_type == 'REMINDE_TEST':
                    keyboard = continue_test(user)
                    send_text = user.select_message('CONTINUE_TEST')
                    self.bot.send_message(chat_id=user.uid, text=send_text, reply_markup=keyboard)
                elif notification_type == 'SEND_RESULT':
                    user.send_main_test_results()
                    time.sleep(3)
                    user.send_invintation_to_aggr_bot()
                elif notification_type == 'SEND_AGGR':
                    user.send_invintation_to_aggr_bot()
            time.sleep(5)

