import telebot

import config
import time

from telebot import types
from db import BotDB
import threading

bot = telebot.TeleBot(config.TOKEN)
bot_name = bot.get_me().first_name
db_file = config.db_file
db = BotDB()
user_chosen_pic = dict()


def is_int(input_data):
    try:
        int(input_data)
        return True
    except ValueError:
        return False


def greeting_text(message):
    user = message.from_user
    return (
        f"Привет, {user.first_name}! \n\n"
        f"Это бот <a href='https://instagram.com/helpfulpics.ru'>«Полезных картинок»</a> – онлайн-галереи, где за донаты благотворительным организациям можно купить работы, созданные детьми.\n\n"
        f"Вы хотите купить работу или предложить? Выберите👇"

    )


@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("Купить ⬅")
    button2 = types.KeyboardButton("Предложить ➡")
    button3 = types.KeyboardButton("Галерея 🖼")
    button4 = types.KeyboardButton("Поддержка 🙋‍♂️")

    markup.add(button1, button2, button3, button4)

    pic = open('logo.png', 'rb')
    bot.send_photo(message.chat.id, pic)
    bot.send_message(message.chat.id, greeting_text(message), parse_mode='html', reply_markup=markup)


def get_address(message):
    client_address = message.text
    user_chat_id = message.chat.id
    picture_number = user_chosen_pic[user_chat_id]
    db.address_adding(picture_number, client_address)
    db.client_chat_id(picture_number, user_chat_id)
    markup = types.InlineKeyboardMarkup(row_width=2)
    option1 = types.InlineKeyboardButton('Россия 🇷🇺', callback_data='russia')
    option2 = types.InlineKeyboardButton('Мир 🌎', callback_data='not_russia')
    markup.add(option1, option2)
    bot.send_message(message.chat.id,
                     str("Отлично, адрес есть ✅\n\nПерейдем к выбору благотворительного проекта. Вы хотели бы перевести деньги в российский проект или тот, который осуществляет деятельность вне России?"),
                     reply_markup=markup)


