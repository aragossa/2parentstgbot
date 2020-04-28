import logging
import telebot
from telebot import apihelper

from bot_user import Botuser
from dbconnector import Dbconnetor
import starting_helper

logging.basicConfig(
    filename='errors.log',
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
logger = telebot.logger
apihelper.proxy = {'https': 'https://Z6dnQZ:s1Pg8b@77.83.185.165:8000'}

telebot.logger.setLevel(logging.INFO)
dbconnector = Dbconnetor()
TOKEN = dbconnector.get_config_parameter('api_token', 'test_bot')
bot = telebot.TeleBot(TOKEN, threaded=True)


@bot.message_handler(commands=['start'])
def handlestart(m):
    user = Botuser(uid=m.chat.id, bot=bot)
    try:
        ref_key = m.text.replace('/start ', '')
        if ref_key == ('/start'):
            ref_key=None
        starting_helper.check_status(user=user, ref_key=ref_key)
    except:
        logging.exception(str(m))
        logging.exception('Got exception on main handler')
        user.send_message(message_index="ERROR_MESSAGE")


@bot.message_handler(commands=['reset'])
def handlestart(m):
    user = Botuser(uid=m.chat.id, bot=bot)
    try:
        user.reset_results()
        if user.isauth():
            question_to_send = user.select_last_question()
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


"""
@bot.message_handler(content_types='text')
def simpletextmessage(m):
    try:
        user = Botuser(uid=m.chat.id, bot=bot)
        bot.send_message(chat_id=m.chat.id, text=m.text)
    except:
        logging.exception(str(m))
        logging.exception('Got exception on main handler')
        user.send_message(message_index="ERROR_MESSAGE")
"""




@bot.callback_query_handler(func=lambda call: call.data[:5] == 'lang_')
def test_answer_handler(call):
    try:
        lang = call.data[5:]
        user = Botuser(uid=call.message.chat.id, bot=bot)
        user.join_to_bot_users(lang=lang)
        send_message = user.select_message('JOIN_MESSAGE')
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=send_message)
        question_to_send = user.select_last_question()
        user.send_question(question_num=question_to_send)
    except:
        logging.exception(str(call))
        logging.exception('Got exception on main handler')
        user.send_message(message_index="ERROR_MESSAGE")


@bot.callback_query_handler(func=lambda call: call.data[:7] == 'answer_')
def test_answer_handler(call):
    try:
        data = call.data.split('_')
        answer = data[1]
        next_question_num = int(data[2])
        user = Botuser(uid=call.message.chat.id, bot=bot)
        user.save_answer(question_num=next_question_num - 1, answer=answer)
        max_count_questions = dbconnector.count_questions()
        edit_text = user.select_question(question_num=next_question_num - 1)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=edit_text)
        if next_question_num <= max_count_questions:

            user.send_question(question_num=next_question_num)
        else:
            user.send_message('GO_TO_AGGR')
    except:
        logging.exception(str(call))
        logging.exception('Got exception on main handler')
        user.send_message(message_index="ERROR_MESSAGE")


bot.polling(none_stop=True)
