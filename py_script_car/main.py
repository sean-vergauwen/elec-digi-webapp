"""
Script pour une voiture télécommandée LEGO avec un raspberry Pi Pico W

Le but du script est de se connecter au Wi-fi puis à notre serveur TCP
pour que le raspberry puissent recevoir les commandes venant du serveur

Lien vers l'interface Web servant à la diriger : https://voiture.seanvergauwen.com
"""
import network
import socket
import time
from machine import Pin, time_pulse_us, Timer

# Constantes
class Config:
    WIFI_SSID = "Sean"
    WIFI_PASSWORD = "ouioui123"
    
    SERVER_IP = "81.243.84.122"
    SERVER_PORT = 50903
    RECONNECT_DELAY_SEC = 5
    
    # Paramètres du HC-SR04
    DISTANCE_THRESHOLD_CM = 12  # Distance en dessous de laquelle la voiture ne peut plus avancer, en cm
    ECHO_TIMEOUT_US = 500 * 2 * 30
    MEASURE_INTERVAL_MS = 100

    # Pins echo et trig du HCSR04
    ECHO_PIN = 7
    TRIG_PIN = 8
    
    # Pin de la led sur le pico
    LED_PIN = "LED"
    
    # Pins moteurs 
    MOTOR_VERTICAL_PIN1 = 12   # pin 1 Avant/Arrière
    MOTOR_VERTICAL_PIN2 = 13   # pin 2 Avant/Arrière
    MOTOR_HORIZONTAL_PIN1 = 4  # pin 1 Gauche/Droite
    MOTOR_HORIZONTAL_PIN2 = 5  # pin 2 Gauche/Droite
    
    # Commandes
    CMD_FORWARD = "FORWARD"
    CMD_BACKWARD = "BACKWARD"
    CMD_LEFT = "LEFT"
    CMD_RIGHT = "RIGHT"
    CMD_STOP = "STOP"
    
    MSG_PICO_CONNECTED = "PICO_CONNECTED"
    MSG_ACK_PREFIX = "ACK:"


class Car:
    """Contrôles de la voiture et de détection d'obstacles."""
    
    def __init__(self):
        # Initialise la led
        self.led = Pin(Config.LED_PIN, Pin.OUT)
        self.led.off()
        
        # Initialize les moteurs à 0/0
        self.init_motors()
        
        # Initialise le HC-SR04
        self.echo = Pin(Config.ECHO_PIN, Pin.IN, Pin.PULL_DOWN)
        self.trig = Pin(Config.TRIG_PIN, Pin.OUT)
        
        # Initialise le timer sur lequel le HC-SR04 va fonctionner
        self.distance_timer = Timer()
        
        # Initialise les variables de mouvement
        self.is_moving_forward = False
        self.is_moving_backward = False
        self.is_moving_left = False
        self.is_moving_right = False
        
        # Initialise le flag de détection d'obstacles
        self.obstacle_detected = False
    
    def init_motors(self):
        """Initialize les pins moteurs."""
        # Pins Avant/Arrière
        self.motor_v_pin1 = Pin(Config.MOTOR_VERTICAL_PIN1, Pin.OUT)
        self.motor_v_pin2 = Pin(Config.MOTOR_VERTICAL_PIN2, Pin.OUT)
        
        # Pins Gauche/Droite
        self.motor_h_pin1 = Pin(Config.MOTOR_HORIZONTAL_PIN1, Pin.OUT)
        self.motor_h_pin2 = Pin(Config.MOTOR_HORIZONTAL_PIN2, Pin.OUT)
        
        # Initialise tous les moteurs à 0
        self.motor_v_pin1.off()
        self.motor_v_pin2.off()
        self.motor_h_pin1.off()
        self.motor_h_pin2.off()
    
    def start_distance_monitoring(self):
        """Lance le timer pour la détection d'obstacles."""
        self.distance_timer.init(
            freq=1000 / Config.MEASURE_INTERVAL_MS,
            mode=Timer.PERIODIC,
            callback=lambda t: self.measure_distance()
        )
    
    def measure_distance(self):
        """Fonction de callback du Timer de mesure de distance."""
        # Reset le trig
        self.trig.value(0)
        time.sleep_us(2)
        
        # Envoi d'une pulsation de 10μs
        self.trig.value(1)
        time.sleep_us(10)
        self.trig.value(0)
        
        # Mesure de la durée de l'echo
        pulse_time = time_pulse_us(self.echo, 1, Config.ECHO_TIMEOUT_US)
        
        # Ensuite on calcule en Cm
        if pulse_time < 0:  # Sert à catch les erreurs que le HC-SR04 peut renvoyer (il est un peu têtu)
            distance_cm = -1
        else:
            distance_cm = pulse_time * 0.0171  # Conversion
        
        # Check si il y a un obstacle
        if 0 < distance_cm <= Config.DISTANCE_THRESHOLD_CM:
            print(f"ATTENTION: Obstacle détecté à {distance_cm:.1f}cm")
            if self.is_moving_forward:
                self.stop_vertical_movement()
                self.obstacle_detected = True
        else:
            self.obstacle_detected = False
    
    def move_forward(self):
        """Fait avancer la voiture vers l'avant si il n'y a pas d'obstacles."""
        if self.obstacle_detected:
            print("Peut pas avancer, il y a un obstacle")
            return
            
        if not self.is_moving_forward:
            self.is_moving_forward = True
            self.is_moving_backward = False
            self.motor_v_pin1.off()
            self.motor_v_pin2.on()
            print("Vroom vroom")
        else:
            self.stop_vertical_movement()
            print("Plus de vroom vroom")
    
    def move_backward(self):
        """Fait reculer la voiture"""
        if not self.is_moving_backward:
            self.is_moving_backward = True
            self.is_moving_forward = False
            self.obstacle_detected = False  # On reset le flag au cas où
            self.motor_v_pin1.on()
            self.motor_v_pin2.off()
            print("On reculeeee")
        else:
            self.stop_vertical_movement()
            print("On recule plus")
    
    def move_left(self):
        """Fait tourner la voiture à gauche"""
        if not self.is_moving_left:
            self.is_moving_left = True
            self.is_moving_right = False
            self.motor_h_pin1.on()
            self.motor_h_pin2.off()
            print("A babôrd mon capitaine !")
        else:
            self.stop_horizontal_movement()
            print("Plus de babôrd par ici")
    
    def move_right(self):
        """Fait tourner la voiture à droite"""
        if not self.is_moving_right:
            self.is_moving_right = True
            self.is_moving_left = False
            self.motor_h_pin1.off()
            self.motor_h_pin2.on()
            print("A TRIBORD TOUTE !!!")
        else:
            self.stop_horizontal_movement()
            print("Finito de triborder ici")
    
    def stop_vertical_movement(self):
        """Stoppe les moteurs Avant/Arrière"""
        self.is_moving_forward = False
        self.is_moving_backward = False
        self.motor_v_pin1.off()
        self.motor_v_pin2.off()
    
    def stop_horizontal_movement(self):
        """Stoppe les moteurs Gauche/Droite"""
        self.is_moving_left = False
        self.is_moving_right = False
        self.motor_h_pin1.off()
        self.motor_h_pin2.off()
    
    def stop_all_movement(self):
        """Stoppe tous les moteurs"""
        self.stop_vertical_movement()
        self.stop_horizontal_movement()
        print("Arrêt total")
    
    def process_command(self, command):
        """Sert à recevoir les commandes et les traiter"""
        if command == Config.CMD_FORWARD:
            self.move_forward()
        elif command == Config.CMD_BACKWARD:
            self.move_backward()
        elif command == Config.CMD_LEFT:
            self.move_left()
        elif command == Config.CMD_RIGHT:
            self.move_right()
        elif command == Config.CMD_STOP:
            self.stop_all_movement()
        else:
            print(f"Commande inconnue: {command}")
            return False
        return True