@bot.message_handler(content_types=['text'])
def main_logic(message):
    if message.chat.type == 'private':
        if message.text == 'Купить ⬅':
            bot.send_message(message.chat.id,
                             str("Картинка может стать приятным подарком или милым украшением вашего дома. А еще покупкой вы ощутимо поможете тому, кто в этом нуждается."))
            time.sleep(3)
            bot.send_message(message.chat.id,
                             text="В <a href='https://instagram.com/helpfulpics.ru'>онлайн-галерее</a> у каждой картинки есть номер. Введите в чат номер той, которую вы хотите купить. Мы проверим, есть ли картинка в наличии.",
                             parse_mode='HTML')

        elif message.text == 'Предложить ➡':
            bot.send_message(message.chat.id,
                             str("Сфотографируйте работу и загрузите картинку в чат 📸"))

            db.adding_client_pic1(message.chat.id)

        elif message.text == 'Галерея 🖼':
            bot.send_message(message.chat.id,
                             text="Наша <a href='https://instagram.com/helpfulpics.ru'>онлайн-галерея</a>",
                             parse_mode='HTML')
        elif message.text == 'Поддержка 🙋‍♂️':
            bot.send_message(message.chat.id,
                             str("Перейдите, пожалуйста, в чат https://t.me/Eva_Schneider1 и отправьте свое сообщение поддержке."))

        elif "," not in message.text and is_int(message.text) and 1 <= int(message.text) <= 200:
            picture_number = int(message.text)
            pic_availab = db.pic_availability(picture_number)  # проверяем есть ли рисунок в наличии

            if int(pic_availab[0]) == 0:  # рисунок в базе- его уже купили
                bot.send_message(message.chat.id,
                                 text="Упс! Картинку уже купили ☹️\n\nНе расстраивайтесь, <a href='https://instagram.com/helpfulpics.ru'> в галерее</a> много других замечательных картинок. Посмотрите, может вам что-то понравится.",
                                 parse_mode='HTML')

            else:  # рисунок в базе- его еще НЕ купили
                # markup = types.InlineKeyboardMarkup(row_width=2)
                # option1 = types.InlineKeyboardButton('Купить в любом случае', callback_data='buy')
                # option2 = types.InlineKeyboardButton('Рассчитать стоимость доставки', callback_data='count')
                # markup.add(option1, option2)
                user_chosen_pic[message.chat.id] = picture_number
                bot.send_message(message.chat.id,
                                 text="Все на месте 🙂\n\nКартинки мы отправляем из Санкт-Петербурга за счет покупателя. Стоимость зависит от страны и города, размера и веса работы.\nВот тарифы отправки работы размера А4 в некоторые города:\n"
                                      "Москва – 153 руб\nЛондон – 273 руб\nБерлин – 313 руб\nНью-Йорк – 498 руб\nДубай – 518 руб\n\nТочную стоимость доставки вы можете рассчитать на сайте <a href='https://www.pochta.ru/letters'> Почты России.</a>",
                                 parse_mode='HTML')

                time.sleep(5)
                bot.send_message(message.chat.id,
                                 "Напишите адрес доставки картинки в формате «Индекс, Страна, Город, Улица, Номер дома, Квартира, ФИО получателя» 📨\n\nПример: 221 122, Великобритания, Лондон, Бейкер-стрит, 221Б, 3, Холмс Шерлок Петрович")

                bot.register_next_step_handler(message, get_address)
        # elif len((message.text).split(",")) > 3 and len((message.text).split(",")) < 12:
        # client_address = message.text
        # user_chat_id = message.chat.id
        # picture_number = user_chosen_pic[user_chat_id]
        # db.address_adding(picture_number, client_address)
        # db.client_chat_id(picture_number, user_chat_id)
        # markup = types.InlineKeyboardMarkup(row_width=2)
        # option1 = types.InlineKeyboardButton('Россия 🇷🇺', callback_data='russia')
        # option2 = types.InlineKeyboardButton('Мир 🌎', callback_data='not_russia')
        # markup.add(option1, option2)
        # bot.send_message(message.chat.id,
        # str("Отлично, адрес есть ✅\n\nПерейдем к выбору благотворительного проекта. Вы хотели бы перевести деньги в российский проект или тот, который осуществляет деятельность вне России?"),
        # reply_markup=markup)

        elif db.check_client_status_for_descr(message.chat.id) == 2:
            bot.send_message(message.chat.id, str("✅"))
            time.sleep(1)
            bot.send_message(message.chat.id,
                             str("Аккуратно упакуйте картинку в плотный конверт и отправьте нам (например, Почтой России).\nКому: Гусевой Валентине Владимировне \nКуда: 194356, Россия, Санкт-Петербург, ул. Композиторов, дом 4, кв 102\n\nМы обязательно сообщим вам о получении."))
            db.add_pic_info(message.chat.id, message.text)
            db.update_status_pic_sent(message.chat.id)

        else:
            bot.send_message(message.chat.id, str("Прости, я тебя не понимаю 😢."))


