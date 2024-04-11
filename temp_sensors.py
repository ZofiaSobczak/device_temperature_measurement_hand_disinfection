# Import biblioteki z modułem czasowym
import time
# Import biblioteki do sterowania interfejsem GPIO
import RPi.GPIO as GPIO
# Import biblioteki obsługującej magistralę I2C
from smbus2 import SMBus
# Import biblioteki obsługującej czujnik temperatury MLX90614
from mlx90614 import MLX90614

# Przypisanie pinów GPIO

GPIO_TRIGGER = 40
GPIO_ECHO    = 38

# Ustawienie liczby pomiarów, oraz prędkości dźwięku

NUM_OF_MEASURMENTS = 10
TEMP_OFFSET = 2
SOUND_SPEED = 34300 #[cm/s]


# Funkcja odpowiedzialna za pomiar odległości głowy od czujników

def ReadDistance():
    # Ustawienie pinow triggerr i echo
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
    GPIO.setup(GPIO_ECHO, GPIO.IN)
    # Ustawienie triggera na stan wysoki na 0.01ms
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    # Zmiana stanu triggera na niski
    GPIO.output(GPIO_TRIGGER, False)
    # Utworzenie zmiennych    
    low_time = time.time()
    high_time = time.time()
    # Pomiar czasu stanu niskiego na echo
    while GPIO.input(GPIO_ECHO) == 0:
        low_time = time.time()
    #Pomiar czasu stanu wysokiego na echo
    while GPIO.input(GPIO_ECHO) == 1:
        high_time = time.time()
    #Obliczanie odległości na podstawie czasu stanów wysokiego i niskiego
    time_elapsed = high_time - low_time
    distance = (time_elapsed * SOUND_SPEED) / 2
    return distance

# Funkcja odczytu temperatury
def ReadTemp():
    bus = SMBus(1)
    # Przywołanie adresu czujnika temperatury
    sensor = MLX90614(bus, address = 0x5A)
    temp_sum = 0
    for i in range(0, NUM_OF_MEASURMENTS):
        temp_sum += sensor.get_obj_temp()
        print(temp_sum)
    # Obliczenie średniej temperatury
    average_temp = temp_sum / NUM_OF_MEASURMENTS
    # Dodanie do wyniku końcowego offsetu
    average_temp += TEMP_OFFSET
    bus.close()
    return round(average_temp, 1)