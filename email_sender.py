# Import biblioteki umożliwiającej wysyłanie wiadomości email
import smtplib

# Określenie portu służącego do komunikacji między serwerami obsługującymi pocztę elektroniczną
PORT = 587
SMTP_SERVER = "smtp.gmail.com"
SENDER = 'praca.inz.python.2022@gmail.com'
PASSWORD = 'ditrwndeatyyogst'
EMAIL_MIN_SIGNS = 6

# Ustawienie treści wysyłanej w wiadomości email
HEADER = "Subject: Pomiar temperatury ciala"
ADMISSION = "Witaj, \r\nTwoja temperatura wynosi: "
GOOD_TEMP = "Twoja temperatura jest prawidlowa."
BAD_TEMP = "Twoja temperatura jest nieprawidlowa. Powinienes opuscic miejsce pracy."

# Funkcja wysyłająca wiadomości email
def SendEmail(receiver, func, temp):
    server =  smtplib.SMTP(SMTP_SERVER, PORT)
    server.ehlo()
    server.starttls()
    server.login(SENDER, PASSWORD)
    if func == 0:
        server.sendmail(SENDER, receiver, HEADER + "\r\n\r\n" + ADMISSION + temp + " stopni Celsjusza. " + GOOD_TEMP)
    else:
        server.sendmail(SENDER, receiver, HEADER + "\r\n\r\n" + ADMISSION + temp + " stopni Celsjusza. " + BAD_TEMP)
    server.quit
   
# Funkcja sprawdzająca poprawność wpisanego adresu email   
def EmailChecker(email):
    if len(email) < EMAIL_MIN_SIGNS:
        return False
    for i in range(len(email)):
        if email[i] == "@":
            break
    for j in range(i, len(email)):
        if email[j] == ".":
            break
    if (len(email) - 1) - j >= 2:
        return True
    return False