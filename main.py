import handlers
import keyboards
import loaders
from loaders import bot, Users, now
from telebot.types import CallbackQuery, ReplyKeyboardRemove
from keyboards import calendar, calendar_in, calendar_out


@bot.message_handler(commands=['start'])
def send_welcome(message) -> None:
    """
    Стартовая команда для бота. Отправляет приветственное сообщение со ссылкой на команду /help

    :param message:
    :type message: Message

    :return: None
    """
    bot.send_message(message.from_user.id, 'Вас приветствует Easy Travel бот - бот для поиска отелей в Вашем городе.\n'
                                           'Для уточнения списка команд введите /help')


@bot.message_handler(commands=['help'])
def com_help(message) -> None:
    """
    Команда отправляет пользователю сообщение со списком доступных команд и их описанием

    :param message:
    :type message: Message

    :return: None
    """
    bot.send_message(message.from_user.id, loaders.help_text)


@bot.message_handler(commands=['lowprice'])
def lowprice(message) -> None:
    """
    Команда запускает процесс поиска самых дешёвых отелей в городе

    :param message:
    :type message: Message

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
    :type message: Message

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
    :type message: Message

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
    :type message: Message

    :return: None
    """
    pass


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_in.prefix))
def callback_inline_in(call: CallbackQuery):
    """
    Обработка inline callback запросов calendar_in-календаря
    Функция запрашивает дату выезда из отеля

    :param call:
    :return:
    """
    user = Users.get_user(call.from_user.id)
    name, action, year, month, day = call.data.split(calendar_in.sep)
    date = calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
    )
    if action == "DAY":
        if date.strftime('%Y-%m-%d') < now.strftime('%Y-%m-%d'):
            bot.send_message(call.from_user.id,
                             text='Дата заселения не может быть меньше сегодняшней.',
                             reply_markup=calendar.create_calendar(
                                 name=calendar_in.prefix,
                                 year=now.year,
                                 month=now.month))
        else:
            user.check_in = date.strftime('%Y-%m-%d')
            bot.send_message(call.from_user.id, text=f'Дата заселения: {user.check_in}.\nВыберите дату выезда:',
                             reply_markup=calendar.create_calendar(
                                 name=calendar_out.prefix,
                                 year=now.year,
                                 month=now.month))
    elif action == 'CANCEL':
        bot.send_message(call.from_user.id,
                         'Операция отменена.\n\n{help}'.format(help=loaders.help_text),
                         reply_markup=ReplyKeyboardRemove())


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_out.prefix))
def callback_inline_out(call: CallbackQuery):
    """
    Обработка inline callback запросов calendar_out-календаря
    Функция запрашивает у пользователя количество отелей, которое нужно показать

    :param call:
    :return:
    """
    user = Users.get_user(call.from_user.id)
    name, action, year, month, day = call.data.split(calendar_out.sep)
    date = calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
    )
    if action == "DAY":
        if date.strftime('%Y-%m-%d') <= user.check_in:
            bot.send_message(call.from_user.id,
                             text=f'Дата выезда не может быть меньше даты заселения.\nДата заселения: {user.check_in}',
                             reply_markup=calendar.create_calendar(
                                 name=calendar_out.prefix,
                                 year=now.year,
                                 month=now.month))
        else:
            user.check_out = date.strftime('%Y-%m-%d')
            bot.send_message(call.from_user.id, f'Дата заселения: {user.check_in}.\nДата выезда: {user.check_out}'
                                                f'\nСколько отелей показать?',
                             reply_markup=keyboards.hotels_num)
            bot.register_next_step_handler(call.message, handlers.num_photos, user)
    elif action == 'CANCEL':
        bot.send_message(call.from_user.id,
                         'Операция отменена.\n\n{help}'.format(help=loaders.help_text),
                         reply_markup=ReplyKeyboardRemove())


bot.infinity_polling()
