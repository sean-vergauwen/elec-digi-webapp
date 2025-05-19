from machine import Pin, Timer, time_pulse_us
from time import sleep_us, sleep_ms
"""
Groupe 10 - Voiture LEGO

Ce script est un script de test permettant de vérifier les connexions des
divers composants de notre projet.

Le projet complet et sa documentation se trouvent à cette adresse : 
https://github.com/sean-vergauwen/elec-digi-webapp

Le lien vers la simulation wokwi se trouve ici :
https://wokwi.com/projects/431390513281876993

Auteurs:
- Sean Vergauwen
- Edward Gay
- Noah Cavrenne
- Baris Ozcelik
"""
# Pins pour le 4511 (A LSB, B, C, D MSB)
A = Pin(16, Pin.OUT)
B = Pin(19, Pin.OUT)
C = Pin(18, Pin.OUT)
D = Pin(17, Pin.OUT)

# Transistors pour activer chaque afficheur
segUnit = Pin(28, Pin.OUT)
segDiz = Pin(27, Pin.OUT)

led1 = Pin(14, Pin.OUT)
led2 = Pin(15, Pin.OUT)
led = machine.Pin("LED", machine.Pin.OUT)

# Pins echo et trig du HCSR04
echo = Pin(7, Pin.IN)
trig = Pin(8, Pin.OUT)

distance_timer = Timer()

# Pins moteurs (L298N)
MOTOR_VERTICAL_PIN1 = Pin(12, Pin.OUT)  # pin 1 Avant/Arrière
MOTOR_VERTICAL_PIN2 = Pin(13, Pin.OUT)  # pin 2 Avant/Arrière
MOTOR_HORIZONTAL_PIN1 = Pin(4, Pin.OUT)  # pin 1 Gauche/Droite
MOTOR_HORIZONTAL_PIN2 = Pin(5, Pin.OUT)  # pin 2 Gauche/Droite

led.on()
led1.on()
led2.on()

# Fonction pour contrôler les moteurs (L298N)
def control_motors(direction):
    """
    direction: 0 pour stop, 1 pour avant, 2 pour arrière, 3 pour gauche, 4 pour droite.
    """
    if direction == 0:  # Stop
        MOTOR_VERTICAL_PIN1.off()
        MOTOR_VERTICAL_PIN2.off()
        MOTOR_HORIZONTAL_PIN1.off()
        MOTOR_HORIZONTAL_PIN2.off()
        print("stop")
    elif direction == 1:  # Avant
        MOTOR_VERTICAL_PIN1.on()
        MOTOR_VERTICAL_PIN2.off()
        MOTOR_HORIZONTAL_PIN1.off()
        MOTOR_HORIZONTAL_PIN2.off()
        print("avant")
    elif direction == 2:  # Arrière
        MOTOR_VERTICAL_PIN1.off()
        MOTOR_VERTICAL_PIN2.on()
        MOTOR_HORIZONTAL_PIN1.off()
        MOTOR_HORIZONTAL_PIN2.off()
        print("arrière")
    elif direction == 3:  # Gauche
        MOTOR_VERTICAL_PIN1.off()
        MOTOR_VERTICAL_PIN2.off()
        MOTOR_HORIZONTAL_PIN1.on()
        MOTOR_HORIZONTAL_PIN2.off()
    elif direction == 4:  # Droite
        print("droite")
        MOTOR_VERTICAL_PIN1.off()
        MOTOR_VERTICAL_PIN2.off()
        MOTOR_HORIZONTAL_PIN1.off()
        MOTOR_HORIZONTAL_PIN2.on()

def measure_distance(timer):
    """Fonction de callback du Timer de mesure de distance."""
    trig.low()
    sleep_us(2)

    # Send a 10 microsecond pulse to the trigger pin
    trig.high()
    sleep_us(10)
    trig.low()

    # Measure the duration of the echo pulse (in microseconds)
    pulse_duration = time_pulse_us(echo, Pin.high, 30000)  # added timeout
    if pulse_duration is not None:  # added check
        # Calculate the distance (in centimeters) using the speed of sound (343 m/s)
        distance = pulse_duration * 0.0343 / 2
        print(distance)
    else:
        print("Timeout: No echo received")

# Fonction pour faire tourner les moteurs de manière périodique
def rotate_motors(timer):
    """
    Fonction de callback du timer pour faire tourner les moteurs.
    Change la direction à chaque appel.
    """
    global motor_direction
    motor_direction = (motor_direction + 1) % 5  # Change direction 0, 1, 2, 3, 4, puis retourne à 0
    control_motors(motor_direction) # Appel de la fonction de contrôle des moteurs

def start_distance_monitoring():
    distance_timer.init(
        freq=1002,  # reduced frequency for better performance
        mode=Timer.PERIODIC,
        callback=measure_distance
    )

# Variable globale qui s'incrémente
valeur = 0
motor_direction = 0 # Ajout d'une variable globale pour suivre la direction du moteur

# Affiche un chiffre (0-9) sur le 4511
def output_digit(digit):
    global A, B, C, D
    bin_str = f'{digit:04b}'
    A.value(int(bin_str[-1]))
    B.value(int(bin_str[-2]))
    C.value(int(bin_str[-3]))
    D.value(int(bin_str[-4]))

# Fonction pour afficher la valeur sur les deux 7-segments
def display_value():
    global valeur, segUnit, segDiz
    unite = valeur % 10
    dizaine = valeur // 10

    # Afficher l'unité
    segUnit.value(1)
    segDiz.value(0)
    output_digit(unite)
    sleep_ms(100)
    segUnit.value(0)

    # Afficher la dizaine
    segUnit.value(0)
    segDiz.value(1)
    output_digit(dizaine)
    sleep_ms(100)
    segDiz.value(0)

def increment_value(timer):
    global valeur
    valeur += 1
    if valeur == 100:
        valeur = 0
    print(valeur)
    display_value()

# Initialisation du timer
timer = Timer()
motor_timer = Timer() # Création d'un deuxième timer pour les moteurs
timer_interval_ms = 1000

# Initialisation
def init():
    timer.init(freq=5000, mode=Timer.PERIODIC, callback=increment_value)
    motor_timer.init(freq=2000, mode=Timer.PERIODIC, callback=rotate_motors) # Timer pour les moteurs, fréquence plus basse

# Boucle principale
def main_loop():
    while True:
        pass

# Point d'entrée du programme
if __name__ == "__main__":
    init()
    start_distance_monitoring()
    main_loop()
