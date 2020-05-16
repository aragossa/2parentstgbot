import logging
import telebot
from dbconnector import Dbconnetor
from bot_user import Botuser

logging.basicConfig(
    filename='errors_aggr.log',
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
logger = telebot.logger
#apihelper.proxy = {'https': 'https://Z6dnQZ:s1Pg8b@77.83.185.165:8000'}

telebot.logger.setLevel(logging.INFO)
dbconnector = Dbconnetor()
TOKEN = dbconnector.get_config_parameter('api_token', 'aggr_bot')
bot = telebot.TeleBot(TOKEN, threaded=True)


@bot.message_handler(commands=['start'])
def handlestart(m):
    try:
        user = Botuser(uid=m.chat.id, bot=bot)
        last_name = m.from_user.last_name
        first_name = m.from_user.first_name
        username = m.from_user.username
        user.join_aggrbot(last_name=last_name, first_name=first_name, username=username, ref_key='Notset', lang='rus' )
        bot.send_message(chat_id=m.chat.id, text='Привет. Чат бот находится в разработке, скоро все будет готово')
    except:
        logging.exception(str(m))
        logging.exception('Got exception on main handler')



@bot.message_handler(content_types='text')
def simpletextmessage(m):
    user = Botuser(uid=m.chat.id, bot=bot)
    try:
        user.send_message_to_all_users(text=m.text)
    except:
        logging.exception(str(m))
        logging.exception('Got exception on main handler')
        user.send_message(message_index="ERROR_MESSAGE")

bot.polling(none_stop=True)
