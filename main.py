import handlers
from loaders import bot
from loaders import Users
from telebot.types import CallbackQuery
from keyboards import calendar, calendar_in, custom_keyboard


@bot.message_handler(commands=['start'])
def send_welcome(message) -> None:
    """
    Стартовая команда для бота. Отправляет приветственное сообщение со ссылкой на команду /help

    :param message:
    :return: None
    """
    bot.send_message(message.from_user.id, 'Вас приветствует Easy Travel бот - бот для поиска отелей в Вашем городе.\n'
                                           'Для уточнения списка команд введите /help')


@bot.message_handler(commands=['help'])
def com_help(message) -> None:
    """
    Команда отправляет пользователю сообщение со списком доступных команд и их описанием

    :param message:
    :return: None
    """
    bot.send_message(message.from_user.id, 'Доступные команды:\n /lowprice - поиск самых дешёвых отелей в городе\n '
                                           '/highprice - поиск самых дорогих отелей в городе\n '
                                           '/bestdeal - поиск отелей наиболее подходящих по цене '
                                           'и удалённости от центра города\n '
                                           '/history - вывод истории поиска отелей')


@bot.message_handler(commands=['lowprice'])
def lowprice(message) -> None:
    """
    Команда запускает процесс поиска самых дешёвых отелей в городе

    :param message:
    :return: None
    """
    user = Users.get_user(message.from_user.id)
    user.command = '/lowprice'
    bot.send_message(message.from_user.id, 'Введите название города:')
    bot.register_next_step_handler(message, handlers.city, user)


@bot.message_handler(commands=['highprice'])
def highrice(message) -> None:
    """
    Команда запускает процесс поиска самых дорогих отелей в городе

    :param message:
    :return: None
    """
    user = Users.get_user(message.from_user.id)
    user.command = '/highprice'
    bot.send_message(message.from_user.id, 'Введите название города:')
    bot.register_next_step_handler(message, handlers.city, user)


@bot.message_handler(commands=['bestdeal'])
def bestdeal(message) -> None:
    """
    Команда запускает процесс поиска отелей наиболее подходящих по цене и удалённости от центра города

    :param message:
    :return: None
    """
    user = Users.get_user(message.from_user.id)
    user.command = '/bestdeal'
    bot.send_message(message.from_user.id, 'Введите название города:')
    bot.register_next_step_handler(message, handlers.city, user)


@bot.message_handler(commands=['history'])
def history(message) -> None:
    """
    Команда отправляет пользователю историю его запросов к данному боту

    :param message:
    :return: None
    """
    pass


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_in.prefix))
def callback_inline(call: CallbackQuery):
    """
    Обработка inline callback запросов календаря

    :param call:
    :return:
    """
    name, action, year, month, day = call.data.split(calendar_in.sep)
    date = calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
    )
    if action == "DAY":
        markup = custom_keyboard([date.strftime('%Y-%m-%d')])
        bot.send_message(
            chat_id=call.from_user.id,
            text=date.strftime('%Y-%m-%d'),
            reply_markup=markup)


bot.infinity_polling()
