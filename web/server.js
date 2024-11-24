const express = require('express');
const http = require('http');
const socketIo = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

const PORT = 3000;

// Статус кулі
let balloonStatus = {
    latitude: 0,
    longitude: 0,
    altitude: 1000, // Висота в метрах
    windSpeed: 10,  // Швидкість вітру
    windDirection: 90, // Напрямок вітру (градуси)
    motors: { left: 0, right: 0 } // Статус двигунів
};

// API для оновлення даних
app.use(express.json());

// Отримання статусу
app.get('/api/status', (req, res) => {
    res.json(balloonStatus);
});

// Керування двигунами
app.post('/api/control', (req, res) => {
    const { motor, value } = req.body;
    if (motor in balloonStatus.motors) {
        balloonStatus.motors[motor] = value;
        io.emit('update', balloonStatus); // Передача нових даних на фронтенд
        res.send({ success: true, message: `Motor ${motor} set to ${value}` });
    } else {
        res.status(400).send({ success: false, message: 'Invalid motor' });
    }
});

// Віддача статичних файлів (інтерфейс)
app.use(express.static('public'));

// WebSocket для реального часу
io.on('connection', (socket) => {
    console.log('Client connected');
    socket.emit('update', balloonStatus);

    socket.on('disconnect', () => {
        console.log('Client disconnected');
    });
});

// Запуск сервера
server.listen(PORT, () => {
    console.log(`Flight control dashboard running at http://localhost:${PORT}`);
});

