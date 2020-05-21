import logging
from telebot import types
import telebot
from telebot import apihelper

from dbconnector import Dbconnetor
from bot_user import Botuser

logging.basicConfig(
    filename='errors_aggr.log',
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
logger = telebot.logger

apihelper.proxy = {'https': 'https://Z6dnQZ:s1Pg8b@77.83.185.165:8000'}

telebot.logger.setLevel(logging.INFO)
dbconnector = Dbconnetor()
TOKEN = dbconnector.get_config_parameter('api_token', 'aggr_bot')
bot = telebot.TeleBot(TOKEN, threaded=True)
states = {}

@bot.message_handler(commands=['start'])
def handlestart(m):
    try:
        user = Botuser(uid=m.chat.id, bot=bot)
        last_name = m.from_user.last_name
        first_name = m.from_user.first_name
        username = m.from_user.username
        user.join_aggrbot(last_name=last_name, first_name=first_name, username=username, ref_key='Notset', lang='rus' )
        keyboard = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text='Поехали', callback_data='gogogo')
        keyboard.add(btn1)
        bot.send_message(chat_id=m.chat.id, text="""Добро пожаловать в Бот/Канал 2Parents

2Parents это сообщестов активных родителей и одновременно полигон для создания продукта, который позволит интерес ребенка к игре направить на достижения в реальной жизни.

Функционал бот/канала:
- блога сообщества
- обратная связь с администраторами
- возможность делиться кейсами борьбы с игрозависимостью
- в перспективе - первая версия продукта

Поехали!""", reply_markup=keyboard)
    except:
        logging.exception(str(m))
        logging.exception('Got exception on main handler')



@bot.message_handler(content_types='text')
def simpletextmessage(m):
    user = Botuser(uid=m.chat.id, bot=bot)

    try:
        if m.text == 'Написать администраторам':
            states[m.chat.id] = 'send_to_admin'
            hideBoard = types.ReplyKeyboardRemove()
            bot.send_message(chat_id=m.chat.id, text='Введите сообщение', reply_markup=hideBoard)
        elif states.get(m.chat.id) == 'send_to_admin':
            admins = [556047985]
            send_message = ('From user_id: {}\nMessage:{}'.format(m.chat.id, m.text))
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton('Написать администраторам')
            keyboard.add(btn1)
            bot.send_message(chat_id=m.chat.id, text='Введите сообщение', reply_markup=keyboard)
            states[m.chat.id] = ''
            for admin in admins:
                bot.send_message(chat_id=admin, text=send_message)
    except:
        logging.exception(str(m))
        logging.exception('Got exception on main handler')
        user.send_message(message_index="ERROR_MESSAGE")



@bot.callback_query_handler(func=lambda call: call.data == 'gogogo')
def gogogo_handler(call):
    user = Botuser(uid=call.message.chat.id, bot=bot)
    try:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Написать администраторам')
        keyboard.add(btn1)

        bot.send_message(chat_id=call.message.chat.id, text=""""Доброго дня!

Я - [Александр Зеленин](https://www.facebook.com/levopisanie). Предприниматель, психолог, отец, муж, искатель баланса во всем.

Мне не нравится как игры влияют не моих детей (и на детей в целом). Это не просто эмоция - крик моей отцовской совести. Это и логика тоже. Я наблюдаю, записываю, рефлексирую, делаю выводы. В конце-концов - протестировал детей и решил, что надо действовать как-то по новому.

До этого я пробовал справиться с игрозависимостью разными способами на протяжении 4 лет. Давал полную волю, ограничивал, использовал приложения Parents Control, вводил договоренности, по которым у детей было столько же времени на игры, сколько они занимаются спортом и творчеством. Даже создал для этого чат-бота. Но все это не решило проблему. Стремление играть постоянно растет, это сказывается на офлайн жизни, из-за чего мы с детьми ссоримся. При этом я не хочу отбирать у них гаджеты, понимая их пользу.

Последней каплей стал тест на игровую зависимость и контакта с одним из разработчиков игр. Оказалось, что его дети играют не более часа и он жестко это контролирует. Я так не хочу, я за экологичные решения, без жести. Поэтому, решил посмотреть на проблему шире, системнее. 

Это подсветило мне, что борьба с детьми - это путь в никуда, это отдаляет, разрывает контакт. Еще я понял, что основное зло в этой истории - игровые механизмы, вызывающие привыкание. Я понимаю, что это деньги, бизнес и серьезные структуры. Но точно так же я понимаю, что растет роль социального влияния и всегда можно найти третье решение, которое в какой-то степени будет удовлетворять все стороны. Вот такое решение я и решил найти. 

В поисках решения я не так давно. Буквально пару месяцев. За это время успел подсобрать информацию, пообщаться с девелоперами и найти единомышленников. Всего этого достаточно для того, чтобы уже назвать происходящее - проектом. 

Первым единомышленником стал Станислав Ефремов. Он же стал сооснователем проекта 2Parents. О себе Станислав расскажет сам.""", parse_mode='markdown', reply_markup=keyboard)
    except:
        logging.exception(str(call.message))
        logging.exception('Got exception on main handler')


bot.polling(none_stop=True)
