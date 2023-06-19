import telebot as tb
from telebot import types
bot = tb.TeleBot('5940817540:AAEWQEsqOUqCcVGqzie1nyCFBe9fNHztrVo')

from model import decode_sequence

user_data = {}
data = {
    'wiki': False,
    'bot_talk': False
}


@bot.message_handler(commands=['start'])
def start(message):
    user_data[message.from_user.id] = data.copy()
    print(user_data)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👋 Привет")
    markup.add(btn1)
    bot.send_message(message.from_user.id, "Привет! Я чат-бот!", reply_markup=markup)


wiki_activator = 'Хочу кое-что узнать про'


@bot.message_handler(func=lambda message: message.text == '👋 Привет', content_types=['text'])
def answer_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Хочу поговорить")
    btn2 = types.KeyboardButton(wiki_activator)
    markup.add(btn1, btn2)
    bot.send_message(message.from_user.id, "С чем тебе помочь?", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Хочу поговорить', content_types=['text'])
def start_bot_dialog(message):
    user_data[message.from_user.id]['bot_talk'] = True
    bot_reply = model.chat(['привет'])
    reply = bot_reply[0].numpy().decode()
    bot.send_message(message.from_user.id, reply)


@bot.message_handler(func=lambda message: message.text == 'Закончить диалог', content_types=['text'])
def end_bot_dialog(message):
    user_data[message.from_user.id]['bot_talk'] = False
    bot.send_message(message.from_user.id, 'Пока 😞')
    answer_message(message)


@bot.message_handler(func=lambda message: user_data[message.from_user.id]['bot_talk'] == True, content_types=['text'])
def get_bot_text(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Закончить диалог")
    bot_reply = decode_sequence([message.text])
    reply = bot_reply[0].numpy().decode()
    markup.add(btn1)
    bot.send_message(message.from_user.id, reply, reply_markup=markup)

bot.polling(none_stop=True, interval=0)
