const KEY_CODES = {
    "ArrowUp": "forward",
    "ArrowLeft": "left",
    "ArrowRight": "right",
    "ArrowDown": "backward",
};


const pressedKeys = new Set();


// Fonction pour simuler un clic sur un bouton
function simulateButtonClick(buttonId) {
    const button = document.getElementById(buttonId);
    if (button) {
        // Simuler l'apparence d'un clic
        button.classList.add('active');

        // Déclencher l'événement de clic
        button.click();

       // Petit délai avant de retirer l'apparence active (facultatif)
       setTimeout(() => {
           button.classList.remove('active');
       }, 100);
    }
}

// Gestionnaire d'événement pour keydown
function handleKeyDown(event) {
    const buttonId = KEY_CODES[event.key];

    // Vérifier si la touche est une touche directionnelle et n'est pas déjà enfoncée
    if (buttonId && !pressedKeys.has(event.key)) {
       // Ajouter la touche à l'ensemble des touches enfoncées
       pressedKeys.add(event.key);

       // Simuler un clic sur le bouton correspondant
       simulateButtonClick(buttonId);

      // Empêcher le comportement par défaut (comme le défilement de la page)
      event.preventDefault();
    }
}

// Gestionnaire d'événement pour keyup
function handleKeyUp(event) {
    const buttonId = KEY_CODES[event.key];

    // Vérifier si la touche est une touche directionnelle
    if (buttonId) {
        // Retirer la touche de l'ensemble des touches enfoncées
        pressedKeys.delete(event.key);

        // Simuler un clic sur le bouton correspondant (pour arrêter l'action)
        simulateButtonClick(buttonId);

        // Empêcher le comportement par défaut
        event.preventDefault();
    }
}

// Ajouter les gestionnaires d'événements au document
document.addEventListener('keydown', handleKeyDown);
document.addEventListener('keyup', handleKeyUp);


// Fonction pour envoyer une commande à la voiture
function sendCommand(command) {
    fetch('/api/command', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ command }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('last-command').innerText = `Commande envoyée: ${command}`;
            document.getElementById('connection-status').classList.add('connected');
        } else {
            document.getElementById('connection-text').innerText = `Erreur: ${data.error}`;
            document.getElementById('connection-status').classList.remove('connected');
        }
    })
    .catch(error => {
        document.getElementById('connection-text').innerText = `Erreur: ${error.message}`;
        document.getElementById('connection-status').classList.remove('connected');
    });
}

// Vérifier périodiquement l'état de la connexion
function checkStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            const statusElement = document.getElementById('connection-text');
            const connectionStatus = document.getElementById('connection-status');

            if (data.connected) {
                statusElement.innerText = 'Statut: Robot connecté';
                connectionStatus.classList.add('connected');
            } else {
                statusElement.innerText = 'Statut: Robot déconnecté';
                connectionStatus.classList.remove('connected');
            }
        })
        .catch(error => {
            document.getElementById('connection-text').innerText = `Erreur de connexion au serveur: ${error.message}`;
            document.getElementById('connection-status').classList.remove('connected');
        });
}

// Vérifier le statut toutes les 3 secondes
setInterval(checkStatus, 3000);
checkStatus(); // Vérifier immédiatement au chargement