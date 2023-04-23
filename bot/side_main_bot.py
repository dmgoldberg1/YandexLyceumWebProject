# Импортируем необходимые классы.
import datetime
import logging
import os
import sqlite3
import time
from io import StringIO

import aiohttp
import requests
import torch
import torch.nn as nn
import torchvision.transforms as transforms
import timm
from PIL import Image
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, MessageHandler, filters
from telegram.ext import CommandHandler, CallbackQueryHandler, ConversationHandler

BOT_TOKEN = '6288452612:AAEkJQqqid5enfM7iUOWHtV7jCaxXWCFgnk'
KEYS = list()
ANS_COUNT = 0
DB = 'ex.db'
dialog_const0, dialog_const1, dialog_const2, dialog_const3, dialog_const4 = True, True, True, True, True

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
    1: (1, 55.468117, 37.296497, 'фонтана', 37.295382, 37.298140, 55.467836, 55.469765),
    2: (2, 55.475614, 37.299292, 'волейбольной площадки', 37.297233, 37.300808, 55.474638, 55.476154),
    3: (1, 55.484520, 37.304923, 'фонтана', 37.304213, 37.308175, 55.484423, 55.486265),
    4: (0, 55.495157, 37.305522, 'уточки', 37.301554, 37.308184, 55.492380, 55.496271)
}
LOC = True
PHOTO = True

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
    global DB
    result = []
    db = sqlite3.connect(DB)
    cursor = db.cursor()
    request = f'''SELECT * FROM {keys[0]}'''
    data = cursor.execute(request).fetchall()
    keys_tokens = set(keys[1])
    print(keys, 'cccc', data)
    print('НАШИ КЛЮЧИ--------------------------------------------------------------------------------')
    for obj in data:
        obj_tokens = set(obj[-1].split())
        print(keys_tokens, '   ', obj_tokens)
        if keys_tokens.issubset(obj_tokens):
            result.append(obj)
    print(result)
    db.close()
    return result


def get_coordinates(place, keys):
    coordinates = []
    print(place, 'ВНУТРИ ФУНКЦИИ')
    db = sqlite3.connect('ex.db')
    cursor = db.cursor()
    request = f'''SELECT coords FROM {keys[0]} WHERE name = ?'''
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
           "/find_place - найти нужное место в Троицке\n" \
           "/game - поучаствовать в игре по фотоориентированию\n" \
           "/start_game_again - начать игру заново\n" \
        # "/walk - пойти гулять\n" \
    # "/place - поиск мест\n" \
    # "/new_place - добавить новое место\n" \
    # "/site - сайт со всеми местами\n" \
    # "/map - карта Троицка\n" \
    # "/geocoder - тест картинок"
    await update.message.reply_text(text, reply_markup=markup)


async def echo(update, context):
    await update.message.reply_text(f'Я получил сообщение "{update.message.text}"', reply_markup=markup)


async def time_now(update, context):
    await update.message.reply_text(f'Время - {datetime.datetime.now().time().strftime("%H:%M")}', reply_markup=markup)


async def date_now(update, context):
    await update.message.reply_text(f'Дата - {datetime.datetime.now().date().strftime("%d %B %Y")}',
                                    reply_markup=markup)


