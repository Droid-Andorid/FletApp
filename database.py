import sqlite3
from flet import dropdown
from datetime import datetime

db = sqlite3.connect("dshooks.db", check_same_thread=False)
cour = db.cursor()


def initialize_db():
    cour.execute("""CREATE TABLE IF NOT EXISTS webhook(
        name TEXT PRIMARY KEY, 
        url URL,
        date DATE)""")
    cour.execute("""CREATE TABLE IF NOT EXISTS bot_api(
        name TEXT PRIMARY KEY,
        api LARGE TEXT,
        date DATE)""")
    db.commit()


def save_hook_url(name, url):
    names = cour.execute("SELECT name FROM webhook").fetchall()
    if name not in names:
        cour.execute("INSERT INTO webhook (name, url, date) VALUES (?, ?, ?)", (name, url, str(datetime.now()).replace(":", "-")))
        db.commit()
    else:
        raise ValueError


def save_bot_api(name, token):
    names = cour.execute("SELECT name FROM bot_api").fetchall()
    if name not in names:
        cour.execute("INSERT INTO bot_api (name, api, date) VALUES (?, ?, ?)",
                     (name, token, str(datetime.now()).replace(":", "-")))
        db.commit()
    else:
        raise ValueError


def get_dropdown_webhook():
    names = cour.execute("SELECT name FROM webhook").fetchall()
    print(names)
    options = []
    for name in names:
        options.append(dropdown.Option(str(name)[2:-3]))

    return options


def get_dropdown_api():
    names = cour.execute("SELECT name FROM bot_api").fetchall()
    print(names)
    options = []
    for name in names:
        options.append(dropdown.Option(str(name)[2:-3]))

    return options

def get_last_name():
    name = cour.execute("SELECT name FROM webhook ORDER BY date").fetchall()[-1]
    return str(name)[2:-3]


def get_last_save_api_name():
    name = cour.execute("SELECT name FROM bot_api ORDER BY date").fetchall()[-1]
    return str(name)[2:-3]


def get_save_url(name):
    return cour.execute("SELECT url FROM webhook WHERE name = :name", {"name": name}).fetchone()[0]


def get_save_api(name):
    return cour.execute("SELECT api FROM bot_api WHERE name = :name", {"name": name}).fetchone()[0]