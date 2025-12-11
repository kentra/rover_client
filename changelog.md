# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [111225] - 2025-12-11

### Added
- **Web Interface**: Added a responsive web controller with virtual joystick (`src/app/static/index.html`).
- **Gamepad Support**: Added support for Xbox-style gamepads with visual feedback.
    - **Dual Joystick**: UI now features two on-screen joysticks for Tank Drive.
    - **Visual Sync**: Moving the physical gamepad sticks moves the virtual joysticks in real-time.
- **Remote Control**: Integrated legacy `remote_control.html` at `/remote` endpoint for button-based control.
- **WebSocket Control**: implemented real-time track control via WebSocket in `web_socket.py`.
- **REST Control**: Added REST endpoints (`/move/{direction}`) in `movement.py` to support button-based remotes.
- **Mock Sensors**: Added mock implementation for `EnvironmentSensors` (`smbus` and `bme280`) to allow development on macOS.

### Changed
- **BLE Connection**: Refactored `HubControl` to maintain a persistent BLE connection instead of reconnecting on every command.
- **Configuration**: Updated configuration handling to match `AppConfig` variable names (e.g., `BLE_DEADZONE`).
- **Dependencies**: Added `bleak` for Bluetooth support. Removed `smbus` from `pyproject.toml` to fix build errors on macOS.
- **Main App**: Updated `main.py` lifespan events to handle auto-connection/disconnection of the BLE rover.