async def photo_game(update, context):
    global LOC
    global PHOTO
    print("Получил фото------------------------")
    # print(update)
    db = sqlite3.connect('game.db')
    cursor = db.cursor()
    user_id = update.message.chat.id
    print(update.message.location, 'LOCATION----------------------')
    level = cursor.execute("SELECT level FROM main_game WHERE user_id = ?", (user_id,)).fetchone()[0]
    if update.message.location:
        await context.bot.send_message(update.message.chat.id, "Получил координаты")
        coor1, coor2 = update.message.location.latitude, update.message.location.longitude
        LOC = True
    elif update.message.photo[0]:
        r = requests.get((await context.bot.getFile(update.message.photo[0].file_id)).file_path)
        await context.bot.send_message(update.message.chat.id, "Получил фото")
        PHOTO = True
        if r.status_code == 200:
            with open("image.jpg", 'wb') as f:
                f.write(r.content)
        print('DOWNLOADED')
    print(LOC, PHOTO)
    if LOC and PHOTO:
        print('ANOOOOOGUS')
        # if predict_image('image.jpg', level) and LEVELS[level][6] < coor1 < LEVELS[level][7] and LEVELS[level][4] < coor2 < LEVELS[level][5]:
        if predict_image('image.jpg', level):
            print('УРОВЕНЬ ПРОЙДЕН')
            cursor.execute('UPDATE main_game SET level = ? WHERE user_id = ?', (level + 1, user_id,))
            db.commit()
            os.remove('image.jpg')
            message = 'Молодец! Ты справился с уровнем! Если хочешь сейчас же начать новый, то нажми на кнопку. Ты в любой момент можешь вернуться к прохождению, написав команду /game'
            LOC, PHOTO = True, True
            callback_button = InlineKeyboardButton(text="Следующий уровень", callback_data="amogus")
            keyboard = InlineKeyboardMarkup([[callback_button]])

            await context.bot.send_message(update.message.chat.id, message, reply_markup=keyboard)
            return 1
        else:
            print('УРОВЕНЬ ПРОВАЛЕН')
            message = 'Ты отправил неправилное фото или ты не дошел то точки. Отправь фото и локацию еше раз'
            LOC, PHOTO = None, None
            await context.bot.send_message(update.message.chat.id, message)


# GGGAAAMMMEEE
# check ans for game
async def game_ans(call, context):
    print('GAME ANS ВЫЗВАН---------------------------------------------------------------')
    ans = call.callback_query.data
    user_id = call.callback_query.from_user.id
    print(user_id)
    if ans == 'amogus':
        db = sqlite3.connect('game.db')
        cursor = db.cursor()
        info = cursor.execute("SELECT level FROM main_game WHERE user_id = ?", (user_id,)).fetchone()[0]
        message1 = f'''С возвращением!\nТвой текущий уровень - {info}'''
        message2 = f'''Тебе нужно пройти к точке и отправить мне фото {LEVELS[info][3]} и свою геопозицию'''
        await context.bot.send_message(call.callback_query.message.chat.id, message1)
        await context.bot.send_message(call.callback_query.message.chat.id, message2)
        await context.bot.send_location(call.callback_query.message.chat.id, LEVELS[info][1], LEVELS[info][2])
        return ConversationHandler.END


# main func for game
async def main_game(update, context):
    print('I AM HERE IN MAIN GAME----------------------------')
    db = sqlite3.connect('game.db')
    cursor = db.cursor()
    user_id = update.message.chat.id
    nickname = update.message.chat.first_name + ' ' + update.message.chat.last_name

    # print(update)
    res = cursor.execute("SELECT user_id FROM main_game").fetchall()
    ids = [i[0] for i in res]
    if user_id not in ids:
        print('НОВЫЙ ПОЛЬЗОВАТЕЛЬ------------------------')
        cursor.execute("INSERT INTO main_game (user_id, nickname, level) VALUES (?, ?, ?)", (user_id, nickname, 1,))
        db.commit()
        message1 = 'Привет! Ты попал в программу "Сдохни или умри". В этой игре есть несколько уровней. Задача каждого ' \
                   'уровня - отправить фотографию предлагаемого объекта в Троицке и твою геопозицию. Тебе будет дана точка на карте, ' \
                   'до которой тебе нужно добраться. За каждое выполненное задание ты будешь получать очки! Удачи! '
        message2 = 'Задание 1\nПройди на точку и отправь фото фонтана.'

        await context.bot.send_message(update.message.chat.id, message1)
        await context.bot.send_message(update.message.chat.id, message2)
        await context.bot.send_location(update.message.chat.id, LEVELS[1][1], LEVELS[1][2])
    else:
        info = cursor.execute("SELECT level FROM main_game WHERE user_id = ?", (user_id,)).fetchone()[0]
        message1 = f'''С возвращением!\nТвой текущий уровень - {info}'''
        message2 = f'''Тебе нужно пройти к точке и отправить мне фото {LEVELS[info][3]} и свою геопозицию'''
        await context.bot.send_message(update.message.chat.id, message1)
        await context.bot.send_message(update.message.chat.id, message2)
        await context.bot.send_location(update.message.chat.id, LEVELS[info][1], LEVELS[info][2])


# clear db for game
async def clear_database(update, context):
    db = sqlite3.connect('game.db')
    cursor = db.cursor()
    cursor.execute('DELETE FROM main_game')
    db.commit()


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


