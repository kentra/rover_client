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

// --- Dual Joystick Setup ---
const JOYSTICK_SIZE = 150;
const managerLeft = nipplejs.create({
    zone: document.getElementById('zone_left'),
    mode: 'static',
    position: { left: '50%', top: '50%' },
    color: 'cyan',
    size: JOYSTICK_SIZE
});

const managerRight = nipplejs.create({
    zone: document.getElementById('zone_right'),
    mode: 'static',
    position: { left: '50%', top: '50%' },
    color: 'cyan',
    size: JOYSTICK_SIZE
});

// State
let motorLeft = 0;
let motorRight = 0;
// let isTouchActive = false; // Not strictly needed with current logic, gamepad will override if touch is idle.

// Throttling
let lastSent = 0;
const SEND_INTERVAL = 50;

function sendLoop() {
    const now = Date.now();
    if (now - lastSent > SEND_INTERVAL && socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ left: Math.round(motorLeft), right: Math.round(motorRight) }));
        lastSent = now;
    }
    requestAnimationFrame(sendLoop);
}
requestAnimationFrame(sendLoop);


// --- Touch Logic (Tank Drive) ---
function handleTouchMove(evt, data, side) {
    if (!data.vector) return;
    // isTouchActive = true; // See comment above
    const y = data.vector.y;
    // Map -1..1 to -100..100
    const val = Math.max(-100, Math.min(100, y * 100));

    if (side === 'left') motorLeft = val;
    if (side === 'right') motorRight = val;
}

function handleTouchEnd(evt, data, side) {
    if (side === 'left') motorLeft = 0;
    if (side === 'right') motorRight = 0;

    // Check if both stopped to clear flag? 
    // Simplified: Just clear values.
    // We keep isTouchActive true for a bit? No, just rely on values.
    // If no active touches, we allow gamepad override.
}

managerLeft.on('move', (evt, data) => handleTouchMove(evt, data, 'left'));
managerLeft.on('end', (evt, data) => handleTouchEnd(evt, data, 'left'));

managerRight.on('move', (evt, data) => handleTouchMove(evt, data, 'right'));
managerRight.on('end', (evt, data) => handleTouchEnd(evt, data, 'right'));


// --- Gamepad Logic ---
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
    return Math.abs(value) < GAMEPAD_DEADZONE ? 0 : value;
}

function updateVisuals(manager, x, y) {
    // x, y are -1 to 1
    // NippleJS Visuals: We need to move the '.front' element relative to center.
    // Max distance is size / 2.
    const maxDist = JOYSTICK_SIZE / 2;
    const posX = x * maxDist;
    const posY = y * maxDist; // Joystick Y up is negative (-1). Translate Y negative is UP. Match signs. 
    // Standard Axes: Y: Up is -1. Down is 1.
    // NippleVisuals: Translate(x, y). Down should be positive Y.
    // So if Axis says 1 (Down), we shift visuals by +Y.
    const frontEl = manager.get(manager.ids[0])?.ui?.front;
    if (frontEl) {
        frontEl.style.transform = `translate(${posX}px, ${posY}px)`;
    }
}

function gamepadLoop() {
    if (gamepadIndex !== null) {
        const gamepads = navigator.getGamepads();
        const gp = gamepads[gamepadIndex];

        if (gp) {
            // Xbox: 
            // Left Stick Y = Axis 1 (Up=-1, Down=1)
            // Right Stick Y = Axis 3 (Up=-1, Down=1)
            // Left Stick X = Axis 0
            // Right Stick X = Axis 2

            // Allow Touch to override Gamepad if active (simple safety)
            // But we don't track start/end perfectly for 'isTouchActive' globally across two managers easily without counters.
            // Let's assume Gamepad always writes, unless touch is actively setting values.
            // Actually, visuals need to be driven by gamepad too.

            // Read Inputs
            // Tank Drive: Left Stick -> Left, Right Stick -> Right
            // Invert Axis 1/3 because normally Up=-1 (we want Up=100 forward)
            const rawLeftY = -applyDeadzone(gp.axes[1]);
            const rawLeftX = applyDeadzone(gp.axes[0]);

            const rawRightY = -applyDeadzone(gp.axes[3]);
            const rawRightX = applyDeadzone(gp.axes[2]);

            // Update Motors
            motorLeft = rawLeftY * 100;
            motorRight = rawRightY * 100;

            // Update Visuals
            // Axis 1 is Y. Up is -1.
            // Visuals need to match stick.
            // Left Stick
            updateVisuals(managerLeft, gp.axes[0], gp.axes[1]);
            updateVisuals(managerRight, gp.axes[2], gp.axes[3]);

            // Update HUD
            updateHud(gp);
        }
        requestAnimationFrame(gamepadLoop);
    }
}

function updateBtn(id, btnObj) {
    const el = document.getElementById(id);
    if (!el) return;
    if (btnObj && btnObj.pressed) el.classList.add('active');
    else el.classList.remove('active');

    // Analog Triggers visual
    if ((id === 'btn_lt' || id === 'btn_rt') && btnObj) {
        el.style.backgroundColor = `rgba(59, 130, 246, ${btnObj.value})`;
    }
}

function updateHud(gp) {
    const b = gp.buttons;
    if (!b) return;

    updateBtn('btn_a', b[0]);
    updateBtn('btn_b', b[1]);
    updateBtn('btn_x', b[2]);
    updateBtn('btn_y', b[3]);

    updateBtn('btn_lb', b[4]);
    updateBtn('btn_rb', b[5]);

    updateBtn('btn_lt', b[6]);
    updateBtn('btn_rt', b[7]);

    updateBtn('btn_select', b[8]);
    updateBtn('btn_start', b[9]);

    updateBtn('btn_up', b[12]);
    updateBtn('btn_down', b[13]);
    updateBtn('btn_left', b[14]);
    updateBtn('btn_right', b[15]);
}
