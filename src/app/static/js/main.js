// Connection
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsUrl = `${protocol}//${window.location.host}/ws`;
let socket;
const statusEl = document.getElementById('status');

function connect() {
    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
        console.log("Connected");
        statusEl.textContent = "Connected";
        statusEl.className = "status connected";
    };

    socket.onclose = () => {
        console.log("Disconnected");
        statusEl.textContent = "Disconnected";
        statusEl.className = "status disconnected";
        // Auto reconnect
        setTimeout(connect, 3000);
    };

    socket.onerror = (err) => {
        console.error("Socket error", err);
        socket.close();
    };
}

connect();

// Joystick Logic
const zone = document.getElementById('zone_joystick');
const manager = nipplejs.create({
    zone: zone,
    mode: 'static',
    position: { left: '50%', top: '50%' },
    color: '#06b6d4',
    size: 150
});

// Throttling to prevent flooding BLE
let lastSent = 0;
const SEND_INTERVAL = 100; // ms

function sendDriveCommand(left, right) {
    const now = Date.now();
    if (now - lastSent > SEND_INTERVAL && socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ left, right }));
        lastSent = now;
    }
}

// Map Joystick Data to Tank Drive
manager.on('move', (evt, data) => {
    if (!data.vector) return;

    // x and y are typically -1 to 1 (or close to it) from vector
    // But nipplejs gives angle and distance usually.
    // Let's use generic logic.

    // data.instance.frontPosition is raw {x, y} relative to enter.
    // simpler: utilize data.vector (normalized {x, y})
    const x = data.vector.x;
    const y = data.vector.y;

    // Simple Tank Drive Mixing
    // Speed = Y
    // Turn = X
    // Left = Speed + Turn
    // Right = Speed - Turn

    let left = y * 100 + x * 100;
    let right = y * 100 - x * 100;

    // Clamp to -100 to 100
    left = Math.max(-100, Math.min(100, left));
    right = Math.max(-100, Math.min(100, right));

    sendDriveCommand(Math.round(left), Math.round(right));
});

manager.on('end', () => {
    // Stop on release
    sendDriveCommand(0, 0);
    // Force send stop immediately
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ left: 0, right: 0 }));
    }
});
