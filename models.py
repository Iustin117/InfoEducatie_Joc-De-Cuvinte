import sqlite3
from datetime import datetime

# Conecteaza te la baza de date
def connect_db():
    return sqlite3.connect('users.db')

# initializeaza schema
def init_db():
    conn = connect_db()
    cursor = conn.cursor()

    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game (
            game_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            starter_word TEXT NOT NULL,
            start_time TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS score (
            score_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,  
            word_list TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS starter_words (
            word TEXT NOT NULL PRIMARY KEY
        )
    ''')
    #pentru test 
    cursor.execute('SELECT COUNT(*) FROM starter_words')
    count = cursor.fetchone()[0]
    if count == 0:
        starter_words = ['copil', 'mura', 'capsuna', 'melc', 'copa', 'balon', 'mama', 'pui']
        cursor.executemany('INSERT INTO starter_words (word) VALUES (?)', [(word,) for word in starter_words])


    conn.commit()
    conn.close()






###### Functii folositoare




###  Adauga High Score

from datetime import datetime
def add_highscore(user_id, score, word_list):
    conn = connect_db()
    cursor = conn.cursor()

    current_timestamp = datetime.now()

    cursor.execute('''
        INSERT INTO score (user_id, score, timestamp, word_list) 
        VALUES (?, ?, ?, ?)
    ''', (user_id, score, current_timestamp, word_list))
    
    conn.commit()
    conn.close()
def add_user(name, email, password):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', (name, email, password))
        conn.commit()
    except sqlite3.IntegrityError:
        return False  # cazul in care deja exista emailul
    finally:
        conn.close()
    return True


def get_user_by_email(email):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_scores_by_user(user_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM score WHERE user_id = ? ORDER BY date DESC
    ''', (user_id,))
    
    scores = cursor.fetchall()
    conn.close()
    return scores


### Gaseste userul dupa scor 
def get_user_by_score(score):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT u.* FROM users u 
        JOIN score s ON u.id = s.user_id 
        WHERE s.score = ?
    ''', (score,))
    
    user = cursor.fetchone()
    conn.close()
    return user


### Gaseste High Score al utilizatorului
def get_user_high_score(user_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT MAX(score) FROM score WHERE user_id = ?
    ''', (user_id,))
    
    high_score = cursor.fetchone()
    conn.close()
    return high_score


### Selecteaza cuvant de inceput
def get_random_starter_word():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('SELECT word FROM starter_words ORDER BY RANDOM() LIMIT 1')
    starter_word = cursor.fetchone()[0]
    
    conn.close()
    return starter_word
