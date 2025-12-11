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
    sendDriveCommand(0, 0);
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ left: 0, right: 0 }));
    }
});


// --- Gamepad Support ---
let gamepadIndex = null;
const GAMEPAD_DEADZONE = 0.1;

window.addEventListener("gamepadconnected", (e) => {
    console.log("Gamepad connected at index %d: %s. %d buttons, %d axes.",
        e.gamepad.index, e.gamepad.id,
        e.gamepad.buttons.length, e.gamepad.axes.length);
    gamepadIndex = e.gamepad.index;
    statusEl.textContent = "Gamepad Connected";
    requestAnimationFrame(gamepadLoop);
});

window.addEventListener("gamepaddisconnected", (e) => {
    console.log("Gamepad disconnected from index %d: %s",
        e.gamepad.index, e.gamepad.id);
    if (gamepadIndex === e.gamepad.index) {
        gamepadIndex = null;
        statusEl.textContent = "Gamepad Disconnected";
    }
});

function applyDeadzone(value) {
    if (Math.abs(value) < GAMEPAD_DEADZONE) return 0;
    return value;
}

function gamepadLoop() {
    if (gamepadIndex !== null) {
        const gamepads = navigator.getGamepads();
        const gp = gamepads[gamepadIndex];

        if (gp) {
            // Xbox Layout usually:
            // Axis 0: Left Stick X
            // Axis 1: Left Stick Y
            // Axis 2: Right Stick X
            // Axis 3: Right Stick Y

            // Arcade Drive
            // Speed: Left Stick Y (Axis 1) - Up is -1 normally, invert it.
            const speed = -applyDeadzone(gp.axes[1]);
            // Turn: Right Stick X (Axis 2)
            const turn = applyDeadzone(gp.axes[2]);

            // Mixing
            let left = (speed + turn) * 100;
            let right = (speed - turn) * 100;

            // Clamp
            left = Math.max(-100, Math.min(100, left));
            right = Math.max(-100, Math.min(100, right));

            // Only send if non-zero or specific interval? 
            // We reuse sendDriveCommand which handles interval.
            // But we should prioritize gamepad if it's being used?
            // For now, let's just send it.

            // Check if active (prevent jitter sending 0s over and over if touch is idle)
            if (Math.abs(left) > 0 || Math.abs(right) > 0) {
                sendDriveCommand(Math.round(left), Math.round(right));
            } else {
                // Determine if we should send stop? 
                // Rely on Interval for now, but if user lets go, we want quick stop.
                // sendDriveCommand will prevent spamming. 
                // Let's send 0 if we were moving recently? 
                // Simplified: Just update loop.
                sendDriveCommand(0, 0);
            }
        }
        requestAnimationFrame(gamepadLoop);
    }
}

