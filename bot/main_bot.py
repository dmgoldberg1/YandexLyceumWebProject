# Импортируем необходимые классы.
import datetime
import logging
import os
import time
import torch
import torch.nn as nn
import torchvision.transforms as transforms
import timm
from PIL import Image
import requests
from io import StringIO
import aiohttp
import sqlite3
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, MessageHandler, filters
from telegram.ext import CommandHandler, CallbackQueryHandler, ConversationHandler

BOT_TOKEN = '6288452612:AAEkJQqqid5enfM7iUOWHtV7jCaxXWCFgnk'
KEYS = list()
ANS_COUNT = 0

# Запускаем логгирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)
reply_keyboard = [['/help', '/start']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

model = timm.create_model("resnest50d", pretrained=False)
num_features = model.fc.in_features
model.fc = nn.Linear(num_features, 3)
model.load_state_dict(torch.load('trobot_classifier2.pth', map_location=torch.device('cpu')))
model.eval()

LEVELS = {
    1: (1, 55.468117, 37.296497),
    2: (2, 55.475614, 37.299292, 'волейбольной площадки'),
    3: (1, 55.484520, 37.304923, 'фонтана'),
    4: (0, 55.495157, 37.305522, 'уточки')
}


def predict_image(image, level):
    img = Image.open(image)
    transform_norm = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(244),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    # get normalized image
    img_normalized = transform_norm(img).float()
    img_normalized = img_normalized.unsqueeze_(0)
    # input = Variable(image_tensor)
    # print(img_normalized.shape)
    with torch.no_grad():
        model.eval()
        output = model(img_normalized)
        p = torch.nn.functional.softmax(output, dim=1)
        probs = [p[0][0].item(), p[0][1].item(), p[0][2].item()]
        max_ind = probs.index(max(probs))
        print(probs)
        print(max_ind)
        if LEVELS[level][0] == max_ind and max(probs) > 0.75:
            return True
        else:
            return False


def check_keys(keys):
    result = []
    db = sqlite3.connect('trobot.db')
    cursor = db.cursor()
    request = f'''SELECT * FROM {keys[0]}'''
    data = cursor.execute(request).fetchall()
    for obj in data:
        # print(set(keys[1]), 'НАШИ КЛЮЧИ-------------------------')
        # print(set(obj[1].split()), 'КЛЮЧИ БД-------------------------')
        if set(keys[1]) == set(obj[1].split()):
            result.append(obj[0])
    db.close()
    return result


def get_coordinates(place, keys):
    coordinates = []
    print(place, 'ВНУТРИ ФУНКЦИИ')
    db = sqlite3.connect('trobot.db')
    cursor = db.cursor()
    request = f'''SELECT coors FROM {keys[0]} WHERE name = ?'''
    coors = cursor.execute(request, (place,)).fetchall()
    # print(coors[0][0])
    coordinates.append(coors[0][0].split(', '))
    print(coordinates)
    db.close()
    return coordinates


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


async def photo_game(update, context):
    print("Получил фото------------------------")
    #print(update)
    db = sqlite3.connect('game.db')
    cursor = db.cursor()
    user_id = update.message.chat.id
    level = cursor.execute("SELECT level FROM main_game WHERE user_id = ?", (user_id,)).fetchone()[0]
    r = requests.get((await context.bot.getFile(update.message.photo[0].file_id)).file_path)
    if r.status_code == 200:
        with open("image.jpg", 'wb') as f:
            f.write(r.content)
    print('DOWNLOADED')
    if predict_image('image.jpg', level):
        print('УРОВЕНЬ ПРОЙДЕН')
        cursor.execute('UPDATE main_game SET level = ? WHERE user_id = ?', (level + 1, user_id, ))
        db.commit()
        os.remove('image.jpg')
        message = 'Молодец! Ты справился с уровнем! Для продолжения напиши команду /game'
        await context.bot.send_message(update.message.chat.id, message)
    else:
        print('УРОВЕНЬ ПРОВАЛЕН')
        message = 'Ты отправил мне какой-то бред)'
        await context.bot.send_message(update.message.chat.id, message)


async def main_game(update, context):
    db = sqlite3.connect('game.db')
    cursor = db.cursor()
    user_id = update.message.chat.id
    nickname = update.message.chat.first_name + ' ' + update.message.chat.last_name
    #print(update)
    res = cursor.execute("SELECT user_id FROM main_game").fetchall()
    ids = [i[0] for i in res]
    if user_id not in ids:
        print('НОВЫЙ ПОЛЬЗОВАТЕЛЬ------------------------')
        cursor.execute("INSERT INTO main_game (user_id, nickname, level) VALUES (?, ?, ?)", (user_id, nickname, 1,))
        db.commit()
        message1 = 'Привет! Ты попал в программу "Сдохни или умри". В этой игре есть несколько уровней. Задача каждого ' \
                  'уровня - отправить фотографию предлагаемого объекта в Троицке. Тебе будет дана точка на карте, ' \
                  'до которой тебе нужно добраться. За каждое выполненное задание ты будешь получать очки! Удачи! '
        message2 = 'Задание 1\nПройди на точку и отправь фото фонтана.'

        await context.bot.send_message(update.message.chat.id, message1)
        await context.bot.send_message(update.message.chat.id, message2)
        await context.bot.send_location(update.message.chat.id, LEVELS[1][1], LEVELS[1][2])
    else:
        info = cursor.execute("SELECT level FROM main_game WHERE user_id = ?", (user_id, )).fetchone()[0]
        message1 = f'''С возвращением!\nТвой текущий уровень - {info}'''
        message2 = f'''Тебе нужно пройти к точке и отправить мне фото {LEVELS[info][3]}'''
        await context.bot.send_message(update.message.chat.id, message1)
        await context.bot.send_message(update.message.chat.id, message2)
        await context.bot.send_location(update.message.chat.id, LEVELS[info][1], LEVELS[info][2])


async def clear_database(update, context):
    db = sqlite3.connect('game.db')
    cursor = db.cursor()
    cursor.execute('DELETE FROM main_game')
    db.commit()


# quiz - пройти квест
async def quiz_command(update, context):
    callback_button1 = InlineKeyboardButton(text="Хочу кушать", callback_data="food")
    callback_button2 = InlineKeyboardButton(text="Хочу гулять", callback_data="walk")
    callback_button3 = InlineKeyboardButton(text="Хочу жить", callback_data="activity")
    callback_button_stop = InlineKeyboardButton(text="Выйти", callback_data="stop")

    keyboard = InlineKeyboardMarkup([[callback_button1, callback_button2, callback_button3], [callback_button_stop]])

    await context.bot.send_message(update.message.chat.id, "Чем вы хотите заняться?!!!", reply_markup=keyboard)
    return 1


async def quiz_ans1(call, context):
    print('ОБРАБОТЧИК ВЫЗВАН---------------------------------------------------------------')
    global KEYS
    KEYS.clear()
    ans = call.callback_query.data
    KEYS.append(ans)
    print(KEYS, "КЛЮЧИ 1 ОТВЕТ--------------------------------------------------")
    if ans == 'food':
        callback_button4 = InlineKeyboardButton(text="< 500", callback_data="дешево")
        callback_button5 = InlineKeyboardButton(text="> 500 но < 1000", callback_data="средне")
        callback_button6 = InlineKeyboardButton(text="> 1000", callback_data="дорого")
        callback_button_stop = InlineKeyboardButton(text="Выйти", callback_data="stop")
        message = 'Какой у вас бюджет?'
        keyboard = InlineKeyboardMarkup([[callback_button4, callback_button5, callback_button6, callback_button_stop]])
    elif ans == 'walk':
        callback_button4 = InlineKeyboardButton(text="Парк", callback_data="парк")
        callback_button5 = InlineKeyboardButton(text="Город", callback_data="город")
        callback_button_stop = InlineKeyboardButton(text="Выйти", callback_data="stop")
        # callback_button6 = InlineKeyboardButton(text="Ресторан", callback_data="rest")
        message = 'Где вы хотите погулять?'
        keyboard = InlineKeyboardMarkup([[callback_button4, callback_button5, callback_button_stop]])
    elif ans == 'activity':
        callback_button4 = InlineKeyboardButton(text="Спорт", callback_data="спорт")
        callback_button5 = InlineKeyboardButton(text="Релакс", callback_data="душа")
        # callback_button6 = InlineKeyboardButton(text="Ресторан", callback_data="rest")
        callback_button_stop = InlineKeyboardButton(text="Выйти", callback_data="stop")
        message = 'Чем хотите позаниматься?'
        keyboard = InlineKeyboardMarkup([[callback_button4, callback_button5, callback_button_stop]])
    elif ans == 'stop':
        await call.callback_query.message.reply_text("Конец резни")
        return ConversationHandler.END

    await context.bot.send_message(call.callback_query.message.chat.id, message, reply_markup=keyboard)
    return 2


async def quiz_ans2(call, context):
    print('ОБРАБОТЧИК ВЫЗВАН---------------------------------------------------------------')
    ans = call.callback_query.data
    KEYS.append([ans])
    # print(KEYS, "КЛЮЧИ 2 ОТВЕТ--------------------------------------------------")
    if len(check_keys(KEYS)) > 0:
        # message = ' '.join(check_keys(KEYS))
        for place in check_keys(KEYS):
            print(place)
            coordinates = get_coordinates(place, KEYS)
            cor1 = float(coordinates[0][0])
            cor2 = float(coordinates[0][1])
            await context.bot.send_location(call.callback_query.message.chat.id, cor1, cor2)
            await context.bot.send_message(call.callback_query.message.chat.id, place)
        return ConversationHandler.END
    elif ans in ('дешево', "средне", "дорого"):
        # KEYS['type'] = 'фастфуд'
        callback_button4 = InlineKeyboardButton(text="Фастфуд", callback_data="фастфуд")
        callback_button5 = InlineKeyboardButton(text="Выпечка", callback_data="выпечка")
        callback_button6 = InlineKeyboardButton(text="Ресторан", callback_data="ресторан")
        callback_button_stop = InlineKeyboardButton(text="Выйти", callback_data="stop")
        message = 'Какую еду вы хотите поесть?'
        keyboard = InlineKeyboardMarkup([[callback_button4, callback_button5, callback_button6, callback_button_stop]])
    elif ans == 'парк':
        # KEYS['type'] = 'парк'
        callback_button4 = InlineKeyboardButton(text="Лес", callback_data="лес")
        callback_button5 = InlineKeyboardButton(text="Река", callback_data="река")
        callback_button_stop = InlineKeyboardButton(text="Выйти", callback_data="stop")
        message = 'Какой природный район вам по душе?'
        keyboard = InlineKeyboardMarkup([[callback_button4, callback_button5, callback_button_stop]])
    # elif ans == 'город':
    #     #KEYS['type'] = 'город'
    elif ans == 'спорт':
        # KEYS['type'] = 'спорт'
        callback_button4 = InlineKeyboardButton(text="Волейбол", callback_data="волейбол")
        callback_button5 = InlineKeyboardButton(text="Футбол", callback_data="футбол")
        message = 'Каким типом спорта вы хотите заняться?'
        keyboard = InlineKeyboardMarkup([[callback_button4, callback_button5]])
    # elif ans == 'душа':
    #     #KEYS['type'] = 'душа'
    elif ans == 'stop':
        await call.callback_query.message.reply_text("Конец резни")
        return ConversationHandler.END

    await context.bot.send_message(call.callback_query.message.chat.id, message, reply_markup=keyboard)
    return 3


async def quiz_ans3(call, context):
    print('ОБРАБОТЧИК ВЫЗВАН---------------------------------------------------------------')
    ans = call.callback_query.data
    KEYS[1].append(ans)
    # print(KEYS, "КЛЮЧИ 3 ОТВЕТ--------------------------------------------------")
    # print(check_keys(KEYS), 'RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR')
    if len(check_keys(KEYS)) > 0:
        # message = ' '.join(check_keys(KEYS))
        for place in check_keys(KEYS):
            print(place)
            coordinates = get_coordinates(place, KEYS)
            cor1 = float(coordinates[0][0])
            cor2 = float(coordinates[0][1])
            await context.bot.send_location(call.callback_query.message.chat.id, cor1, cor2)
            await context.bot.send_message(call.callback_query.message.chat.id, place)
        return ConversationHandler.END

    elif ans == 'фастфуд':
        callback_button4 = InlineKeyboardButton(text="Пицца", callback_data="пицца")
        callback_button5 = InlineKeyboardButton(text="Бургер", callback_data="бургер")
        callback_button6 = InlineKeyboardButton(text="Шаурма", callback_data="шаурма")
        callback_button_stop = InlineKeyboardButton(text="Выйти", callback_data="stop")
        message = 'Какую гадость будешь кушать?'
        keyboard = InlineKeyboardMarkup([[callback_button4, callback_button5, callback_button6, callback_button_stop]])
    elif ans == 'выпечка':
        callback_button4 = InlineKeyboardButton(text="Кофейня", callback_data="кофе")
        callback_button5 = InlineKeyboardButton(text="Булочная", callback_data=",булочная")
        callback_button_stop = InlineKeyboardButton(text="Выйти", callback_data="stop")
        message = 'Какой тип заведения предпочитаете?'
        keyboard = InlineKeyboardMarkup([[callback_button4, callback_button5, callback_button_stop]])
    elif ans == 'stop':
        await call.callback_query.message.reply_text("Конец резни")
        return ConversationHandler.END
    await context.bot.send_message(call.callback_query.message.chat.id, message, reply_markup=keyboard)
    return 4


async def quiz_ans4(call, context):
    print('ОБРАБОТЧИК ВЫЗВАН---------------------------------------------------------------')
    ans = call.callback_query.data
    KEYS[1].append(ans)
    # print(KEYS, "КЛЮЧИ 4 ОТВЕТ--------------------------------------------------")
    if len(check_keys(KEYS)) > 0:
        # message = ' '.join(check_keys(KEYS))
        for place in check_keys(KEYS):
            print(place)
            coordinates = get_coordinates(place, KEYS)
            cor1 = float(coordinates[0][0])
            cor2 = float(coordinates[0][1])
            await context.bot.send_location(call.callback_query.message.chat.id, cor1, cor2)
            await context.bot.send_message(call.callback_query.message.chat.id, place)
        return ConversationHandler.END

    elif ans == 'stop':
        await call.callback_query.message.reply_text("Конец резни")
        return ConversationHandler.END


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
            2: [CallbackQueryHandler(quiz_ans2)],
            3: [CallbackQueryHandler(quiz_ans3)],
            4: [CallbackQueryHandler(quiz_ans4)]
        },
        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop)]
    )

    application.add_handler(conv_handler_quiz)

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("time", time_now))
    application.add_handler(CommandHandler("date", date_now))
    application.add_handler(MessageHandler(filters.PHOTO, photo_game))

    application.add_handler(CommandHandler("walk", walk_command))
    application.add_handler(CommandHandler("place", place_command))
    application.add_handler(CommandHandler("new_place", new_place_command))
    application.add_handler(CommandHandler("site", site_command))
    application.add_handler(CommandHandler("map", map_command))
    application.add_handler(CommandHandler('game', main_game))
    application.add_handler(CommandHandler('clear_data', clear_database))

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