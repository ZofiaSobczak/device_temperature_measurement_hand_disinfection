# Zaimportowanie bibliotek pythona umożliwiającej tworzenie interfejsu graficznego
from tkinter import *
import customtkinter
import sys
# Import biblioteki obsługującej modułu RFID MFRC522
from mfrc522 import SimpleMFRC522
# Import biblioteki do sterowania interfejsem GPIO
import RPi.GPIO as GPIO
# Import biblioteki z modułem czasowym
import time
# Import bibliotek odpowiedzialnych za obsługę bazy danych, wysyłanie emaili oraz pomiar tempratury
import database
import email_sender
import temp_sensors

# Przypisanie loginu oraz hasła dla administratora
ADMIN    = "admin"
PASSWORD = "Admin@123"

# Przypisanie pinów GPIO
GPIO_POMP_SENSOR_1 = 37
GPIO_POMP_SENSOR_2 = 35
GPIO_POMP_OUT      = 33
GPIO_BUZZER        = 29

IDLE_FUNC          = 0
ADD_PERSON_FUNC    = 1
DELETE_PERSON_FUNC = 2
MEASURE_FUNC       = 3

# Ustawienie minimalnej i maksymalnej odległości do pomiaru temperatury
MIN_RANGE = 1 #[cm]
MAX_RANGE = 3 #[cm]

# Ustawienie czsu pracy timera, buzzera oraz pompki
TASK_TIMER   = 100 #[ms]
BUZZER_TIMER = 0.5 #[s]
POMP_TIMER   = 0.35 #[s]

# Określenie zakresu, w którym temperatura uznawana jest za poprawną
WRONG_TEMP_HIGH = 37.8
WRONG_TEMP_LOW = 35.5

actual_card_id = None
task = None
actual_email = None
pomp_time_start = None