@bot.callback_query_handler(func=lambda call: call.data == 'russia' or call.data == 'not_russia')
def count_delivery_price(call):
    if call.data == 'russia':
        markup = types.InlineKeyboardMarkup(row_width=3)
        option1 = types.InlineKeyboardButton('Бабушка 👵', callback_data='babyshka')
        option2 = types.InlineKeyboardButton('Мята 🌱', callback_data='mint')
        option3 = types.InlineKeyboardButton('Центр ⛪️', callback_data='zentr')
        markup.add(option1, option2, option3)
        bot.send_message(call.message.chat.id,
                         text="1. <a href='https://specopbabushka.ru/'>Спецоперация Бабушка</a> – лекарства, дрова и продукты для бабушек и дедушек из маленьких деревень \n2. <a href='https://justmint.ru/'>Благотворительная организация «Мята» </a> – образование и профориентация для детей в трудной жизненной ситуации\n3. <a href='http://svtvasilij.ru/'>Центр святителя Василия Великого </a> – помощь подросткам, нарушившим закон, найти свой путь в мире с собой и обществом",
                         reply_markup=markup, parse_mode='HTML', disable_web_page_preview=True)

    # <a href='https://instagram.com/helpfulpics.ru'> в галерее</a>
    elif call.data == 'not_russia':
        markup = types.InlineKeyboardMarkup(row_width=3)
        option1 = types.InlineKeyboardButton('Кожен може 🏥', callback_data='kojen_moje')
        option2 = types.InlineKeyboardButton('Голоси Дiтей 👨‍👩‍👦‍👦', callback_data='golosi_ditey')
        option3 = types.InlineKeyboardButton('Помогаем уехать 🚗', callback_data='pomogaem_yehat')
        markup.add(option1, option2, option3)
        bot.send_message(call.message.chat.id,
                         text=" 1. <a href='https://everybodycan.com.ua/'> Кожен може</a> - помогает детям, пожилым людям и медицинским учреждениям по всей Украине\n2. <a href='https://voices.org.ua/en'>Голоси Дiтей </a> - помощь пострадавшим от войны детям и их родителям.\n3. <a href='https://helpingtoleave.org/uk'>Помогаем уехать</a>- занимается эвакуацией людей из горячих точек",
                         reply_markup=markup, parse_mode='HTML', disable_web_page_preview=True)


# @bot.callback_query_handler(func=lambda call: call.data == 'count' or call.data == 'buy')
# def count_delivery_price(call):
# if call.data == 'count':
# bot.send_message(call.message.chat.id,
# str("Перейдите, пожалуйста, в чат https://t.me/Eva_Schneider1 и отправьте свой адрес поддержке для расчета стомости доставки."))

# elif call.data == 'buy':
# bot.send_message(call.message.chat.id,
# str('Напишите адрес, куда отпавить картинку в формате «Индекс, Страна, Город, Улица, Номер дома, Квартира, ФИО получателя».'))


@bot.callback_query_handler(func=lambda
        call: call.data == 'babyshka' or call.data == 'mint' or call.data == 'zentr' or call.data == 'kojen_moje' or call.data == 'golosi_ditey' or call.data == 'pomogaem_yehat')
def choosing_project(call):
    if call.data == 'babyshka':
        bot.send_message(call.message.chat.id,
                         text="Вы решили помочь бабушкам и дедушкам 🙏\n\nПерейдите <a href='https://specopbabushka.ru/so_sbor/'>по ссылке</a> и перечислите «Спецоперации Бабушка» от 2000 руб. Фотографию или PDF чека отправьте в чат.",
                         parse_mode='HTML')
    elif call.data == 'mint':
        bot.send_message(call.message.chat.id,
                         text=" Вы решили помочь детям в трудной жизненной ситуации 🙏\n\nПерейдите <a href='https://justmint.ru/help/'>по ссылке </a> и перечислите «Мяте» от 2000 руб. Фотографию или PDF чека отправьте в чат.",
                         parse_mode='HTML')
    elif call.data == 'zentr':
        bot.send_message(call.message.chat.id,
                         text="Вы решили помочь подросткам, нарушившим закон 🙏\n\nПерейдите <a href='https://donate.svtvasilij.ru/'>по ссылке</a> и перечислите «Центру святителя Василия Великого» от 2000 руб. Фотографию или PDF чека отправьте в чат.",
                         parse_mode='HTML')
    elif call.data == 'kojen_moje':
        bot.send_message(call.message.chat.id,
                         text="Вы решили помочь людям в Украине 🙏\n\nПерейдите <a href='https://everybodycan.com.ua/dopomogti-zaraz'>по ссылке</a> и перечислите организации «Кожен може» от 30$. Фотографию или PDF чека отправьте в чат.",
                         parse_mode='HTML')
    elif call.data == 'golosi_ditey':
        bot.send_message(call.message.chat.id,
                         text="Вы решили помочь детям и их родителям, пострадавшим от войны 🙏\n\nПерейдите <a href='https://voices.org.ua/en/donat/'>по ссылке</a> и перечислите организации «Голоси Дiтей» от 30$. Фотографию или PDF чека отправьте в чат.",
                         parse_mode='HTML')
    elif call.data == 'pomogaem_yehat':
        bot.send_message(call.message.chat.id,
                         text="Вы решили помочь с эвакуацией людей из горячих точек 🙏\n\nПерейдите <a href='https://helpingtoleave.org/uk#donate'>по ссылке</a> и перечислите организации «Помогаем уехать» от 30$. Фотографию или PDF чека отправьте в чат.",
                         parse_mode='HTML')

    # bot.send_message(call.message.chat.id,
    # str("Спасибо большое!🙏 Загрузите, пожалуйста, чек файлом, чтобы мы проверили перевод."))


