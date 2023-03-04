import telebot
import config
import time

from telebot import types
from db import BotDB
import threading

bot = telebot.TeleBot(config.TOKEN)
bot_name = bot.get_me().first_name
db_file = config.db_file
db = BotDB(db_file=db_file)
user_chosen_pic = dict()


def greeting_text(message):
    user = message.from_user
    return (
        f"Привет, {user.first_name}! 🙋‍♂️ \n"
        f"Я - <b>{bot_name}</b>, бот, который поможет тебе купить, "
        f"понравившийся рисунок из нашей онлайн-галереи или пополнить коллекцию и загрузить в нашу галерею свою картину."
    )


@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("Купить работу 🤗")
    button2 = types.KeyboardButton("Отправить работу 💌")
    button3 = types.KeyboardButton("Посмотреть работы 🖼")
    button4 = types.KeyboardButton("Обратная связь 🔄")

    markup.add(button1, button2, button3, button4)

    pic = open('/Users/evangelinaschnaider/Desktop/programming/IZO_BOT/sun.jpg', 'rb')
    bot.send_photo(message.chat.id, pic)
    bot.send_message(message.chat.id, greeting_text(message), parse_mode='html', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def main_logic(message):
    if message.chat.type == 'private':
        # print(len((message.text).split(",")))
        if message.text == 'Купить работу 🤗':
            bot.send_message(message.chat.id,
                             str("Здорово! Работа станет замечательным украшением вашего дома, а еще покупкой вы кому-то ощутимо поможете.🎨"))
            bot.send_message(message.chat.id,
                             str("В инстаграме в подписи к картинке вы найдете номер. Введите его сюда в чат,  чтобы проверить, есть ли картинка в наличии ⬇"))
        elif message.text == 'Отправить работу 💌':
            bot.send_message(message.chat.id, str("to be developed"))
        elif message.text == 'Посмотреть работы 🖼':
            bot.send_message(message.chat.id,
                             str("Наша онлайн-галерея: https://instagram.com/helpfulpics.ru"))
        elif message.text == 'Обратная связь 🔄':
            bot.send_message(message.chat.id,
                             str("Перейдите, пожалуйста, в чат https://t.me/Eva_Schneider1 и отправьте свое сообщение поддержке."))

        elif len((message.text).split(",")) == 1 and int(message.text) >= 1 and int(message.text) <= 100:
            picture_number = int(message.text)
            # print(picture_number)
            pic_availab = db.pic_availability(picture_number)  # проверяем есть ли рисунок в наличии
            # print(f"x={pic_availab[0]}")

            if int(pic_availab[0]) == 0:  # рисунок в базе- его уже купили
                bot.send_message(message.chat.id,
                                 str("Нам очень жаль, но кто-то успел купить картинку до вас. Посмотрите, может вам понравится какая-то еще."))

            else:  # рисунок в базе- его еще НЕ купили
                markup = types.InlineKeyboardMarkup(row_width=2)
                option1 = types.InlineKeyboardButton('Купить в любом случае', callback_data='buy')
                option2 = types.InlineKeyboardButton('Рассчитать стоимость доставки', callback_data='count')
                markup.add(option1, option2)
                user_chosen_pic[message.chat.id] = picture_number
                bot.send_message(message.chat.id,
                                 str("Хотим вас предупредить, что отправка за счет получателя. Мы отправляем из Санкт-Петербурга. До Берлина, например, стоит около 300 руб."),
                                 reply_markup=markup)

        elif len((message.text).split(",")) > 3:
            client_address = message.text
            user_chat_id = message.chat.id
            picture_number = user_chosen_pic[user_chat_id]
            # print(picture_number, client_address)
            db.address_adding(picture_number, client_address)
            db.client_chat_id(picture_number, user_chat_id)

            markup = types.InlineKeyboardMarkup(row_width=2)
            option1 = types.InlineKeyboardButton('Российский', callback_data='russia')
            option2 = types.InlineKeyboardButton('Вне России', callback_data='not_russia')
            markup.add(option1, option2)
            bot.send_message(message.chat.id,
                             str("Спасибо, адрес мы получили.📬 Перейдем к выбору благотворительного проекта. Вы хотели бы перевести деньги в российский проект или тот, который осуществляет деятельность вне России?"),
                             reply_markup=markup)

    print(user_chosen_pic)


@bot.callback_query_handler(func=lambda call: call.data == 'russia' or call.data == 'not_russia')
def count_delivery_price(call):
    if call.data == 'russia':
        markup = types.InlineKeyboardMarkup(row_width=3)
        option1 = types.InlineKeyboardButton('Проект 1', callback_data='Rus_project1')
        option2 = types.InlineKeyboardButton('Проект 2', callback_data='Rus_project2')
        option3 = types.InlineKeyboardButton('Проект 3', callback_data='Rus_project3')
        markup.add(option1, option2, option3)
        bot.send_message(call.message.chat.id,
                         str("Тут короткий рассказ о каждом из проектов. Буквально в одном предложении (кому помогают, на что и сколько собирают+ССЫЛКИ) (Russia) Перевести в ⬇"),
                         reply_markup=markup)


    elif call.data == 'not_russia':
        markup = types.InlineKeyboardMarkup(row_width=3)
        option1 = types.InlineKeyboardButton('Проект 1', callback_data='NOT_Rus_project1')
        option2 = types.InlineKeyboardButton('Проект 2', callback_data='NOT_Rus_project2')
        option3 = types.InlineKeyboardButton('Проект 3', callback_data='NOT_Rus_project3')
        markup.add(option1, option2, option3)
        bot.send_message(call.message.chat.id,
                         str('Тут короткий рассказ о каждом из проектов. Буквально в одном предложении (кому помогают, на что и сколько собирают+ССЫЛКИ) (NOT Russia) Перевести в ⬇'),
                         reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'count' or call.data == 'buy')
def count_delivery_price(call):
    if call.data == 'count':
        bot.send_message(call.message.chat.id,
                         str("Перейдите, пожалуйста, в чат https://t.me/Eva_Schneider1 и отправьте свой адрес поддержке для расчета стомости доставки."))

    elif call.data == 'buy':
        bot.send_message(call.message.chat.id,
                         str('Напишите адрес, куда отпавить картинку в формате «Индекс, Страна, Город, Улица, Номер дома, Квартира, ФИО получателя».'))


@bot.callback_query_handler(func=lambda
        call: call.data == 'Rus_project1' or call.data == 'Rus_project2' or call.data == 'Rus_project3' or call.data == 'NOT_Rus_project1' or call.data == 'NOT_Rus_project2' or call.data == 'NOT_Rus_project3')
def choosing_project(call):
    if call.data == 'Rus_project1':
        bot.send_message(call.message.chat.id,
                         str("Pеквизиты с припиской о том, что надо сделать скрин.(Rus проект1)"))
    elif call.data == 'Rus_project2':
        bot.send_message(call.message.chat.id,
                         str("Pеквизиты с припиской о том, что надо сделать скрин.(Rus проект2)"))
    elif call.data == 'Rus_project3':
        bot.send_message(call.message.chat.id,
                         str("Pеквизиты с припиской о том, что надо сделать скрин.(Rus проект3)"))
    elif call.data == 'NOT_Rus_project1':
        bot.send_message(call.message.chat.id,
                         str("Pеквизиты с припиской о том, что надо сделать скрин.(NOT_Rus проект1)"))
    elif call.data == 'NOT_Rus_project2':
        bot.send_message(call.message.chat.id,
                         str("Pеквизиты с припиской о том, что надо сделать скрин.(NOT_Rus проект2)"))
    elif call.data == 'NOT_Rus_project3':
        bot.send_message(call.message.chat.id,
                         str("Pеквизиты с припиской о том, что надо сделать скрин.(NOT_Rus проект3)"))

    bot.send_message(call.message.chat.id,
                     str("Спасибо большое!🙏 Загрузите, пожалуйста, картинку чека, чтобы мы проверили перевод."))


@bot.message_handler(content_types=['photo', 'document'])  # ???????
def bill_receive(message):  # пересылаем чек менеджеру
    user_name = message.from_user.username
    db.client_name_telegram(chat_id=message.chat.id, client_name_telegram=user_name)
    forward_chat = config.manager_id  # id менеджера
    bot.forward_message(chat_id=forward_chat, from_chat_id=message.chat.id, message_id=message.id)
    bot.send_message(message.chat.id,
                     str("Нам требуется немного времени на проверку. Как все получится, мы сразу напишем."))
    picture_number = user_chosen_pic[message.chat.id]
    print(picture_number)
    db.availability_update(picture_number)
    # db.update_bill_sent_status(message.chat.id)


# user_chosen_pic.keys()[0]
# user_chosen_pic[picture_number] = message.chat.id
# bill_presence= db.bill_sent(picture_number)
# run the bot

class BotThread(threading.Thread):

    def run(self) -> None:
        bot.polling(none_stop=True)


BotThread().start()

while True:
    time.sleep(5)
    for client_id in db.bill_approved_client_ids():  # status=1
        client_chat_id = client_id[0]
        bot.send_message(client_chat_id,
                         'Отлично, благотворительная организация получила платеж! В ближайшие дни мы отправим посылку и скинем вам трек-номер для отслежнивания!')
        db.update_bill_approved_status(client_chat_id)  # status=2

    for client_id in db.track_number():  # status=2
        client_chat_id = client_id[0]
        track_number = client_id[1]
        bot.send_message(client_chat_id,
                         f'Мы отправили конверт. Ориентировочное время доставки до 30 дней. Вот ваш трек номер, по которому вы можете отслеживать конверт на сайте Почты России {track_number}')
        db.update_envelope_status(client_chat_id)  # status=3

    for client_id in db.envelop_devilered():  # status=4
        client_chat_id = client_id[0]
        bot.send_message(client_chat_id,
                         'Нам пришло уведомление, что вы забрали конверт. Очень надеемся, что вам работа понравилась. Спасибо за участие в добром деле! Pасскажи о нас')
        db.finalise_purchase(client_chat_id)  # status=5
