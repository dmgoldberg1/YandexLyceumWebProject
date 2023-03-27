from flask import Flask, render_template, url_for

app = Flask(__name__)


@app.route('/')
def main_page():
    return render_template('main_page.html')


@app.route('/test')
def index():
    user = "Ученик Яндекс.Лицея"
    return render_template('index.html', title='ТЕСТОВАЯ СТРАНИЦА',
                           place='Имя места', description='Описание места',
                           image=url_for('static', filename='test.png'))


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')