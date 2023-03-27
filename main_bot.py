# Импортируем необходимые классы.
import datetime
import logging
import time

import aiohttp
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, MessageHandler, filters
from telegram.ext import CommandHandler, CallbackQueryHandler, ConversationHandler

BOT_TOKEN = '6288452612:AAEkJQqqid5enfM7iUOWHtV7jCaxXWCFgnk'
KEYS = dict()

# Запускаем логгирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

reply_keyboard = [['/help', '/start']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)


async def start_command(update, context):
    """Отправляет сообщение когда получена команда /start"""
    # user = update.effective_user
    # await update.message.reply_html(
    #     f"Привет {user.mention_html()}! Я ангел-бот. Напишите мне что-нибудь, и я пришлю это назад!",
    #     reply_markup=markup
    # )
    await update.message.reply_text(
        f"Я Бета Бот, охранник Троицка. Я помогу тебе познакомиться с этим городом. "
        f"\nНапишите мне /help, чтобы узнать, что я могу!",

        reply_markup=markup
    )


async def help_command(update, context):
    """Отправляет сообщение когда получена команда /help"""
    text = "Я могу помочь тебе\n" \
           "Используй такие команды:\n\n" \
           "/quiz - пройти квест\n" \
           "/walk - пойти гулять\n" \
           "/place - поиск мест\n" \
           "/new_place - добавить новое место\n" \
           "/site - сайт со всеми местами\n" \
           "/map - карта Троицка\n" \
           "/geocoder - тест картинок"
    await update.message.reply_text(text)


async def echo(update, context):
    await update.message.reply_text(f'Я получил сообщение "{update.message.text}"')


async def time_now(update, context):
    await update.message.reply_text(f'Время - {datetime.datetime.now().time().strftime("%H:%M")}')


async def date_now(update, context):
    await update.message.reply_text(f'Дата - {datetime.datetime.now().date().strftime("%d %B %Y")}')


# quiz - пройти квест
async def quiz_command(update, context):
    KEYS = []
    callback_button1 = InlineKeyboardButton(text="Хочу кушать", callback_data="food")
    callback_button2 = InlineKeyboardButton(text="Хочу гулять", callback_data="walk")
    callback_button3 = InlineKeyboardButton(text="Хочу жить", callback_data="life")
    callback_button_stop = InlineKeyboardButton(text="Выйти", callback_data="stop")

    keyboard = InlineKeyboardMarkup([[callback_button1, callback_button2, callback_button3], [callback_button_stop]])

    await context.bot.send_message(update.message.chat.id, "Начинается резня!!!", reply_markup=keyboard)
    return 1


async def quiz_ans1(call, context):
    print('ОБРАБОТЧИК ВЫЗВАН---------------------------------------------------------------')
    global KEYS
    KEYS.clear()
    ans = call.callback_query.data
    print(call, 'ASWER')
    if ans == 'food':
        KEYS['table_name'] = 'food'
        callback_button4 = InlineKeyboardButton(text="Фастфуд", callback_data="fastfood")
        callback_button5 = InlineKeyboardButton(text="Выпечка/Булочки", callback_data="snack")
        callback_button6 = InlineKeyboardButton(text="Ресторан", callback_data="rest")
        keyboard = InlineKeyboardMarkup([[callback_button4, callback_button5, callback_button6]])
    elif ans == 'walk':
        KEYS['table_name'] = 'walk'
        callback_button4 = InlineKeyboardButton(text="Парк", callback_data="park")
        callback_button5 = InlineKeyboardButton(text="Город", callback_data="city")
        # callback_button6 = InlineKeyboardButton(text="Ресторан", callback_data="rest")
        keyboard = InlineKeyboardMarkup([[callback_button4, callback_button5]])
    elif ans == 'life':
        KEYS['table_name'] = 'activity'
        callback_button4 = InlineKeyboardButton(text="Спорт", callback_data="sport")
        callback_button5 = InlineKeyboardButton(text="Релакс", callback_data="relax")
        # callback_button6 = InlineKeyboardButton(text="Ресторан", callback_data="rest")
        keyboard = InlineKeyboardMarkup([[callback_button4, callback_button5]])
    elif ans == 'stop':
        await call.callback_query.message.reply_text("Конец резни")
        return ConversationHandler.END

    await context.bot.send_message(call.callback_query.message.chat.id, "Начинается резня!!!", reply_markup=keyboard)
    return 2