class NetworkManager:
    """Gère la connexion Wifi et au serveur TCP."""
    
    def __init__(self, car):
        self.car = car
        self.wlan = network.WLAN(network.STA_IF)
    
    def connect_wifi(self, max_attempts=15):
        """Connecte au Wi-fi"""
        self.wlan.active(True)
        
        print(f"Connexion au réseau : {Config.WIFI_SSID}...")
        self.wlan.connect(Config.WIFI_SSID, Config.WIFI_PASSWORD)
        
        # On attend que la connexion se fasse
        attempts = 0
        while attempts < max_attempts:
            if self.wlan.status() == network.STAT_GOT_IP:
                ip_address = self.wlan.ifconfig()[0]
                print(f"Connecté! Adresse IP: {ip_address}")
                return True
                
            attempts += 1
            print(f"En attente de connexion... ({attempts}/{max_attempts})")
            time.sleep(1)
        
        print("Connexion au Wi-fi ratée")
        return False
    
    def connect_to_server(self):
        """Etablit une connexion TCP avec le serveur et lance le traitement des commandes"""
        while True:
            try:
                print(f"Tentative de connexion au serveur : {Config.SERVER_IP}:{Config.SERVER_PORT}")
                sock = socket.socket()
                sock.connect((Config.SERVER_IP, Config.SERVER_PORT))
                print("Connexion étable")
                self.car.led.on()  # On allume la LED comme ça on voit (lol)
                
                # On envoie le message d'authentification
                sock.send(Config.MSG_PICO_CONNECTED.encode())
                
                # On entre dans la loop principale de traitement des commandes
                self._process_server_commands(sock)
                
            except OSError as e:
                print(f"Erreur de connexion: {e}")
                self.car.led.off()
                time.sleep(Config.RECONNECT_DELAY_SEC)
            
            print(f"Tentative de reconnexion dans {Config.RECONNECT_DELAY_SEC} secondes...")
            time.sleep(Config.RECONNECT_DELAY_SEC)
    
    def _process_server_commands(self, sock):
        """Traite les commandes venant du serveur."""
        try:
            while True:
                data = sock.recv(1024)
                if not data:
                    print("Connexion fermée par le serveur")
                    break
                
                command = data.decode().strip()
                print(f"Commande reçue: {command}")
                
                # Traite la commande du côté de la voiture
                success = self.car.process_command(command)
                ack_message = f"{Config.MSG_ACK_PREFIX}{command}"
                sock.send(ack_message.encode())
                
        finally:
            sock.close()
            self.car.led.off()


def main():
    """Point d'entrée du script."""
    try:
        # Initialise le contrôleur de la voiture
        car = Car()
        
        # Initialise le contrôleur de connexion
        network_mgr = NetworkManager(car)
        
        # Se connecte au wifi
        if not network_mgr.connect_wifi():
            print("Connexion au Wi-fi non concluante")
            return
        
        # Lance le timer de mesure de distances
        car.start_distance_monitoring()
        
        # Se connecte au serveur et ensuite traite les commandes
        network_mgr.connect_to_server()
        
    except Exception as e:
        print(f"Erreur inconnue : {e}")


# Lance le programme
if __name__ == "__main__":
    main()

