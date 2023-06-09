import sqlite3
import os


def russglish(word):
    eng_place = ''
    settings = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g',
                'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'j',
                'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k',
                'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
                'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
                'у': 'u', 'ы': 'i', 'ф': 'f', 'х': 'kh', 'ц': 'ts',
                'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ь': '', 'ъ': '',
                'э': 'e', 'ю': 'yu', 'я': 'ya', '№': 'n', '-': ' ', '.': '', ',': ''}

    for i in word:
        eng_place += settings.get(i.lower(), i.lower())

    return '_'.join(eng_place.split())


db_path = os.path.abspath('code_printer.py').split('\_'[0])[:-2] + ['bot', 'trobot.db']

con = sqlite3.connect('\_'[0].join(db_path))
cur = con.cursor()

result = cur.execute("""SELECT name FROM activity""").fetchall()
result += cur.execute("""SELECT name FROM food""").fetchall()
result += cur.execute("""SELECT name FROM walk""").fetchall()

for elem in result:
    place = elem[0]
    description = 'descriptions/' + place + '.txt'
    photo = place + '.png'

    if not os.path.exists(description):
        print('# Нет описания')
        description = 'descriptions/Нет описания.txt'
    if not os.path.exists(photo):
        print('# Нет фотографии')
        photo = 'Нет картинки.png'

    print(f"""@app.route('/{'_'.join(place.split())}')
def {russglish(place)}():
    with open('{description}', 'r', encoding='utf8') as fp:
        description = fp.readline()
    return render_template('index.html',
                           title='{place}',
                           place='{place}',
                           description=description,
                           image=url_for('static', filename='{photo}'))""")
    print()
    print()

con.close()