async def quiz_ans2(call, context):
    print('ОБРАБОТЧИК ВЫЗВАН---------------------------------------------------------------')
    ans = call.callback_query.data
    print(call, 'ASWER')
    if ans == 'fastfood':
        KEYS['type'] = 'фастфуд'
        callback_button4 = InlineKeyboardButton(text="Пицца", callback_data="pizza")
        callback_button5 = InlineKeyboardButton(text="Шаурма", callback_data="shaurma")
        callback_button6 = InlineKeyboardButton(text="Бургер", callback_data="burger")
        keyboard = InlineKeyboardMarkup([[callback_button4, callback_button5, callback_button6]])
    elif ans == 'snack':
        KEYS['type'] = 'выпечка'
        callback_button4 = InlineKeyboardButton(text="Кофейня", callback_data="coffee")
        callback_button5 = InlineKeyboardButton(text="Булочная", callback_data="bread")
        keyboard = InlineKeyboardMarkup([[callback_button4, callback_button5]])
    elif ans == 'rest':
        KEYS['type'] = 'ресторан'
    elif ans == 'park':
        KEYS['type'] = 'парк'
        callback_button4 = InlineKeyboardButton(text="Лес", callback_data="forest")
        callback_button5 = InlineKeyboardButton(text="Река", callback_data="river")
        keyboard = InlineKeyboardMarkup([[callback_button4, callback_button5]])
    elif ans == 'city':
        KEYS['type'] = 'город'
    elif ans == 'sport':
        KEYS['type'] = 'спорт'
        callback_button4 = InlineKeyboardButton(text="Волейбол", callback_data="volleyball")
        callback_button5 = InlineKeyboardButton(text="Река", callback_data="river")
        keyboard = InlineKeyboardMarkup([[callback_button4, callback_button5]])
    elif ans == 'relax':
        KEYS['type'] = 'душа'

    await context.bot.send_message(call.callback_query.message.chat.id, "Начинается резня!!!", reply_markup=keyboard)
    return 3


async def stop(update, context):
    await update.message.reply_text("Конец резни")
    return ConversationHandler.END


# walk - пойти гулять
async def walk_command(update, context):
    arg = context.args
    print(arg, 'AGRSSSSSSSSSSSSSSSSSSSS')
    if arg:
        time.sleep(int(arg[0]))
    await update.message.reply_text(f'Перерыв окончен. Пора ботать, кожаный мешок')


# place - поиск мест
async def place_command(update, context):
    arg = context.args
    if arg:
        time.sleep(int(arg[0]))
    await update.message.reply_text(f'Перерыв окончен. Пора ботать, кожаный мешок')


# new_place - добавить новое место
async def new_place_command(update, context):
    text = 'Пока ничего нельзя добавить'
    await update.message.reply_text(text)
    await update.message.reply_text(text)


# site - сайт со всеми местами
async def site_command(update, context):
    link = 'https://absurdopedia.net/wiki/%D0%93%D0%BE%D1%80%D0%BE%D0%B4%D0%B0_%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D0%B8'
    text = 'Пока только так'
    await update.message.reply_text(link)
    await update.message.reply_text(text)


# map - карта Троицка
async def map_command(update, context):
    foto = f'files/map1.png'
    text = 'Пока только так'
    await context.bot.send_photo(update.message.from_user.id, open(foto, 'rb'))
    await update.message.reply_text(text)


TIMER = 5  # таймер на 5 секунд


