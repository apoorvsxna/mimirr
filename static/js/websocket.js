class WebSocketManager {
    constructor() {
        this.ws = null;
        this.pingInterval = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.playerNumber = this.getPlayerNumber();
        this.connect();
    }

    getPlayerNumber() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('player') || '0';
    }

    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.hostname}:8000`;
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            console.log('Connected to server');
            document.getElementById('connection-status').className = 'connected';
            document.getElementById('connection-status').textContent = 'Connected';
            this.startPing();
            this.reconnectAttempts = 0;
        };

        this.ws.onclose = () => {
            console.log('Disconnected from server');
            document.getElementById('connection-status').className = 'disconnected';
            document.getElementById('connection-status').textContent = 'Disconnected';
            this.stopPing();
            
            if (this.reconnectAttempts < this.maxReconnectAttempts) {
                setTimeout(() => {
                    this.reconnectAttempts++;
                    this.connect();
                }, this.reconnectDelay * Math.pow(2, this.reconnectAttempts));
            }
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    startPing() {
        this.pingInterval = setInterval(() => {
            if (this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(`ping ${Date.now()}`);
            }
        }, 5000);
    }

    stopPing() {
        if (this.pingInterval) {
            clearInterval(this.pingInterval);
            this.pingInterval = null;
        }
    }

    sendCommand(command) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(`${command} ${this.playerNumber}`);
        }
    }
}

// Export for use in other modules
window.wsManager = new WebSocketManager();