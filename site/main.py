from flask import Flask, render_template, url_for

app = Flask(__name__)


@app.route('/')
def main_page():
    base = 'http://127.0.0.1:8080/'
    links = ['ТЦ_Троицк', 'Заречье', 'Квант',
             'Рынок', 'Баня', 'Вкусно_И_Точка',
             'Додо_Пицца', 'Изумрудный_Город']
    return render_template('main_page.html',
                           base=base,
                           links=links)


@app.route('/тест')
def test():
    return render_template('index.html',
                           title='ТЕСТОВАЯ СТРАНИЦА',
                           place='Имя места',
                           description='Описание места',
                           image=url_for('static', filename='test.png'))


@app.route('/ТЦ_Троицк')
def tc_troitsk():
    shops = ['Автомойка', 'Pizza House', 'Mama SHU',
             'Белорусская лавка', 'Ресторан В Старом Городе', 'Перекрёсток',
             'Rusalut', 'Книжный Лабиринт', 'BORODACH',
             'До Рассвета', 'М1', 'Кондитерская',
             'Батарейки', 'Шведская чистка', 'Эрика',
             'FUN&SUN', 'Экспедиция', 'Картинная галерея',
             'Садива', 'Chimp Champ', 'Maxx',
             'ProfLine', 'Yagona', 'Смарт Скул',
             'Школа самбо и дзюдо', 'Электроник', 'Ермолино',
             'Титан', 'Ozon', 'Вояж',
             'Free Move Family', 'АльфаСтрахование',
             'Мои небеса', 'Мирабела', 'Академия развития Бамбино',
             'Iva Beauty Lab', 'Торты', 'Msk-stone',
             'АвтоАкадемия', 'Техномания', 'Boxberry']

    return render_template('index.html',
                           title='ТЦ Троицк',
                           place='Торговый Центр Троицк',
                           description='Самый большой торговый центр в Троицке. Список его заведений:',
                           in_place=shops,
                           image=url_for('static', filename='ТЦ Троицк.png'))


@app.route('/Заречье')
def zarechye():
    return render_template('index.html',
                           title='Заречье',
                           place='Парк Заречье',
                           description='Самый большой парк Троицка. На территории можно арендовать беседку или'
                                       ' покушать в одноимённом ресторане.',
                           image=url_for('static', filename='Заречье.png'))


@app.route('/Квант')
def kvant():
    shops = ['Чемпион', 'Дэма', 'ТШСВиЕ Белый Тигр']

    return render_template('index.html',
                           title='Квант',
                           place='Дворец спорта Квант',
                           description='Центр спорта Троицка. Предлагает большое разнообразие секций.',
                           in_place=shops,
                           image=url_for('static', filename='Квант.png'))


@app.route('/Рынок')
def rinok():
    shops = ['Металлоремонт', 'Продукты Ермолино', 'Обувь',
             'Ozon', 'DPD', 'Boxberry'
             'Яндекс Маркет', 'IML']

    return render_template('index.html',
                           title='Рынок',
                           place='Центральный Рынок',
                           description='Главный рынок Троицка.',
                           in_place=shops,
                           image=url_for('static', filename='Рынок.png'))


@app.route('/Баня')
def banya():
    shops = ['Т-Клуб', 'Отопление-Троицк', 'Чемпионика',
             'Araz RichMan', 'Буханка', 'МУП Троицкие городские бани',
             'Троицкие сауны', 'Грифон', 'Небеса',
             'Заречье', 'Арарата денс']

    return render_template('index.html',
                           title='Баня',
                           place='Троицкие бани',
                           description='Небезызвестные бани Троицка.',
                           in_place=shops,
                           image=url_for('static', filename='Баня.png'))


@app.route('/Вкусно_И_Точка')
def macdonalds():
    return render_template('index.html',
                           title='Вкусно И Точка',
                           place='Вкусно И Точка',
                           description='Бывший Макдональдс. Самый забитый ресторан быстрого питания в Троицке.',
                           image=url_for('static', filename='Макдональдс.png'))


@app.route('/Додо_Пицца')
def dodo():
    return render_template('index.html',
                           title='Додо',
                           place='Додо Пицца',
                           description='Самая лучшая пиццерия в городе. За приличную цену приличная еда.',
                           image=url_for('static', filename='Додо Пицца.png'))


@app.route('/Изумрудный_Город')
def izumrudniy_gorod():
    shops = ['Изумрудный город', 'С-Логика', 'Fix Price',
             'FoodBand.ru', 'ГлавБухъ', 'Пятёрочка',
             'Женская одежда', 'Пивмаг', 'DesignStudio22',
             'Трикотаж', 'Косметология']

    return render_template('index.html',
                           title='Изумрудный Город',
                           place='Изумрудный Город',
                           description='Пользуется популярностью среди местных школьников.',
                           in_place=shops,
                           image=url_for('static', filename='Изумрудный Город.png'))


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
