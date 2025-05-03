import network
import socket
import time
from machine import Pin

# Configuration Wi-Fi
SSID = "Sean"
PASSWORD = "ouioui123"

BACKEND_IP = "81.243.84.122"
BACKEND_PORT = 50903

led = Pin("LED", Pin.OUT)
led.off()

# Moteur haut bas
IN1 = Pin(12, Pin.OUT)
IN2 = Pin(13, Pin.OUT)
# Moteur gauche droite
IN3 = Pin(4, Pin.OUT)
IN4 = Pin(5, Pin.OUT)

GOING_FORWARD = False
GOING_BACKWARD = False

GOING_LEFT = False
GOING_RIGHT = False

# Initialisation des broches des moteurs
def init_motors():
    # Avant arrière arrêté
    IN1.off()
    IN2.off()
    # Gauche droite arrêté
    IN3.off()
    IN4.off()
    print("Moteurs initialisés")

def move_car(direction):
    global GOING_FORWARD, GOING_BACKWARD, GOING_LEFT, GOING_RIGHT
    if direction == "haut":
        if GOING_FORWARD:
            GOING_FORWARD = False    
            IN1.off()
            IN2.off()
            print("Stop Avancer")
        else:
            GOING_FORWARD = True
            GOING_BACKWARD = False
            IN1.on()
            IN2.off()
            print("Avancer")
        
    if direction == "bas":
        if GOING_BACKWARD:
            GOING_BACKWARD = False
            IN1.off()
            IN2.off()
            print("Stop Reculer")
        else:
            GOING_BACKWARD = True
            GOING_FORWARD = False
            IN1.off()
            IN2.on()
            print("Reculer")
        
    if direction == "gauche":
        if GOING_LEFT:
            GOING_LEFT = False
            IN3.off()
            IN4.off()
            print("Stop Gauche")
        else:
            GOING_LEFT = True
            GOING_RIGHT = False
            IN3.on()
            IN4.off()
            print("Gauche")
        
    if direction == "droite":
        if GOING_RIGHT:
            GOING_RIGHT = False
            IN3.off()
            IN4.off()
            print("Stop droite")
        else:
            GOING_RIGHT = True
            GOING_LEFT = False
            IN3.off()
            IN4.on()
            print("Droite")
        
    if direction == "stop":
        # Arrêter tous les moteurs
        GOING_FORWARD = False
        GOING_BACKWARD = False
        GOING_LEFT = False
        GOING_RIGHT = False
        IN1.off()
        IN2.off()
        IN3.off()
        IN4.off()
        print("Arrêt")

# Connexion au réseau Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    print(f"Connexion au réseau Wi-Fi {SSID}...")
    wlan.connect(SSID, PASSWORD)
    
    # Attente de la connexion avec timeout
    max_wait = 10
    while max_wait > 0:
        if wlan.status() == network.STAT_GOT_IP:
            break
        max_wait -= 1
        print("En attente de connexion...")
        time.sleep(1)
    
    if wlan.status() == network.STAT_GOT_IP:
        ip = wlan.ifconfig()[0]
        print(f"Connecté! Adresse IP: {ip}")
        return ip
    else:
        print("Échec de connexion")
        return None
    
def connect_to_server():
    """Établit une connexion TCP avec le serveur et traite les commandes"""
    while True:
        try:
            print(f"Tentative de connexion au serveur: {BACKEND_IP}:{BACKEND_PORT}")
            s = socket.socket()
            s.connect((BACKEND_IP, BACKEND_PORT))
            print("Connexion établie avec le serveur")
            led.on()  # Allumer la LED pour indiquer la connexion
            
            # Envoyer un message d'identification au serveur
            s.send("PICO_CONNECTED".encode())
            
            # Boucle pour recevoir et traiter les commandes
            while True:
                data = s.recv(1024)
                if not data:
                    print("Connexion fermée par le serveur")
                    break
                
                command = data.decode().strip()
                print(f"Commande reçue: {command}")
                
                # Traiter la commande
                if command == "FORWARD":
                    move_car("haut")
                elif command == "BACKWARD":
                    move_car("bas")
                elif command == "LEFT":
                    move_car("gauche")
                elif command == "RIGHT":
                    move_car("droite")
                elif command == "STOP":
                    move_car("stop")
                else:
                    print(f"Commande inconnue: {command}")
                
                # Envoyer un accusé de réception
                s.send(f"ACK:{command}".encode())
            
            s.close()
            led.off()  # Éteindre la LED lorsque la connexion est fermée
            
        except OSError as e:
            print(f"Erreur de connexion: {e}")
            led.value(0)
            time.sleep(5)  # Attendre avant de réessayer
        
        print("Tentative de reconnexion dans 5 secondes...")
        time.sleep(5)

# Fonction principale
def main():
    # Initialiser les moteurs
    init_motors()
    
    # Se connecter au Wi-Fi
    private_ip = connect_wifi()
    if not private_ip:
        print("Impossible de continuer sans connexion Wi-Fi")
        return
    
    connect_to_server()
     
# Exécuter le programme
if __name__ == "__main__":
    main()




