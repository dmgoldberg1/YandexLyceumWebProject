from flask import Flask, render_template, url_for
import os
import sqlite3

app = Flask(__name__)

COLOURS = {'activity': '#D1E0FF',
           'food': '#FAECE5',
           'walk': '#EFFACE'}

@app.route('/')
def main_page():
    base = 'http://127.0.0.1:8080/'
    links = []
    db_path = os.path.abspath('main.py').split('\_'[0])[:-2] + ['bot', 'ex.db']
    con = sqlite3.connect('\_'[0].join(db_path))
    cur = con.cursor()

    links.append(('Где можно провести досуг:', COLOURS['activity']))
    result = cur.execute("""SELECT name FROM activity""").fetchall()
    for i in result:
        links.append(i[0])

    links.append(('Где можно поесть:',  COLOURS['food']))
    result = cur.execute("""SELECT name FROM food""").fetchall()
    for i in result:
        links.append(i[0])

    links.append(('Где можно прогуляться:', COLOURS['walk']))
    result = cur.execute("""SELECT name FROM walk""").fetchall()
    for i in result:
        links.append(i[0])

    con.close()

    return render_template('main_page.html',
                           logo=url_for('static', filename='Логотип.png'),
                           base=base,
                           links=links)


@app.route('/тест')
def test():
    return render_template('index.html',
                           title='ТЕСТОВАЯ СТРАНИЦА',
                           place='Имя места',
                           description='Описание места',
                           image=url_for('static', filename='test.png'))


@app.route('/<place>')
def sites(place):
    db_path = os.path.abspath('main.py').split('\_'[0])[:-2] + ['bot', 'ex.db']

    con = sqlite3.connect('\_'[0].join(db_path))
    cur = con.cursor()

    background = '#BAB1ED'

    result = cur.execute("""SELECT name, place, desc, pict FROM activity WHERE name = ?""", (place,)).fetchall()
    if result:
        background = COLOURS['activity']

    result += cur.execute("""SELECT name, place, desc, pict FROM food WHERE name = ?""", (place,)).fetchall()
    if result and background == '#BAB1ED':
        background = COLOURS['food']

    result += cur.execute("""SELECT name, place, desc, pict FROM walk WHERE name = ?""", (place,)).fetchall()
    if result and background == '#BAB1ED':
        background = COLOURS['walk']

    con.close()

    if result:
        photo = url_for('static', filename=result[0][3])
        return render_template('index.html',
                               title=result[0][0],
                               name=result[0][0],
                               place=result[0][1],
                               description=result[0][2],
                               background=background,
                               image='/'.join(photo.split('%5C')))

    else:
        print(url_for('static', filename='Нет картинки.png'))
        return render_template('non_existent.html')


@app.route('/О_нас')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(port=8080)