def remove_job_if_exists(name, context):
    """Удаляем задачу по имени.
    Возвращаем True если задача была успешно удалена."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def task(context):
    """Выводит сообщение"""
    await context.bot.send_message(context.job.chat_id, text=f'КУКУ! 5c. прошли!')


async def set_timer(update, context):
    """Добавляем задачу в очередь"""
    chat_id = update.effective_message.chat_id
    # Добавляем задачу в очередь
    # и останавливаем предыдущую (если она была)
    job_removed = remove_job_if_exists(str(chat_id), context)
    context.job_queue.run_once(task, TIMER, chat_id=chat_id, name=str(chat_id), data=TIMER)

    text = f'Вернусь через 5 с.!'
    if job_removed:
        text += ' Старая задача удалена.'
    await update.effective_message.reply_text(text)


async def unset(update, context):
    """Удаляет задачу, если пользователь передумал"""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Таймер отменен!' if job_removed else 'У вас нет активных таймеров'
    await update.message.reply_text(text)


# async def chekan(update, context):
#     foto = random.randint(0, 5)
#     await update.get_bot().send_photo(update.message.from_user.id, open(f'files/chekan{foto}.png', 'rb'))
#
#
# async def chekan_voice(update, context):
#     video = random.randint(0, 0)
#     await update.get_bot().send_video(update.message.from_user.id, open(f'files/chekan_voice{video}.mp4', 'rb'))

async def get_response(url, params):
    logger.info(f"getting {url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            return await resp.json()


async def geocoder(update, context):
    text = 'Москва Троицк'
    geocoder_uri = "http://geocode-maps.yandex.ru/1.x/"
    response = await get_response(geocoder_uri, params={
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "format": "json",
        "geocode": text
    })
    print(response)
    print(response["response"]["GeoObjectCollection"])
    toponym = response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
    print(toponym)

    toponym_coodrinates = toponym["Point"]["pos"]
    # Долгота и широта:
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
    delta = "0.009"

    ll, spn = ",".join([toponym_longitude, toponym_lattitude]), ",".join([delta, delta]),
    # Можно воспользоваться готовой функцией,
    # которую предлагалось сделать на уроках, посвящённых HTTP-геокодеру.

    static_api_request = f"http://static-maps.yandex.ru/1.x/?ll={ll}&spn={spn}&l=map"
    await context.bot.send_photo(
        update.message.chat_id,  # Идентификатор чата. Куда посылать картинку.
        # Ссылка на static API, по сути, ссылка на картинку.
        # Телеграму можно передать прямо её, не скачивая предварительно карту.
        static_api_request,
        caption="Нашёл:"
    )


# async def callback_inline(call, context):
#     # Если сообщение из чата с ботом
#     print(call, ' CALLLL')
#     print(call.callback_query.data, 'AMOGUS')
#     print('------------------------------------------------------------')
#     # if call.message:
#     #     if call.data == "test":
#     #         context.bot.send_message(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Пыщь")
#     # # Если сообщение из инлайн-режима
#     # elif call.inline_query:
#     #     if call.data == "test":
#     await context.bot.send_message(call.callback_query.from_user.id, 'ура')


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    text_handler = MessageHandler(filters.TEXT, echo)
    # application.add_handler(text_handler)
    conv_handler_quiz = ConversationHandler(
        # Точка входа в диалог.
        entry_points=[CommandHandler('quiz', quiz_command)],
        # Состояние внутри диалога.
        states={
            # Функция читает ответ на первый вопрос и задаёт второй.
            1: [CallbackQueryHandler(quiz_ans1)],
            # Функция читает ответ на второй вопрос и завершает диалог.
            2: [CallbackQueryHandler(quiz_ans2)]
        },
        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop)]
    )

    application.add_handler(conv_handler_quiz)

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("time", time_now))
    application.add_handler(CommandHandler("date", date_now))

    application.add_handler(CommandHandler("walk", walk_command))
    application.add_handler(CommandHandler("place", place_command))
    application.add_handler(CommandHandler("new_place", new_place_command))
    application.add_handler(CommandHandler("site", site_command))
    application.add_handler(CommandHandler("map", map_command))

    application.add_handler(CommandHandler("set", set_timer))
    application.add_handler(CommandHandler("unset", unset))
    application.add_handler(CommandHandler("geocoder", geocoder))
    # application.add_handler(CommandHandler("chekan", chekan))
    # application.add_handler(CommandHandler("chekan_voice", chekan_voice))

    # application.add_handler(CallbackQueryHandler(callback_inline))

    application.run_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
