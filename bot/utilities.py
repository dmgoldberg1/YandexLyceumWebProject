import sqlite3


def check_keys(keys):
    result = []
    db = sqlite3.connect('trobot.db')
    cursor = db.cursor()
    request = f'''SELECT * FROM {keys['table_name']}'''
    data = cursor.execute(request).fetchall()
    for obj in data:
        if set(keys['keys'] == set(obj[1])):
            result.append(obj[0])
    return result