# прием чека
@bot.message_handler(content_types=['document', 'photo'])
def bill_receive(message):  # пересылаем чек менеджеру
    if not db.checking_client_to_download_pic(message.chat.id):
        user_name = message.from_user.username
        db.client_name_telegram(chat_id=message.chat.id, client_name_telegram=user_name)

        user_name = message.from_user.full_name
        db.client_name(chat_id=message.chat.id, name=user_name)

        forward_chat = config.manager_id  # id менеджера
        bot.forward_message(chat_id=forward_chat, from_chat_id=message.chat.id, message_id=message.id)
        bot.send_message(message.chat.id,
                         str("Спасибо. Нам требуется немного времени на проверку. Как все получится, мы сразу напишем."))
        picture_number = user_chosen_pic[message.chat.id]
        db.availability_update(picture_number)
    else:
        user_name = message.from_user.username
        user_full_name = message.from_user.full_name
        db.client_name_receive(chat_id=message.chat.id, name=user_full_name)

        raw = message.photo[0].file_id
        path = raw + ".jpg"
        file_info = bot.get_file(raw)
        downloaded_file = bot.download_file(file_info.file_path)
        with open(f'pics_received/{path}', 'wb') as new_file:
            new_file.write(downloaded_file)

        forward_chat = config.manager_id  # id менеджера
        bot.forward_message(chat_id=forward_chat, from_chat_id=message.chat.id, message_id=message.id)

        bot.send_message(message.chat.id,
                         str("Мы получили вашу работу. Нам нужно время, чтобы принять решение о том, сможем ли мы взять картинку в онлайн-галерею ⏳\n\nПодождите "))
        db.adding_client_pic(message.chat.id, user_name, user_full_name, path)


# прием картинки от клиента
# @bot.message_handler(content_types=['photo'])
# def pic_receive(message):  # пересылаем картинку менеджеру
# user_name = message.from_user.username
# user_full_name = message.from_user.full_name
# db.client_name_receive(chat_id=message.chat.id, name=user_full_name)

# raw = message.photo[2].file_id
# path = raw + ".jpg"
# file_info = bot.get_file(raw)
# downloaded_file = bot.download_file(file_info.file_path)
# with open(f'pics_received/{path}', 'wb') as new_file:
# new_file.write(downloaded_file)

# forward_chat = config.manager_id  # id менеджера
# bot.forward_message(chat_id=forward_chat, from_chat_id=message.chat.id, message_id=message.id)

# bot.send_message(message.chat.id,
# str("Мы получили вашу картинку. Нам нужно время, чтобы принять решение. Мы вам обязательно сообщим о том, сможем ли мы взять ее в галерею."))
# db.adding_client_pic(message.chat.id, user_name, user_full_name, path)


class BotThread(threading.Thread):

    def run(self) -> None:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
            bot.polling(none_stop=True)


