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


# Нет описания
# Нет фотографии
@app.route('/Волейбол')
def voleybol():
    with open('descriptions/Нет описания.txt', 'r', encoding='utf8') as fp:
        description = fp.readline()
    return render_template('index.html',
                           title='Волейбол',
                           place='Волейбол',
                           description=description,
                           image=url_for('static', filename='Нет картинки.png'))


# Нет описания
# Нет фотографии
@app.route('/Футбол')
def futbol():
    with open('descriptions/Нет описания.txt', 'r', encoding='utf8') as fp:
        description = fp.readline()
    return render_template('index.html',
                           title='Футбол',
                           place='Футбол',
                           description=description,
                           image=url_for('static', filename='Нет картинки.png'))


# Нет описания
# Нет фотографии
@app.route('/Лодочки')
def lodochki():
    with open('descriptions/Нет описания.txt', 'r', encoding='utf8') as fp:
        description = fp.readline()
    return render_template('index.html',
                           title='Лодочки',
                           place='Лодочки',
                           description=description,
                           image=url_for('static', filename='Нет картинки.png'))


# Нет описания
# Нет фотографии
@app.route('/МАУК_Троицкая_библиотека_№_1_имени_Михайловых')
def mauk_troitskaya_biblioteka_n_1_imeni_mikhaylovikh():
    with open('descriptions/Нет описания.txt', 'r', encoding='utf8') as fp:
        description = fp.readline()
    return render_template('index.html',
                           title='МАУК Троицкая библиотека № 1 имени Михайловых',
                           place='МАУК Троицкая библиотека № 1 имени Михайловых',
                           description=description,
                           image=url_for('static', filename='Нет картинки.png'))


# Нет описания
# Нет фотографии
@app.route('/Спортивно-оздоровительная_база_Лесная')
def sportivno_ozdorovitelnaya_baza_lesnaya():
    with open('descriptions/Нет описания.txt', 'r', encoding='utf8') as fp:
        description = fp.readline()
    return render_template('index.html',
                           title='Спортивно-оздоровительная база Лесная',
                           place='Спортивно-оздоровительная база Лесная',
                           description=description,
                           image=url_for('static', filename='Нет картинки.png'))


# Нет описания
# Нет фотографии
@app.route('/Троицкие_бани')
def troitskie_bani():
    with open('descriptions/Нет описания.txt', 'r', encoding='utf8') as fp:
        description = fp.readline()
    return render_template('index.html',
                           title='Троицкие бани',
                           place='Троицкие бани',
                           description=description,
                           image=url_for('static', filename='Нет картинки.png'))


# Нет описания
# Нет фотографии
@app.route('/Дом_книги')
def dom_knigi():
    with open('descriptions/Нет описания.txt', 'r', encoding='utf8') as fp:
        description = fp.readline()
    return render_template('index.html',
                           title='Дом книги',
                           place='Дом книги',
                           description=description,
                           image=url_for('static', filename='Нет картинки.png'))


# Нет описания
# Нет фотографии
@app.route('/Троицкая_библиотека_№_2')
def troitskaya_biblioteka_n_2():
    with open('descriptions/Нет описания.txt', 'r', encoding='utf8') as fp:
        description = fp.readline()
    return render_template('index.html',
                           title='Троицкая библиотека № 2',
                           place='Троицкая библиотека № 2',
                           description=description,
                           image=url_for('static', filename='Нет картинки.png'))


# Нет описания
# Нет фотографии
@app.route('/Театр-студия_17')
def teatr_studiya_17():
    with open('descriptions/Нет описания.txt', 'r', encoding='utf8') as fp:
        description = fp.readline()
    return render_template('index.html',
                           title='Театр-студия 17',
                           place='Театр-студия 17',
                           description=description,
                           image=url_for('static', filename='Нет картинки.png'))


# Нет описания
# Нет фотографии
@app.route('/додо_пицца')
def dodo_pitstsa():
    with open('descriptions/Нет описания.txt', 'r', encoding='utf8') as fp:
        description = fp.readline()
    return render_template('index.html',
                           title='додо пицца',
                           place='додо пицца',
                           description=description,
                           image=url_for('static', filename='Нет картинки.png'))


# Нет описания
# Нет фотографии
@app.route('/YourTime')
def yourtime():
    with open('descriptions/Нет описания.txt', 'r', encoding='utf8') as fp:
        description = fp.readline()
    return render_template('index.html',
                           title='YourTime',
                           place='YourTime',
                           description=description,
                           image=url_for('static', filename='Нет картинки.png'))


# Нет описания
# Нет фотографии
@app.route('/В_старом_городе')
def v_starom_gorode():
    with open('descriptions/Нет описания.txt', 'r', encoding='utf8') as fp:
        description = fp.readline()
    return render_template('index.html',
                           title='В старом городе',
                           place='В старом городе',
                           description=description,
                           image=url_for('static', filename='Нет картинки.png'))


# Нет описания
# Нет фотографии
@app.route('/Заречье')
def zareche():
    with open('descriptions/Нет описания.txt', 'r', encoding='utf8') as fp:
        description = fp.readline()
    return render_template('index.html',
                           title='Заречье',
                           place='Заречье',
                           description=description,
                           image=url_for('static', filename='Нет картинки.png'))


# Нет описания
# Нет фотографии
@app.route('/Академический_сквер')
def akademicheskiy_skver():
    with open('descriptions/Нет описания.txt', 'r', encoding='utf8') as fp:
        description = fp.readline()
    return render_template('index.html',
                           title='Академический сквер',
                           place='Академический сквер',
                           description=description,
                           image=url_for('static', filename='Нет картинки.png'))


