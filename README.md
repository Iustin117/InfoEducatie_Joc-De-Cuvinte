# Jocuri-de-Cuvinte
 
Aplicația web care permite utilizatorilor să se înregistreze, să se autentifice și să participe la un joc de cuvinte, pentru un scor cât mai mare, aceștia pot să vadă în timp real performanțele celorlalți jucători în cafrul unui clasament a primilor cei mai buni 10. Scopul jocului este de a genera cât mai multe cuvinte ceare să rimeze cu un cuvânt de pornire aleator, cu validare automată prin intermediul unui doctionar predefinit.

## Continut tehnic:
>Python
>>Flask
>>
>>SQLite
>>
>>Passlib

>HTML si CSS

## User interfaace:
![image](https://github.com/user-attachments/assets/2ee5440b-bc78-4093-bbc6-c563b7b21091)
![image](https://github.com/user-attachments/assets/7c018988-c474-4e09-8d55-0c6bfe79d420)
![image](https://github.com/user-attachments/assets/2ddc8944-cbf1-4271-b72b-35132c3f3a21)

## Modelul de Bază de Date (Diagramă ERD – descriere text)

    Tabelul users:
        id (PK, autoincrement)
        name (text)
        email (unic, text)
        password (text – stocat criptat)

    Tabelul game:
        game_id (PK, autoincrement)
        user_id (FK, referinţă la users)
        starter_word (text)
        start_time (text, format datetime)
        is_active (integer – 1 activ, 0 inactiv)

    Tabelul score:
        score_id (PK, autoincrement)
        user_id (FK, referinţă la users)
        score (integer)
        timestamp (datetime)
        word_list (text, cuvinte acceptate de utilizator)

    Tabelul starter_words:
        word (PK, text)

![image](https://github.com/user-attachments/assets/6b7f6eef-9a5f-4fa1-bcdd-32420897e6f4)




