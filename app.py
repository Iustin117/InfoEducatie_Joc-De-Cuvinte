from flask import Flask, render_template, request, redirect, url_for, flash, session
from passlib.hash import sha256_crypt
from datetime import datetime
from models import connect_db, init_db, add_user, get_user_by_email, get_random_starter_word, add_highscore   # Importa functiile mele pentru baze de date
import re  
from datetime import datetime, timedelta
app = Flask(__name__)
app.config['SECRET_KEY'] = 'XXXXX'

# Initiere
init_db()


@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('register'))
    return render_template('index.html')  


#Pentru o eventuala adaugare a Google ads:
@app.route('/ToS-ro')
def ToS():
    return render_template('ToS-ro.html')  
@app.route('/privacy-policy-ro')
def privacy():
    return render_template('privacy-policy-ro.html') 


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('game'))  
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Validare Parola corespunzatoare
        special_characters = re.compile('[@_!#$%^&*()<>?/\\|}{~:]')  # Regex dictionar de caractere speciale
        numbers_characters = re.compile(r'\d')  # Dictionar cifre (0-9)
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return redirect(url_for('register'))

        if not special_characters.search(password):
            flash('Password must contain at least one special character.', 'danger')
            return redirect(url_for('register'))
        if not numbers_characters.search(password):
            flash('Password must contain at least one digit character.', 'danger')
            return redirect(url_for('register'))

        # Hash 
        hashed_password = sha256_crypt.hash(password)

        # Adauga client in db
        if add_user(name, email, hashed_password):
            flash('User Registered Successfully!', 'success')
            return redirect(url_for('login'))
        else:
            flash('Email already registered!', 'danger')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))  # daca s a gasit cookie go index

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # cauta dupa mail
        user = get_user_by_email(email)

        # verifica parola
        if user and sha256_crypt.verify(password, user[3]):
            # salvam user_id pt evidenta ca e conectat
            session['user_id'] = user[0]
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login failed. Check email and password.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)  # eliminam cookie
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/game')
def game():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    # verifica daca deja are un joc inceput
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM game WHERE user_id = ? AND is_active = 1', (user_id,))
    active_game = cursor.fetchone()

    if active_game:
        # verifica daca jocul s a teminat
        game_start_time = datetime.strptime(active_game[3], '%Y-%m-%d %H:%M:%S')
        time_passed = datetime.now() - game_start_time
        if time_passed < timedelta(minutes=3):
            remaining_time = 3 * 60 - time_passed.seconds
            starter_word = active_game[2]
            return render_template('game.html', word=starter_word, remaining_time=remaining_time)
        else:
            # marcheaza joc ca terminat, sa il stergem mai tarziu
            cursor.execute('UPDATE game SET is_active = 0 WHERE game_id = ?', (active_game[0],))
            conn.commit()

    # Incepe alt joc
    starter_word = get_random_starter_word()
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        INSERT INTO game (user_id, starter_word, start_time, is_active) 
        VALUES (?, ?, ?, 1)
    ''', (user_id, starter_word, current_time))
    conn.commit()
    conn.close()

    return render_template('game.html', word=starter_word, remaining_time=180)
@app.route('/submit_game', methods=['POST'])
def submit_game():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user_words = request.form.get('user_words', '').split()  # separare cuvinte 
    conn = connect_db()
    cursor = conn.cursor()

    # gaseste jocul activ 
    cursor.execute('SELECT * FROM game WHERE user_id = ? AND is_active = 1', (user_id,))
    active_game = cursor.fetchone()

    if not active_game:
        return redirect(url_for('game'))  # Redirectionare pe pagina principala dupa finalul jocului

    starter_word = active_game[2]

    # validare locala a cuvintelor prin dicionar
    valid_words = []
    seen_words = set()  # Se elimina duplicatele

    for word in user_words:
        word = word.lower()  # Normalizare din litere mari in litere mici
        if word not in seen_words:  # Se verifica cuvintele duplicate
            if validate_word(word) and check_rhyme(word, starter_word):  # Valideaza si verifica rima
                valid_words.append(word)
                seen_words.add(word)  # Marcare/Punctare cuvant corect

    # Numarare puncte
    score = len(valid_words)
    if score > 100: #aici avem o metoda primitiva pentru 
        score = -score
    # Salveaza outcome ul jocului
    word_list = ', '.join(valid_words)
    add_highscore(user_id, score, word_list)

    # Seteaza jocul inactiv
    cursor.execute('UPDATE game SET is_active = 0 WHERE game_id = ?', (active_game[0],))
    conn.commit()
    conn.close()

    return redirect(url_for('profile'))

@app.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    conn = connect_db()
    cursor = conn.cursor()

    # Gaseste numele userului
    cursor.execute('SELECT name FROM users WHERE id = ?', (user_id,))
    user_name = cursor.fetchone()

    if not user_name:
        return redirect(url_for('login'))  # eroare -> login

    # Gaseste scor
    cursor.execute('SELECT MAX(score) FROM score WHERE user_id = ?', (user_id,))
    best_score = cursor.fetchone()[0] or 0  # se pune 0 daca nu are nici un scor

    # Gaseste doar ultimele 10 jocuri 
    cursor.execute('''
        SELECT score, word_list, timestamp 
        FROM score 
        WHERE user_id = ? 
        ORDER BY timestamp DESC LIMIT 10
    ''', (user_id,))
    last_games = cursor.fetchall()

    conn.close()

    return render_template('profile.html', user_name=user_name[0], best_score=best_score, last_games=last_games)



@app.route('/highscores')
def highscores():
    conn = connect_db()
    cursor = conn.cursor()
    
    # Gaseste nume scor timp ordoneaza descrescator duoa scor 
    cursor.execute('''
    SELECT name, score, timestamp
    FROM (
        SELECT
            u.name,
            s.score,
            s.timestamp,
            ROW_NUMBER() OVER (
                PARTITION BY s.user_id
                ORDER BY s.score DESC
            ) AS rn
        FROM score AS s
        JOIN users AS u
            ON s.user_id = u.id
    ) AS ranked
    WHERE rn = 1
    ORDER BY score DESC
    LIMIT 10;
''') # ar trebuii impementata o limita 
    
    scores = cursor.fetchall()
    conn.close()

    # Gaseste highscorurile fiecarui jucator
    best_scores = {}
    for name, score, timestamp in scores:
        if name not in best_scores or best_scores[name][0] < score:
            best_scores[name] = (score, timestamp)

    # Formeaza o lista
    final_scores = [(name, score, timestamp) for name, (score, timestamp) in best_scores.items()]

    return render_template('highscores.html', scores=final_scores)






#### Game word validation:

def check_rhyme(word1, word2):
    word1 = word1.lower()
    word2 = word2.lower()
    if word1 == word2:
        return False

    return word1[-2:] == word2[-2:] or word1[-3:] == word2[-3:]


def load_dictionary(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return set(word.strip() for word in f.readlines())

dictionary = load_dictionary('romanian_dictionary.txt')

def validate_word(word):
    return word.lower() in dictionary


if __name__ == '__main__':
    app.run(debug=True, port=8080)
