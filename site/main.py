from flask import Flask, render_template, url_for

app = Flask(__name__)


@app.route('/')
def main_page():
    return render_template('main_page.html')


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
             'Белорусская лавка', 'Ресторан В Старом Городе','Перекрёсток', 
             'Rusalut', 'Книжный интернет-магазин', 'Барбершоп BORODACH']
    
    return render_template('index.html',
                           title='ТЦ Троицк',
                           place='ТЦ Троицк',
                           description='Самый большой торговый центр в Троицке. Список его заведений:',
                           in_place=shops,
                           image=url_for('static', filename='ТЦ Троицк.png'))


@app.route('/Заречье')
def zarechye():
    return render_template('index.html',
                           title='Заречье',
                           place='Заречье',
                           description='Самый большой парк Троицка. На территории можно арендовать беседки и'
                                       ' покушать в одноимённом ресторане.',
                           image=url_for('static', filename='Заречье.png'))


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