# Нет описания
# Нет фотографии
@app.route('/Октябрьский_проспект')
def oktyabrskiy_prospekt():
    with open('descriptions/Нет описания.txt', 'r', encoding='utf8') as fp:
        description = fp.readline()
    return render_template('index.html',
                           title='Октябрьский проспект',
                           place='Октябрьский проспект',
                           description=description,
                           image=url_for('static', filename='Нет картинки.png'))


# Нет описания
# Нет фотографии
@app.route('/Усадьба_Троицкое')
def usadba_troitskoe():
    with open('descriptions/Нет описания.txt', 'r', encoding='utf8') as fp:
        description = fp.readline()
    return render_template('index.html',
                           title='Усадьба Троицкое',
                           place='Усадьба Троицкое',
                           description=description,
                           image=url_for('static', filename='Нет картинки.png'))


# Нет описания
# Нет фотографии
@app.route('/Троицкий_музей_имени_М._Н._Лялько')
def troitskiy_muzey_imeni_m_n_lyalko():
    with open('descriptions/Нет описания.txt', 'r', encoding='utf8') as fp:
        description = fp.readline()
    return render_template('index.html',
                           title='Троицкий музей имени М. Н. Лялько',
                           place='Троицкий музей имени М. Н. Лялько',
                           description=description,
                           image=url_for('static', filename='Нет картинки.png'))


# Нет описания
# Нет фотографии
@app.route('/Храм_Живоначальной_Троицы_в_Троицке')
def khram_jivonachalnoy_troitsi_v_troitske():
    with open('descriptions/Нет описания.txt', 'r', encoding='utf8') as fp:
        description = fp.readline()
    return render_template('index.html',
                           title='Храм Живоначальной Троицы в Троицке',
                           place='Храм Живоначальной Троицы в Троицке',
                           description=description,
                           image=url_for('static', filename='Нет картинки.png'))


# Нет описания
# Нет фотографии
@app.route('/d')
def d():
    with open('descriptions/Нет описания.txt', 'r', encoding='utf8') as fp:
        description = fp.readline()
    return render_template('index.html',
                           title='d',
                           place='d',
                           description=description,
                           image=url_for('static', filename='Нет картинки.png'))


# Нет описания
# Нет фотографии
@app.route('/Младший_научный_сотрудник')
def mladshiy_nauchniy_sotrudnik():
    with open('descriptions/Нет описания.txt', 'r', encoding='utf8') as fp:
        description = fp.readline()
    return render_template('index.html',
                           title='Младший научный сотрудник',
                           place='Младший научный сотрудник',
                           description=description,
                           image=url_for('static', filename='Нет картинки.png'))


# Нет описания
# Нет фотографии
@app.route('/Троицкий_Дом_ученых')
def troitskiy_dom_uchenikh():
    with open('descriptions/Нет описания.txt', 'r', encoding='utf8') as fp:
        description = fp.readline()
    return render_template('index.html',
                           title='Троицкий Дом ученых',
                           place='Троицкий Дом ученых',
                           description=description,
                           image=url_for('static', filename='Нет картинки.png'))


# Нет описания
# Нет фотографии
@app.route('/Вантовый_мост')
def vantoviy_most():
    with open('descriptions/Нет описания.txt', 'r', encoding='utf8') as fp:
        description = fp.readline()
    return render_template('index.html',
                           title='Вантовый мост',
                           place='Вантовый мост',
                           description=description,
                           image=url_for('static', filename='Нет картинки.png'))


# Нет описания
# Нет фотографии
@app.route('/Церковь_Тихвинской_иконы_Божией_Матери')
def tserkov_tikhvinskoy_ikoni_bojiey_materi():
    with open('descriptions/Нет описания.txt', 'r', encoding='utf8') as fp:
        description = fp.readline()
    return render_template('index.html',
                           title='Церковь Тихвинской иконы Божией Матери',
                           place='Церковь Тихвинской иконы Божией Матери',
                           description=description,
                           image=url_for('static', filename='Нет картинки.png'))


# Нет описания
# Нет фотографии
@app.route('/Огонь_памяти')
def ogon_pamyati():
    with open('descriptions/Нет описания.txt', 'r', encoding='utf8') as fp:
        description = fp.readline()
    return render_template('index.html',
                           title='Огонь памяти',
                           place='Огонь памяти',
                           description=description,
                           image=url_for('static', filename='Нет картинки.png'))


# Нет описания
# Нет фотографии
@app.route('/Культурно-технический_центр_Профкома_Тринити')
def kulturno_tekhnicheskiy_tsentr_profkoma_triniti():
    with open('descriptions/Нет описания.txt', 'r', encoding='utf8') as fp:
        description = fp.readline()
    return render_template('index.html',
                           title='Культурно-технический центр Профкома Тринити',
                           place='Культурно-технический центр Профкома Тринити',
                           description=description,
                           image=url_for('static', filename='Нет картинки.png'))


# Нет описания
# Нет фотографии
@app.route('/Физическая_кунсткамера')
def fizicheskaya_kunstkamera():
    with open('descriptions/Нет описания.txt', 'r', encoding='utf8') as fp:
        description = fp.readline()
    return render_template('index.html',
                           title='Физическая кунсткамера',
                           place='Физическая кунсткамера',
                           description=description,
                           image=url_for('static', filename='Нет картинки.png'))


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
