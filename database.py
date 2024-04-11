# Import biblioteki umożliwiającej utworzenie bazy danych
import sqlite3
TABLE_NAME = "Pracownicy"
conn = sqlite3.connect('employees.db')
c = conn.cursor()
#Funkcja służąca do tworzenia bazy danych pracowników
def InitDataBase():
    create = 'create table if not exists ' + TABLE_NAME + ' (card_id INTEGER, name TEXT, surname TEXT, email TEXT)'
    c.execute(create)

# Funkcja dodająca pracowników do bazy danych
def AddToDataBase(card_id, name, surname, email):
    c.execute("INSERT INTO " + TABLE_NAME + " VALUES (?, ?, ?, ?)", (card_id, name, surname, email))
    conn.commit() #wykonaj i potwirdź / zapisz

# Funkcja usuwająca pracowników z bazy danych
def DeleteFromDataBase(card_id):
    c.execute("DELETE FROM Pracownicy WHERE card_id = " + card_id)
    conn.commit()
    
# Funkcja sprawdzająca, czy pracownik o danym ID istnieje w bazie
def SearchId(card_id):
    for row in c.execute('SELECT card_id FROM Pracownicy'):
        if card_id == row[0]:
            return True;
    return False

# Funkcja wyszukująca adres email pracownika o danym ID z bazy danych
def SearchEmail(card_id):
    c.execute('SELECT email FROM Pracownicy WHERE card_id = ' + card_id)
    email = c.fetchone() # pobranie całego wiersza z tabeli
    return email[0]