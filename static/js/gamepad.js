class GamepadInterface {
    constructor() {
        this.initializeJoysticks();
        this.initializeButtons();
        this.initializeKeyboardControls();
        this.vibrationSupported = 'vibrate' in navigator;
    }

    initializeJoysticks() {
        const options = {
            mode: 'static',
            position: { left: '50%', top: '50%' },
            color: 'white',
            size: 120,
            restOpacity: 0.5,
            lockX: false,
            lockY: false
        };

        const leftJoystick = nipplejs.create({ 
            ...options, 
            zone: document.getElementById('left-joystick')
        });

        const rightJoystick = nipplejs.create({ 
            ...options, 
            zone: document.getElementById('right-joystick')
        });

        this.setupJoystickEvents(leftJoystick, 'vjl');
        this.setupJoystickEvents(rightJoystick, 'vjr');
    }

    setupJoystickEvents(joystick, side) {
        let lastUpdate = 0;
        const updateThreshold = 1000 / 60; // 60fps limit

        joystick.on('move', (evt, data) => {
            const now = Date.now();
            if (now - lastUpdate < updateThreshold) return;
            lastUpdate = now;

            if (data?.instance?.frontPosition) {
                // Map joystick coordinates to XInput values (0-65535)
                const x = Math.round(((data.instance.frontPosition.x + 50) / 100) * 65535);
                const y = Math.round(((50 - data.instance.frontPosition.y) / 100) * 65535);
                
                window.wsManager.sendCommand(`${side} ${x}|${y}`);
            }
        });

        joystick.on('end', () => {
            window.wsManager.sendCommand(`${side} 32767|32767`);
        });
    }

    initializeButtons() {
        const buttons = {
            'button-a': 'xusb_gamepad_a',
            'button-b': 'xusb_gamepad_b',
            'button-x': 'xusb_gamepad_x',
            'button-y': 'xusb_gamepad_y',
            'dpad-up': 'xusb_gamepad_dpad_up',
            'dpad-down': 'xusb_gamepad_dpad_down',
            'dpad-left': 'xusb_gamepad_dpad_left',
            'dpad-right': 'xusb_gamepad_dpad_right'
        };

        for (const [id, command] of Object.entries(buttons)) {
            const button = document.getElementById(id);
            if (button) {
                ['touchstart', 'mousedown'].forEach(event => {
                    button.addEventListener(event, (e) => {
                        e.preventDefault();
                        window.wsManager.sendCommand(`p ${command}`);
                        if (this.vibrationSupported) {
                            navigator.vibrate(20);
                        }
                    });
                });

                ['touchend', 'mouseup', 'mouseleave'].forEach(event => {
                    button.addEventListener(event, (e) => {
                        e.preventDefault();
                        window.wsManager.sendCommand(`r ${command}`);
                    });
                });
            }
        }
    }

    initializeKeyboardControls() {
        const keyMap = {
            'ArrowUp': 'xusb_gamepad_dpad_up',
            'ArrowDown': 'xusb_gamepad_dpad_down',
            'ArrowLeft': 'xusb_gamepad_dpad_left',
            'ArrowRight': 'xusb_gamepad_dpad_right',
            'x': 'xusb_gamepad_x',
            'z': 'xusb_gamepad_a',
            's': 'xusb_gamepad_b',
            'a': 'xusb_gamepad_y'
        };

        document.addEventListener('keydown', (e) => {
            const command = keyMap[e.key];
            if (command) {
                e.preventDefault();
                window.wsManager.sendCommand(`p ${command}`);
            }
        });

        document.addEventListener('keyup', (e) => {
            const command = keyMap[e.key];
            if (command) {
                e.preventDefault();
                window.wsManager.sendCommand(`r ${command}`);
            }
        });
    }
}

// Initialize the gamepad interface when the page loads
window.addEventListener('load', () => {
    new GamepadInterface();
});