async def chekan(update, context):
    foto = random.randint(0, 5)
    await update.get_bot().send_photo(update.message.from_user.id, open(f'files/chekan{foto}.png', 'rb'))


async def chekan_voice(update, context):
    video = random.randint(0, 0)
    await update.get_bot().send_video(update.message.from_user.id, open(f'files/chekan_voice{video}.mp4', 'rb'))


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


async def callback_inline(call, context):
    # Если сообщение из чата с ботом
    print(call, ' CALLLL')
    print(call.callback_query.data, 'AMOGUS')
    print('------------------------------------------------------------')
    # if call.message:
    #     if call.data == "test":
    #         context.bot.send_message(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Пыщь")
    # # Если сообщение из инлайн-режима
    # elif call.inline_query:
    #     if call.data == "test":
    await context.bot.send_message(call.callback_query.from_user.id, 'ура')


# quiz - пройти квест
async def quiz_command(update, context):
    global dialog_const0, dialog_const1, dialog_const2, dialog_const3, dialog_const4
    if not dialog_const0:
        await call.callback_query.message.reply_text("Закончите разговор")
        return
    dialog_const0 = False
    callback_button1 = InlineKeyboardButton(text="Хочу наполнить желудок", callback_data="food")
    callback_button2 = InlineKeyboardButton(text="Хочу расслабиться и погулять", callback_data="walk")
    callback_button3 = InlineKeyboardButton(text="Хочу активности", callback_data="activity")
    callback_button_stop = InlineKeyboardButton(text="Выйти", callback_data="stop")

    keyboard = InlineKeyboardMarkup(
        [[callback_button1], [callback_button2], [callback_button3], [callback_button_stop]])
    await context.bot.send_message(update.message.chat.id, "Чем вы хотите заняться?!!!", reply_markup=keyboard)
    return 1


async def quiz_ans1(call, context):
    print('ОБРАБОТЧИК ВЫЗВАН  quiz_ans1---------------------------------------------------------------')
    global KEYS, dialog_const1, dialog_const2, dialog_const3, dialog_const4
    print(dialog_const1, '-----------')
    if not dialog_const1:
        await call.callback_query.message.reply_text("Закончите разговор")
        return
    dialog_const1 = False
    KEYS.clear()
    # Получаем название кнопки - таблицы бд
    ans = call.callback_query.data
    KEYS.append(ans)
    print(KEYS, "КЛЮЧИ 1 ОТВЕТ--------------------------------------------------")

    context.bot.delete_message(call.callback_query.message.chat.id, call.callback_query.message.message_id)

    # обработка ответа - "Хочу наполнить желудок"
    if ans == 'food':
        callback_button4 = InlineKeyboardButton(text="< 500", callback_data="дешево")
        callback_button5 = InlineKeyboardButton(text="> 500 но < 1000", callback_data="средне")
        callback_button6 = InlineKeyboardButton(text="> 1000", callback_data="дорого")
        callback_button_stop = InlineKeyboardButton(text="Выйти", callback_data="stop")
        message = 'Какой у вас бюджет?'
        keyboard = InlineKeyboardMarkup(
            [[callback_button4], [callback_button5], [callback_button6], [callback_button_stop]])
        await context.bot.send_message(call.callback_query.message.chat.id, message, reply_markup=keyboard)
        return 2

    # обработка ответа - "Хочу расслабиться и погулять"
    elif ans == 'walk':
        callback_button4 = InlineKeyboardButton(text="Погулять по парку", callback_data="парк")
        callback_button5 = InlineKeyboardButton(text="Посмотреть достопримечательности",
                                                callback_data="достопримечательность")
        callback_button_stop = InlineKeyboardButton(text="Выйти", callback_data="stop")
        message = 'Где вы хотите погулять?'
        keyboard = InlineKeyboardMarkup([[callback_button4], [callback_button5], [callback_button_stop]])
        await context.bot.send_message(call.callback_query.message.chat.id, message, reply_markup=keyboard)
        return 3


    # обработка ответа - "Хочу активности"
    elif ans == 'activity':
        callback_button4 = InlineKeyboardButton(text="Заняться спортом", callback_data="спорт")
        callback_button5 = InlineKeyboardButton(text="Посмотреть музей", callback_data="музей")
        callback_button6 = InlineKeyboardButton(text="Посетить театр", callback_data="театр")
        callback_button7 = InlineKeyboardButton(text="Попасть в СЕРДЦЕ Троицка", callback_data="центр")
        callback_button_stop = InlineKeyboardButton(text="Выйти", callback_data="stop")
        message = 'Чем хотите позаниматься?'
        keyboard = InlineKeyboardMarkup(
            [[callback_button4], [callback_button5], [callback_button6], [callback_button7], [callback_button_stop]])
        await context.bot.send_message(call.callback_query.message.chat.id, message, reply_markup=keyboard)
        return 4

    # обработка выхода из 1 вопроса
    elif ans == 'stop':
        dialog_const0, dialog_const1, dialog_const2, dialog_const3, dialog_const4 = True, True, True, True, True
        await call.callback_query.message.reply_text("Конец резни")
        return ConversationHandler.END

    message = 'Произошла ошибка'
    await context.bot.send_message(call.callback_query.message.chat.id, message)
    dialog_const0, dialog_const1, dialog_const2, dialog_const3, dialog_const4 = True, True, True, True, True
    return ConversationHandler.END


