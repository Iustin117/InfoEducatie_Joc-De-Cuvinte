import sqlite3

def connect_db():
    
    return sqlite3.connect('users.db')

def add_words_from_file(filename):
    conn = connect_db()
    cursor = conn.cursor()

    # Citeste cuvinte din fisier
    with open(filename, 'r', encoding='utf-8') as file:
        words = [line.strip() for line in file if line.strip()]  # Sterge linii goale

    # SQL insereaaza valori
    cursor.executemany('INSERT INTO starter_words (word) VALUES (?)', [(word,) for word in words])
    
    conn.commit()
    conn.close()

    print(f"Added {len(words)} words to the database from {filename}.")

if __name__ == "__main__":
    
    add_words_from_file('words.txt')
