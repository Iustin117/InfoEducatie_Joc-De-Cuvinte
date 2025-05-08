import sqlite3
from datetime import datetime, timedelta

def connect_db():
    return sqlite3.connect('users.db')
    

def delete_old_scores():
    
    conn = connect_db()
    cursor = conn.cursor()

    # calculeaza timestempul de acum o ora
    one_hour_ago = datetime.now() - timedelta(hours=1)
    
    # Sterge toate scorurile care 
    cursor.execute('DELETE FROM score WHERE timestamp < ?', (one_hour_ago,))
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    print("Scores older than one hour deleted successfully.")



def delete_inactive_games():
    
    conn = connect_db()
    cursor = conn.cursor()

    # Sterge jocurile inactive
    cursor.execute('DELETE FROM game WHERE is_active = 0')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    print("Inactive games deleted successfully.")

if __name__ == "__main__":
    conn = connect_db()
    cursor = conn.cursor()
    conn.rollback()
    