async def quiz_ans_food(call, context):
    global KEYS, dialog_const0, dialog_const1, dialog_const2, dialog_const3, dialog_const4
    print(dialog_const2, '---------')
    if not dialog_const2 or len(KEYS) >= 2:
        await call.callback_query.message.reply_text("Закончите разговор")
        return
    dialog_const2 = False
    print('ОБРАБОТЧИК ВЫЗВАН  quiz_ans_food---------------------------------------------------------------')
    ans = call.callback_query.data
    KEYS.append([ans])
    print(KEYS)
    context.bot.delete_message(call.callback_query.message.chat.id, call.callback_query.message.message_id)
    if ans == 'stop':
        await call.callback_query.message.reply_text("Конец резни")
        dialog_const0, dialog_const1, dialog_const2, dialog_const3, dialog_const4 = True, True, True, True, True
        return ConversationHandler.END

    callback_button4 = InlineKeyboardButton(text="Фастфуд", callback_data="фастфуд")
    callback_button5 = InlineKeyboardButton(text="Кафе", callback_data="кафе")
    callback_button6 = InlineKeyboardButton(text="Ресторан", callback_data="ресторан")
    callback_button_stop = InlineKeyboardButton(text="Выйти", callback_data="stop")
    message = 'Какую еду вы хотите поесть?'
    keyboard = InlineKeyboardMarkup(
        [[callback_button4], [callback_button5], [callback_button6], [callback_button_stop]])

    await context.bot.send_message(call.callback_query.message.chat.id, message, reply_markup=keyboard)
    return 5


async def quiz_ans_walk(call, context):
    global KEYS, dialog_const0, dialog_const1, dialog_const2, dialog_const3, dialog_const4
    print(dialog_const2, '---------')
    if not dialog_const2 or len(KEYS) >= 2:
        await call.callback_query.message.reply_text("Закончите разговор")
        return
    dialog_const2 = False

    print('ОБРАБОТЧИК ВЫЗВАН quiz_ans_walk---------------------------------------------------------------')
    ans = call.callback_query.data
    KEYS.append([ans])
    context.bot.delete_message(call.callback_query.message.chat.id, call.callback_query.message.message_id)
    if ans == 'stop':
        await call.callback_query.message.reply_text("Конец резни")
        dialog_const0, dialog_const1, dialog_const2, dialog_const3, dialog_const4 = True, True, True, True, True
        return ConversationHandler.END
    elif ans == 'достопримечательность':
        db_results, buttons = check_keys(KEYS), []
        for place in db_results:
            callback_button = InlineKeyboardButton(text=place[1], callback_data=place[1][:10])
            buttons.append([callback_button])
        message = 'Выберете место для посещения'
        callback_button_stop = InlineKeyboardButton(text="Выйти", callback_data="stop")
        keyboard = InlineKeyboardMarkup([*buttons, [callback_button_stop]])

        await context.bot.send_message(call.callback_query.message.chat.id, message, reply_markup=keyboard)
        return 6

    callback_button4 = InlineKeyboardButton(text="Детские площадки и другие развлечения", callback_data="развлечения")
    callback_button5 = InlineKeyboardButton(text="Река", callback_data="река")
    callback_button6 = InlineKeyboardButton(text="Лес", callback_data="лес")
    callback_button_stop = InlineKeyboardButton(text="Выйти", callback_data="stop")
    message = 'Что вы хотите, чтобы было в парке?'
    keyboard = InlineKeyboardMarkup(
        [[callback_button4], [callback_button5], [callback_button6], [callback_button_stop]])

    print(dialog_const2)
    await context.bot.send_message(call.callback_query.message.chat.id, message, reply_markup=keyboard)
    return 5


