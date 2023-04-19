from flask import Flask, render_template, url_for
import os
import sqlite3

app = Flask(__name__)


@app.route('/')
def main_page():
    base = 'http://127.0.0.1:8080/'
    links = []

    db_path = os.path.abspath('code_printer.py').split('\_'[0])[:-2] + ['bot', 'trobot.db']

    con = sqlite3.connect('\_'[0].join(db_path))
    cur = con.cursor()

    result = cur.execute("""SELECT name FROM activity""").fetchall()
    result += cur.execute("""SELECT name FROM food""").fetchall()
    result += cur.execute("""SELECT name FROM walk""").fetchall()

    con.close()

    for i in result:
        links.append(i[0])

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


@app.route('/<place>')
def sites(place):
    db_path = os.path.abspath('code_printer.py').split('\_'[0])[:-2] + ['bot', 'ex.db']

    con = sqlite3.connect('\_'[0].join(db_path))
    cur = con.cursor()

    result = cur.execute("""SELECT name FROM activity WHERE name = ?""", (place,)).fetchall()
    result += cur.execute("""SELECT name FROM food WHERE name = ?""", (place,)).fetchall()
    result += cur.execute("""SELECT name FROM walk WHERE name = ?""", (place,)).fetchall()
    print(result)

    con.close()

    if result:
        description = 'descriptions/' + place + '.txt'
        photo = place + '.png'

        if not os.path.exists(description):
            print('# Нет описания')
            description = 'descriptions/Нет описания.txt'
        if not os.path.exists(photo):
            print('# Нет фотографии')
            photo = 'Нет картинки.png'

        return render_template('index.html',
                               title=result[0][0],
                               place=result[0][0],
                               description='Описание места',
                               image=url_for('static', filename='test.png'))

    else:
        return render_template('non_existent.html')


@app.route('/О_нас')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(port=8080, host='192.168.68.125')