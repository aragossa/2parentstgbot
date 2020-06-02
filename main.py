import logging
#import threading

import telebot
from telebot import apihelper

from bot_user import Botuser
from dbconnector import Dbconnetor
import starting_helper
from notificator import Notificator
from post_helper import enter_post_index

logging.basicConfig(
    filename='errors.log',
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
logger = telebot.logger



telebot.logger.setLevel(logging.INFO)
dbconnector = Dbconnetor()
use_proxy = dbconnector.get_config_parameter('proxy', 'global')
if use_proxy:
    apihelper.proxy = {'https': 'https://{}'.format(use_proxy)}
TOKEN = dbconnector.get_config_parameter('api_token', 'test_bot')
bot = telebot.TeleBot(TOKEN, threaded=True)
notificator = Notificator(bot=bot)


@bot.message_handler(commands=['start'])
def handlestart(m):
    user = Botuser(uid=m.chat.id, bot=bot)
    try:
        starting_helper.stating_handler(bot=bot, user=user, message=m)
    except:
        logging.exception(str(m))
        logging.exception('Got exception on main handler')
        user.send_message(message_index="ERROR_MESSAGE")


@bot.message_handler(commands=['reset'])
def handlestart(m):
    user = Botuser(uid=m.chat.id, bot=bot)
    try:
        user.reset_results()
        if user.get_user_lang():
            question_to_send = user.select_question_number_to_send()
            user.send_question(question_num=question_to_send)
        else:
            user.send_select_lang_message()
    except:
        logging.exception(str(m))
        logging.exception('Got exception on main handler')
        user.send_message(message_index="ERROR_MESSAGE")


@bot.message_handler(commands=['changelang'])
def handlestart(m):
    user = Botuser(uid=m.chat.id, bot=bot)
    try:
        user.send_select_lang_message()
    except:
        logging.exception(str(m))
        logging.exception('Got exception on main handler')
        user.send_message(message_index="ERROR_MESSAGE")


@bot.message_handler(commands=['sendpostbyindex'])
def sendpostbyindex(m):
    user = Botuser(uid=m.chat.id, bot=bot)
    try:
        enter_post_index(user)
    except:
        logging.exception(str(m))
        logging.exception('Got exception on main handler')
        user.send_message(message_index="ERROR_MESSAGE")


@bot.message_handler(content_types='text')
def simpletextmessage(m):
    user = Botuser(uid=m.chat.id, bot=bot)
    try:
        starting_helper.text_message_handler(bot=bot, user=user, input_value=m.text)
    except:
        logging.exception(str(m))
        logging.exception('Got exception on main handler')
        user.send_message(message_index="ERROR_MESSAGE")


@bot.callback_query_handler(func=lambda call: call.data[:5] == 'lang_')
def test_lang_handler(call):
    user = Botuser(uid=call.message.chat.id, bot=bot)
    try:
        starting_helper.language_selection_helper(call=call, user=user, bot=bot)
    except:
        logging.exception(str(call))
        logging.exception('Got exception on main handler')
        user.send_message(message_index="ERROR_MESSAGE")


@bot.callback_query_handler(func=lambda call: call.data[:7] == 'answer_')
def test_answer_handler(call):
    user = Botuser(uid=call.message.chat.id, bot=bot)
    try:
        starting_helper.user_answer_handler(call=call, user=user, bot=bot)
    except:
        logging.exception(str(call))
        logging.exception('Got exception on main handler')
        user.send_message(message_index="ERROR_MESSAGE")


@bot.callback_query_handler(func=lambda call: call.data[:9] == 'nextstep_')
def next_step_selection(call):
    user = Botuser(uid=call.message.chat.id, bot=bot)
    try:
        starting_helper.main_test_complite_handler(call=call, user=user, bot=bot)
    except:
        logging.exception(str(call))
        logging.exception('Got exception on main handler')
        user.send_message(message_index="ERROR_MESSAGE")


@bot.callback_query_handler(func=lambda call: call.data[:10] == 'add_quest_')
def next_step_selection(call):
    user = Botuser(uid=call.message.chat.id, bot=bot)
    try:
        starting_helper.additional_question_inline_handler(call=call, user=user, bot=bot)
    except:
        logging.exception(str(call))
        logging.exception('Got exception on main handler')
        user.send_message(message_index="ERROR_MESSAGE")


@bot.callback_query_handler(func=lambda call: call.data[:8] == 'onemore_')
def next_step_selection(call):
    user = Botuser(uid=call.message.chat.id, bot=bot)
    try:
        starting_helper.one_more_test_handler(call=call, user=user, bot=bot)
    except:
        logging.exception(str(call))
        logging.exception('Got exception on main handler')
        user.send_message(message_index="ERROR_MESSAGE")


@bot.callback_query_handler(func=lambda call: call.data[:8] == 'continue')
def next_step_selection(call):
    user = Botuser(uid=call.message.chat.id, bot=bot)
    try:
        starting_helper.send_continue_test(user=user)
    except:
        logging.exception(str(call))
        logging.exception('Got exception on main handler')
        user.send_message(message_index="ERROR_MESSAGE")


# th = threading.Thread(target=notificator.get_active_notifications, args=())
# th.start()


bot.polling(none_stop=True)