async def quiz_ans_activity(call, context):
    global KEYS, dialog_const0, dialog_const1, dialog_const2, dialog_const3, dialog_const4
    print(dialog_const2, '---------')
    if not dialog_const2 or len(KEYS) >= 2:
        await call.callback_query.message.reply_text("Закончите разговор")
        return
    dialog_const2 = False
    print('ОБРАБОТЧИК ВЫЗВАН---------------------------------------------------------------')
    ans = call.callback_query.data
    KEYS.append([ans])
    context.bot.delete_message(call.callback_query.message.chat.id, call.callback_query.message.message_id)
    if ans == 'stop':
        dialog_const0, dialog_const1, dialog_const2, dialog_const3, dialog_const4 = True, True, True, True, True
        await call.callback_query.message.reply_text("Конец резни")
        return ConversationHandler.END
    print('ОБРАБОТЧИК ВЫЗВАН---------------------------------------------------------------')
    ans = call.callback_query.data
    KEYS.append([ans])
    print(KEYS)

    if ans == 'музей' or ans == 'театр' or ans == 'центр':
        db_results, buttons = check_keys(KEYS), []
        for place in db_results:
            callback_button = InlineKeyboardButton(text=place[1], callback_data=place[1][:10])
            buttons.append([callback_button])
        print(buttons)
        message = 'Выберете место для посещения'
        callback_button_stop = InlineKeyboardButton(text="Выйти", callback_data="stop")
        keyboard = InlineKeyboardMarkup([*buttons, [callback_button_stop]])

        await context.bot.send_message(call.callback_query.message.chat.id, message, reply_markup=keyboard)
        return 6

    callback_button4 = InlineKeyboardButton(text="Воркаут", callback_data="воркаут")
    callback_button5 = InlineKeyboardButton(text="Футбол", callback_data="футбол")
    callback_button6 = InlineKeyboardButton(text="Волейбол", callback_data="волейбол")
    callback_button7 = InlineKeyboardButton(text="Хоккей", callback_data="хоккей")
    callback_button8 = InlineKeyboardButton(text="Лыжи", callback_data="лыжи")
    callback_button9 = InlineKeyboardButton(text="Развлечения и детские площадки", callback_data="развлечения")
    callback_button_stop = InlineKeyboardButton(text="Выйти", callback_data="stop")
    message = 'Что вы хотите, чтобы было в парке?'
    keyboard = InlineKeyboardMarkup(
        [[callback_button4], [callback_button5], [callback_button6], [callback_button7], [callback_button8],
         [callback_button9], [callback_button_stop]])

    await context.bot.send_message(call.callback_query.message.chat.id, message, reply_markup=keyboard)
    return 5


async def quiz_ans_final(call, context):
    global KEYS, dialog_const0, dialog_const1, dialog_const2, dialog_const3, dialog_const4
    if not dialog_const3:
        await call.callback_query.message.reply_text("Закончите разговор")
        return
    dialog_const3 = False
    print('ОБРАБОТЧИК ВЫЗВАН---------------------------------------------------------------')
    ans = call.callback_query.data
    KEYS[1].append(ans)
    print(KEYS)

    if ans == 'stop':
        dialog_const0, dialog_const1, dialog_const2, dialog_const3, dialog_const4 = True, True, True, True, True
        await call.callback_query.message.reply_text("Конец резни")
        return ConversationHandler.END

    db_results, buttons = check_keys(KEYS), []
    for place in db_results:
        callback_button = InlineKeyboardButton(text=place[1], callback_data=place[1][:10])
        buttons.append([callback_button])
    print(buttons)
    message = 'Выберете место для посещения'
    callback_button_stop = InlineKeyboardButton(text="Выйти", callback_data="stop")
    # print(len([*buttons1, [callback_button_stop]]))
    keyboard = InlineKeyboardMarkup([*buttons, [callback_button_stop]])
    await context.bot.send_message(call.callback_query.message.chat.id, message, reply_markup=keyboard)
    return 6