BotThread().start()

while True:
    time.sleep(5)
    for client_id in db.bill_approved_client_ids():  # status=1
        client_chat_id = client_id[0]
        bot.send_message(client_chat_id,
                         'Благотворительная организация получила платеж! 🎉\n\nВ течение нескольких дней мы отправим посылку и вышлем вам трек-номер для отслеживания.')
        db.update_bill_approved_status(client_chat_id)  # status=2

    for client_id in db.track_number():  # status=2
        client_chat_id = client_id[0]
        track_number = client_id[1]
        bot.send_message(client_chat_id,
                         text=f"Письмо отправлено. Вот ваш трек номер: {track_number}. По нему <a href='https://www.pochta.ru/tracking'>на сайте Почты России</a> вы можете отслеживать местонахождение конверта.\n\nОриентировочное время доставки – 30 дней 💌",
                         parse_mode='HTML')

        db.update_envelope_status(client_chat_id)  # status=3

    for client_id in db.envelop_devilered():  # status=4
        client_chat_id = client_id[0]
        bot.send_message(client_chat_id,
                         "Нам пришло уведомление, что вы получили письмо 📭\n\nНадеемся, работа вам понравилась. Спасибо за участие в добром деле!\n\nМы будем очень благодарны, если вы расскажете о проекте в социальных сетях. Возможно, кто-то из ваших друзей прямо сейчас ищет способ кому-нибудь помочь.")
        db.finalise_purchase(client_chat_id)  # status=5

    # pic received

    for client_id in db.photo_pic_from_client_received():  # status=1
        client_chat_id = client_id[0]
        bot.send_message(client_chat_id,
                         'Вау! С радостью возьмем картинку в галерею.')
        db.update_photo_received_status(client_chat_id)  # status=2
        time.sleep(2)
        bot.send_message(client_chat_id,
                         text="Чтобы рассказать о картинке <a href='https://instagram.com/helpfulpics.ru'>в инстаграме</a>, нам нужна следующая информация:\n1. Название\n2. Имя и возраст художника\n3. Размер работы (в см)\n4. Короткая история создания",
                         parse_mode='HTML')

    for client_id in db.photo_pic_from_client_received_not_approve():  # status=10
        client_chat_id = client_id[0]
        bot.send_message(client_chat_id,
                         'Спасибо за уделенное время. Картинка замечательная, но мы не возьмемся разместить ее в галерее, так как не уверены, что сможем ее продать.\n\nПопробуйте загрузить другую картинку.')
        db.update_photo_received_status_not_approved(client_chat_id)

    for client_id in db.pic_received():  # status=4
        client_chat_id = client_id[0]
        bot.send_message(client_chat_id,
                         text="Мы получили работу, скоро разместим ее <a href='https://instagram.com/helpfulpics.ru'>в онлайн-галерее</a>.\n Подпишитесь, чтобы не пропустить.",
                         parse_mode='HTML')
        db.update_status_pic_sent_received(client_chat_id)

    for client_id in db.pic_received_sold():  # status=6
        client_chat_id = client_id[0]
        pic_name = db.get_sold_pic_info1(client_chat_id)
        pic_price = db.get_sold_pic_info2(client_chat_id)
        location = db.get_sold_pic_info3(client_chat_id)
        project_name = db.get_sold_pic_info4(client_chat_id)

        bot.send_message(client_chat_id,
                         f'🎉\n\nКартинка "{pic_name[0]}" продана за {pic_price[0]} долларов  и едет в {location[0]}. Деньги пошли на помощь подопечным организации "{project_name[0]}"!')
        time.sleep(5)
        bot.send_message(client_chat_id,
                         "Мы будем очень благодарны, если вы расскажете о проекте в социальных сетях. Возможно, кто-то из ваших друзей прямо сейчас хочет кому-нибудь помочь.")
        db.update_status_pic_sent_received_sold(client_chat_id)
