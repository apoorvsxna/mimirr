import React, { useState, useEffect } from 'react';
import Joystick from './Joystick';
import DPad from './DPad';
import ActionButton from './ActionButton';
import SystemButton from './SystemButton';
import useFullscreen from './useFullscreen';

const defaultLayout = {
  dpad: {
    position: { x: "30%", y: "60%" }
  },
  buttons: [
    {
      type: "XUSB_GAMEPAD_A",
      position: { x: "75%", y: "63%" },
      label: "A"
    },
    {
      type: "XUSB_GAMEPAD_B",
      position: { x: "79%", y: "59%" },
      label: "B"
    },
    {
      type: "XUSB_GAMEPAD_X",
      position: { x: "71%", y: "59%" },
      label: "X"
    },
    {
      type: "XUSB_GAMEPAD_Y",
      position: { x: "75%", y: "55%" },
      label: "Y"
    },
    {
      type: "XUSB_GAMEPAD_START",
      position: { x: "55%", y: "35%" },
      label: "Menu"
    },
    {
      type: "XUSB_GAMEPAD_BACK",
      position: { x: "45%", y: "35%" },
      label: "View"
    }
  ],
  joysticks: [
    {
      type: "LEFT_THUMB",
      position: { x: "30%", y: "35%" }
    },
    {
      type: "RIGHT_THUMB",
      position: { x: "70%", y: "70%" }
    }
  ]
};

const DynamicGamepad = () => {
  const [layout, setLayout] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const { showPrompt, enterFullscreen } = useFullscreen();

  useEffect(() => {
    // In the future, this could load from a JSON file
    setLayout(defaultLayout);
    
    // Initialize WebSocket manager if it doesn't exist globally
    if (!window.wsManager) {
      window.wsManager = new WebSocketManager();
    }

    // Set up WebSocket connection status listeners
    const handleOpen = () => {
      setIsConnected(true);
    };

    const handleClose = () => {
      setIsConnected(false);
    };

    window.wsManager.ws.addEventListener('open', handleOpen);
    window.wsManager.ws.addEventListener('close', handleClose);

    // Set initial connection status
    setIsConnected(window.wsManager.ws.readyState === WebSocket.OPEN);

    return () => {
      window.wsManager.ws.removeEventListener('open', handleOpen);
      window.wsManager.ws.removeEventListener('close', handleClose);
    };
  }, []);

  if (!layout) return null;

  return (
    <div className="gamepad-container">
      <div 
        id="connection-status" 
        className={isConnected ? 'connected' : 'disconnected'}
      >
        {isConnected ? 'Connected' : 'Disconnected'}
      </div>

      {showPrompt && (
        <div 
          id="fullscreen-prompt"
          onClick={enterFullscreen}
        >
          <p>Tap to enter fullscreen</p>
        </div>
      )}

      {/* Render D-pad */}
      <DPad position={layout.dpad.position} />

      {/* Render action buttons */}
      {layout.buttons.map((button, index) => {
        if (button.type.includes('GAMEPAD_A') || 
            button.type.includes('GAMEPAD_B') || 
            button.type.includes('GAMEPAD_X') || 
            button.type.includes('GAMEPAD_Y')) {
          return <ActionButton key={index} {...button} />;
        }
        return <SystemButton key={index} {...button} />;
      })}

      {/* Render joysticks */}
      {layout.joysticks.map((joystick, index) => (
        <Joystick key={index} {...joystick} />
      ))}
    </div>
  );
};

export default DynamicGamepad;