async def quiz_ans_final_end(call, context):
    global KEYS, dialog_const0, dialog_const1, dialog_const2, dialog_const3, dialog_const4
    # if not dialog_const4:
    #     await call.callback_query.message.reply_text("Закончите разговор")
    #     return
    # dialog_const4 = False
    print('ОБРАБОТЧИК ВЫЗВАН---------------------------------------------------------------')
    ans = call.callback_query.data
    print(KEYS)

    if ans == 'stop':
        dialog_const0, dialog_const1, dialog_const2, dialog_const3, dialog_const4 = True, True, True, True, True
        await call.callback_query.message.reply_text("Конец резни")
        return ConversationHandler.END

    db_results, button = check_keys(KEYS), []
    for cafe in db_results:
        if ans in cafe[1]:
            button = cafe
    print('Place = ', button)
    place = button[1]
    coordinates = get_coordinates(place, KEYS)
    cor1 = float(coordinates[0][0])
    cor2 = float(coordinates[0][1])
    message = f'Нажми на кнопку и перейди на сайт с информацией про это место'
    callback_button = InlineKeyboardButton(text="Сайт места",
                                           url=f"http://192.168.68.125:8080/{place.capitalize()}")
    keyboard = InlineKeyboardMarkup([[callback_button]])
    await context.bot.send_message(call.callback_query.message.chat.id, place)
    await context.bot.send_location(call.callback_query.message.chat.id, cor1, cor2)
    await context.bot.send_message(call.callback_query.message.chat.id, message, reply_markup=keyboard)
    dialog_const0, dialog_const1, dialog_const2, dialog_const3, dialog_const4 = True, True, True, True, True
    return ConversationHandler.END


async def stop_dialog(update, context):
    await update.message.reply_text("Конец резни")
    global KEYS, dialog_const0, dialog_const1, dialog_const2, dialog_const3, dialog_const4
    dialog_const0, dialog_const1, dialog_const2, dialog_const3, dialog_const4 = True, True, True, True, True
    return ConversationHandler.END


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    text_handler = MessageHandler(filters.TEXT, echo)
    # application.add_handler(text_handler)
    conv_handler_quiz = ConversationHandler(
        # Точка входа в диалог.
        entry_points=[CommandHandler('find_place', quiz_command)],
        # Состояние внутри диалога.
        states={
            # Функция читает ответ на первый вопрос и задаёт второй.
            1: [CallbackQueryHandler(quiz_ans1)],
            2: [CallbackQueryHandler(quiz_ans_food)],
            3: [CallbackQueryHandler(quiz_ans_walk)],
            4: [CallbackQueryHandler(quiz_ans_activity)],
            5: [CallbackQueryHandler(quiz_ans_final)],
            6: [CallbackQueryHandler(quiz_ans_final_end)],
            # 7: [CallbackQueryHandler(quiz_ans_walk_seeings)]
        },
        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop_dialog)]
    )
    conv_handler_game = ConversationHandler(
        # Точка входа в диалог.
        entry_points=[MessageHandler(filters.LOCATION | filters.PHOTO, photo_game)],
        # Состояние внутри диалога.
        states={
            1: [CallbackQueryHandler(game_ans)],
        },
        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop_dialog)]
    )

    application.add_handler(conv_handler_quiz)
    application.add_handler(conv_handler_game)

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("time", time_now))
    application.add_handler(CommandHandler("date", date_now))

    application.add_handler(MessageHandler(filters.LOCATION | filters.PHOTO, photo_game))
    application.add_handler(CommandHandler("walk", walk_command))
    application.add_handler(CommandHandler("place", place_command))
    application.add_handler(CommandHandler("new_place", new_place_command))
    application.add_handler(CommandHandler("site", site_command))
    application.add_handler(CommandHandler("map", map_command))

    application.add_handler(CommandHandler('game', main_game))
    application.add_handler(CommandHandler('start_game_again', clear_database))

    application.add_handler(CommandHandler("set", set_timer))
    application.add_handler(CommandHandler("unset", unset))
    application.add_handler(CommandHandler("geocoder", geocoder))

    # application.add_handler(CallbackQueryHandler(callback_inline))

    application.run_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