# Tworzenie klasy aplikacji
class DeviceApp():
    # Funkcja wywołująca okno główne aplikacji, ustawienie rozmiaru okna, wyświetlanych informacji oraz wyświetlanych przycisków
    def __init__(self, main_window = customtkinter.CTk):
        database.InitDataBase()
        customtkinter.set_appearance_mode("dark")
        self.main_window = main_window()
        self.main_window.geometry("800x480")
        self.main_window.title("Praca inżynierska")
        self.main_text = StringVar(value = "DZIEŃ DOBRY!")
        self.main_label = customtkinter.CTkLabel(master = self.main_window, text_font = (1, 35), textvariable = self.main_text)
        self.main_label.place(relx = 0.5, rely = 0.3, anchor = CENTER)
        self.measure_btn = customtkinter.CTkButton(master = self.main_window, width = 150, height = 150, text = "Pomiar\n temperatury", command = self.MeasureBtnAction)
        self.measure_btn.place(relx = 0.2, rely = 0.7, anchor = CENTER)
        self.cancel_measure_btn = customtkinter.CTkButton(master = self.main_window, width = 150, height = 150, fg_color = "red", text = "Anuluj", command = self.CancelMeasureBtnAction)
        self.cancel_measure_btn.place(relx = 0.8, rely = 0.7, anchor = CENTER)
        self.login_panel_btn = customtkinter.CTkButton(master = self.main_window, width = 150, height = 150, text = "Panel\n administratora", command = self.LoginPanelBtnAction)
        self.login_panel_btn. place(relx = 0.5, rely = 0.7, anchor = CENTER)
        
    # Funkcja opisująca działanie programu po wciśnięciu przycisku "Pomiar temperatury"    
    def MeasureBtnAction(self):
        self.main_window.after(TASK_TIMER, self.ReadCardId, MEASURE_FUNC)
        self.main_text.set("Przyłóż kartę")
     # Funkcja opisująca działanie programu po wciśnięciu przycisku "Panel administratora"   
    def LoginPanelBtnAction(self):
        self.CreateLoginPanel()
    # Funkcja opisująca działanie programu po wciśnięciu przycisku "Anuluj"
    def CancelMeasureBtnAction(self):
        global actual_card_id
        global task
        actual_card_id = None
        self.main_text.set("DZIEŃ DOBRY!")
        if task != None:
            self.main_window.after_cancel(task)
            
    # Funkcja tworząca okno do logowania administratora
    def CreateLoginPanel(self):
        self.login_window = customtkinter.CTkToplevel(master = self.main_window)
        self.login_window.geometry("800x480")
        self.login_window_label = customtkinter.CTkLabel(master = self.login_window, text = "Zaloguj się", text_font = (1, 30))
        self.login_window_label.place(relx = 0.5, rely = 0.25, anchor = CENTER)
        self.login_entry = customtkinter.CTkEntry(master = self.login_window, placeholder_text = "Login", width = 160, height = 50)
        self.login_entry.place(relx = 0.5, rely = 0.4, anchor = CENTER)
        self.password_entry = customtkinter.CTkEntry(master = self.login_window, placeholder_text = "Hasło", show = "*", width = 160, height = 50)
        self.password_entry.place(relx = 0.5, rely = 0.55, anchor = CENTER)
        self.return_from_login_panel_btn = customtkinter.CTkButton(master = self.login_window, width = 120, height = 60, text = "Powrót", command = self.ReturnFromLoginPanelAction)
        self.return_from_login_panel_btn.place(relx = 0.1, rely = 0.1, anchor = CENTER)
        self.login_button = customtkinter.CTkButton(master = self.login_window, width = 120, height = 60, text = "Zaloguj", fg_color = "green", command = self.LoginButtonAction)
        self.login_button.place(relx = 0.5, rely = 0.8, anchor = CENTER)
    # Funkcja opisująca działanie programu po wciśnięciu przycisku "Powrót"
    def ReturnFromLoginPanelAction(self):
        self.login_window.destroy()
    # Funkcja opisująca działanie programu po wciśnięciu przycisku "Zaloguj"
    def LoginButtonAction(self):
        if self.password_entry.get() != PASSWORD or self.login_entry.get() != ADMIN:
            self.wrong_pass_login_label = customtkinter.CTkLabel(master = self.login_window, text = "Błędny login lub hasło", text_font = (1, 10), text_color = "red")
            self.wrong_pass_login_label.place(relx = 0.5, rely = 0.67, anchor = CENTER)
        else:
            self.CreateAdminPanel()
            
    # Funkcja opisująca działanie programu po zalogowaniu do panela administratora
    def CreateAdminPanel(self):
        self.login_window.destroy()
        self.admin_window = customtkinter.CTkToplevel(master = self.main_window)
        self.admin_window.geometry("800x480")
        self.admin_window_txt = StringVar(value = "Wybierz opcję")
        self.admin_label = customtkinter.CTkLabel(master = self.admin_window, text_font = (1, 23), textvariable = self.admin_window_txt)
        self.admin_label.place(relx = 0.5, rely = 0.3, anchor = CENTER)
        self.add_person_btn = customtkinter.CTkButton(master = self.admin_window, width = 150, height = 150, text = "Dodaj pracownika", command = self.AddPersonBtnAction)
        self.add_person_btn.place(relx = 0.2, rely = 0.7, anchor = CENTER)
        self.delete_person_btn = customtkinter.CTkButton(master = self.admin_window, width = 150, height = 150, text = "Usuń pracownika", command = self.DeletePersonBtnAction)
        self.delete_person_btn.place(relx = 0.5, rely = 0.7, anchor = CENTER)
        self.cancel_option_btn = customtkinter.CTkButton(master = self.admin_window, width = 150, height = 150, fg_color = "red", text = "Anuluj", command = self.CancelOptionBtnAction)
        self.cancel_option_btn.place(relx = 0.8, rely = 0.7, anchor = CENTER)
        self.return_from_admin_panel_btn = customtkinter.CTkButton(master = self.admin_window, width = 120, height = 60, text = "Powrót", command = self.ReturnFromAdminPanelBtn)
        self.return_from_admin_panel_btn.place(relx = 0.1, rely = 0.1, anchor = CENTER)
     # Funkcja opisująca działanie programu po wciśnięciu przycisku "Dodaj pracownika"
    def AddPersonBtnAction(self):
        self.admin_window_txt.set("Przyłóż kartę nowego pracownika")
        self.main_window.after(TASK_TIMER, self.ReadCardId, ADD_PERSON_FUNC)
    # Funkcja opisująca działanie programu po wciśnięciu przycisku "Usuń pracownika"    
    def DeletePersonBtnAction(self):
        self.admin_window_txt.set("Przyłóż kartę")
        self.main_window.after(TASK_TIMER, self.ReadCardId, DELETE_PERSON_FUNC)
    # Funkcja opisująca działanie programu po wciśnięciu przycisku "Anuluj"
    def CancelOptionBtnAction(self):
        self.admin_window_txt.set("Wybierz opcję")
    # Funkcja opisująca działanie programu po wciśnięciu przycisku "Powrót"
    def ReturnFromAdminPanelBtn(self):
        self.admin_window.destroy()
    # Funkcja tworząca okno do wprowadzenia danych nowego pracownika
    def CreateAddPersonPanel(self):
        self.add_person_window = customtkinter.CTkToplevel(master = self.main_window)
        self.add_person_window.geometry("800x480")
        self.name_entry = customtkinter.CTkEntry(master = self.add_person_window, placeholder_text = "Imię", width = 160, height = 50)
        self.name_entry.place(relx = 0.5, rely = 0.2, anchor = CENTER)
        self.surname_entry = customtkinter.CTkEntry(master = self.add_person_window, placeholder_text = "Nazwisko", width = 160, height = 50)
        self.surname_entry.place(relx = 0.5, rely = 0.35, anchor = CENTER)
        self.email_entry = customtkinter.CTkEntry(master = self.add_person_window, placeholder_text = "E-Mail", width = 160, height = 50)
        self.email_entry.place(relx = 0.5, rely = 0.5, anchor = CENTER)
        self.add_person_to_db_btn = customtkinter.CTkButton(master = self.add_person_window, width = 120, height = 60, text = "Dodaj", command = self.AddPersonToDbBtnAction)
        self.add_person_to_db_btn.place(relx = 0.5, rely = 0.76, anchor = CENTER)
        self.return_from_add_person_panel = customtkinter.CTkButton(master = self.add_person_window, width = 120, height = 60, text = "Powrót", command = self.ReturnFromAddPesonPanelAction)
        self.return_from_add_person_panel.place(relx = 0.1, rely = 0.1, anchor = CENTER)
    # Funkcja opisująca działanie programu po wciśnięciu przycisku "Dodaj"
    def AddPersonToDbBtnAction(self):
        global actual_card_id
        # Sprawdzanie poprawności wpisanych danych
        if len(self.name_entry.get()) < 2 or len(self.surname_entry.get()) < 2 or email_sender.EmailChecker(self.email_entry.get()) == False:
            self.wrong_personal_label = customtkinter.CTkLabel(master = self.add_person_window, text = "Uzupełnij poprawnie wszystkie pola", text_font = (1, 10), text_color = "red")
            self.wrong_personal_label.place(relx = 0.5, rely = 0.65, anchor = CENTER)
        # Dodawanie nowego pracownika
        else:
            database.AddToDataBase(actual_card_id, self.name_entry.get(), self.surname_entry.get(), self.email_entry.get())
            self.admin_window_txt.set("Dodano pracownika do bazy.\nWybierz opcję")
            actual_card_id = None
            self.add_person_window.destroy()
    # Funkcja opisująca działanie programu po wciśnięciu przycisku "Powrót"
    def ReturnFromAddPesonPanelAction(self):
        self.admin_window_txt.set("Wybierz opcję")
        self.add_person_window.destroy()
        
    
    def Start(self):
        self.main_window.mainloop()
    # Funkcja odczytująca nr ID karty
    def ReadCardId(self, card_func = IDLE_FUNC):
        self.reader = SimpleMFRC522()
        global task
        global actual_card_id
        actual_card_id = self.reader.read_id_no_block()
        print("ID: %s" % (actual_card_id))
        GPIO.cleanup()
        task = self.main_window.after(TASK_TIMER, self.ReadCardId, card_func)
        if actual_card_id != None:
            # Tworzenie okna umożliwiającego wpisanie danych nowego pracownika
            if card_func == ADD_PERSON_FUNC:
                card_func = IDLE_FUNC
                self.main_window.after_cancel(task)
                if False == database.SearchId(actual_card_id):
                    self.CreateAddPersonPanel()
                # Informacja wyświetlana w przypadku występowania danego ID w bazie
                else:
                    self.admin_window_txt.set("Pracownik o podanym ID istnieje już w bazie.\nWybierz opcję")
            # Usuwanie pracownika z bazy danych
            elif card_func == DELETE_PERSON_FUNC:
                card_func = IDLE_FUNC
                self.main_window.after_cancel(task)
                database.DeleteFromDataBase(str(actual_card_id))
                self.admin_window_txt.set("Usunięto pracownika z bazy.\nWybierz opcję")
            # Pomiar temperatury
            elif card_func == MEASURE_FUNC:
                global actual_email
                self.main_window.after_cancel(task)
                # Wykonywanie pomiaru jeśli pracownik o danym ID istnieje w bazie
                if True == database.SearchId(actual_card_id):
                    actual_email = database.SearchEmail(str(actual_card_id))
                    self.main_window.after(TASK_TIMER, self.MeasureTemp)
                # Informacja wyświetlana w przypadku braku pracownika o danym ID w bazie
                else:
                    self.main_text.set("Brak pracownika w bazie.\n Wybierz opcję.")
    
    # Funkcja wykonująca pomiar temperatury
    def MeasureTemp(self):
        global task
        global actual_email
        #
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(GPIO_BUZZER, GPIO.OUT)
        task = self.main_window.after(TASK_TIMER, self.MeasureTemp)
        self.main_text.set("Zbliż czoło do czujnika\n temperatury na odległość\n około 3 cm.")
        distance = temp_sensors.ReadDistance()
        # Sprawdzanie odległości czoła od czujnika
        if distance > MIN_RANGE and distance < MAX_RANGE:
            self.main_window.after_cancel(task)
            time.sleep(1)
            self.employee_temp = temp_sensors.ReadTemp()
            if self.employee_temp > WRONG_TEMP_LOW and self.employee_temp < WRONG_TEMP_HIGH:
                email_sender.SendEmail(actual_email, 0, str(self.employee_temp))
            else:
                email_sender.SendEmail(actual_email, 1, str(self.employee_temp))
            GPIO.output(GPIO_BUZZER, True)
            time.sleep(BUZZER_TIMER)
            GPIO.output(GPIO_BUZZER, False)
            task = self.main_window.after(TASK_TIMER, self.PompProcess)    
    #Funkcja uruchamiająca pompkę
    def PompProcess(self):
        global task
        global pomp_time_start
        GPIO.setup(GPIO_POMP_SENSOR_1, GPIO.IN)
        GPIO.setup(GPIO_POMP_SENSOR_2, GPIO.IN)
        GPIO.setup(GPIO_POMP_OUT, GPIO.OUT)
        GPIO.output(GPIO_POMP_OUT, True)
        #Działanie programu w przypadku nieprzyłożenia obydwu dłoni w miesjce dezynfkecji
        if (GPIO.input(GPIO_POMP_SENSOR_1) == False and GPIO.input(GPIO_POMP_SENSOR_2) == False):
            self.main_window.after_cancel(task)
            pomp_time_start = time.time()
            task = self.main_window.after(TASK_TIMER, self.PompTimer) 
            GPIO.output(GPIO_POMP_OUT, False)
        #Działanie programu w przypadku prawidłowego przyłożenia obydwu dłoni
        else:
            task = self.main_window.after(TASK_TIMER, self.PompProcess)
            if self.employee_temp > WRONG_TEMP_LOW and self.employee_temp < WRONG_TEMP_HIGH:
                self.main_text.set("Temperatura prawidłowa: " + str(self.employee_temp) + "\n" + "Zdezynfekuj obie dłonie.")
            else:
                self.main_text.set("Temperatura nieprawidłowa: " + str(self.employee_temp) + "\n" + "Zdezynfekuj obie dłonie.")
                
    def PompTimer(self):
        global task
        global pomp_time_start
        if ((time.time() - pomp_time_start) > POMP_TIMER):
            GPIO.output(GPIO_POMP_OUT, True)
            self.main_text.set("DZIEŃ DOBRY!")
            self.main_window.after_cancel(task)
        else:
            task = self.main_window.after(TASK_TIMER, self.PompTimer)
app = DeviceApp()
app.Start()