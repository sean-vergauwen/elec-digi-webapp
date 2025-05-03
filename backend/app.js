// API Express.js pour recevoir les connexions TCP et contrôler le robot Raspberry Pi Pico W
const express = require('express');
const http = require('http');
const net = require('net');
const bodyParser = require('body-parser');
const cors = require('cors');


// Configuration du serveur
const app = express();
const httpPort = 50902;
const tcpPort = 50903;
const tcpServer = net.createServer();

app.use(cors());

// Middleware
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Stocker la connexion active du Pico W
let picoConnection = null;
let lastCommandTime = Date.now();
const TIMEOUT_INTERVAL = 5000; // 5 secondes

// Créer un serveur TCP
tcpServer.on('connection', (socket) => {
    console.log('Nouvelle connexion TCP reçue de:', socket.remoteAddress);

    // Enregistrer la nouvelle connexion
    picoConnection = socket;

    // Gérer les données reçues du Pico W
    socket.on('data', (data) => {
        const message = data.toString().trim();
        console.log('Message reçu du Pico W:', message);

        // Si c'est un message d'identification
        if (message === 'PICO_CONNECTED') {
            console.log('Raspberry Pi Pico W connecté et prêt à recevoir des commandes');
        }
        // Si c'est un accusé de réception
        else if (message.startsWith('ACK:')) {
            console.log('Accusé de réception:', message);
        }
    });

    // Gérer la fermeture de la connexion
    socket.on('close', () => {
        console.log('Connexion avec le Pico W fermée');
        picoConnection = null;
    });

    // Gérer les erreurs de connexion
    socket.on('error', (err) => {
        console.error('Erreur de connexion TCP:', err.message);
        picoConnection = null;
    });
});

// Démarrer le serveur TCP
tcpServer.listen(tcpPort, () => {
    console.log(`Serveur TCP en écoute sur le port ${tcpPort}`);
});

// Endpoint pour vérifier l'état de la connexion
app.get('/api/status', (req, res) => {
    res.json({
        connected: picoConnection !== null,
        lastCommandTime: lastCommandTime
    });
});

// Endpoint pour envoyer une commande au robot
app.post('/api/command', (req, res) => {
    const { command } = req.body;

    if (!command) {
        return res.status(400).json({ error: 'Commande non spécifiée' });
    }

    // Vérifier si la commande est valide
    const validCommands = ['FORWARD', 'BACKWARD', 'LEFT', 'RIGHT', 'STOP'];
    if (!validCommands.includes(command)) {
        return res.status(400).json({ error: 'Commande invalide' });
    }

    // Vérifier si le Pico W est connecté
    if (!picoConnection) {
        return res.status(503).json({ error: 'Raspberry Pi Pico W non connecté' });
    }

    try {
        // Envoyer la commande au Pico W
        picoConnection.write(command);
        lastCommandTime = Date.now();

        console.log(`Commande "${command}" envoyée au Pico W`);
        res.json({ success: true, command });
    } catch (error) {
        console.error('Erreur lors de l\'envoi de la commande:', error);
        res.status(500).json({ error: 'Erreur lors de l\'envoi de la commande' });
    }
});

// Route pour la page d'accueil - peut servir à tester si l'API fonctionne
app.get('/', (req, res) => {
    res.json({ message: 'API de contrôle de voiture télécommandée active' });
});

// Démarrer le serveur HTTP
const httpServer = http.createServer(app);
httpServer.listen(httpPort, () => {
    console.log(`Serveur HTTP en écoute sur le port ${httpPort}`);
});

// Gérer les erreurs non capturées
process.on('uncaughtException', (err) => {
    console.error('Erreur non capturée:', err);
});