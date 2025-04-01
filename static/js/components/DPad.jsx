import React, { useCallback } from 'react';
import useDebounce from './useDebounce';

const DPad = ({ position }) => {
  const handleButtonPress = useDebounce((direction) => {
    window.wsManager?.sendCommand(`p XUSB_GAMEPAD_DPAD_${direction}`);
  }, 150);

  const handleButtonRelease = useCallback((direction) => {
    window.wsManager?.sendCommand(`r XUSB_GAMEPAD_DPAD_${direction}`);
  }, []);

  return (
    <div className="dpad" style={{
      position: 'absolute',
      left: position.x,
      top: position.y,
      transform: 'translate(-50%, -50%)'
    }}>
      <button></button>
      <button 
        id="dpad-up" 
        onTouchStart={() => handleButtonPress('UP')}
        onTouchEnd={() => handleButtonRelease('UP')}
        onMouseDown={() => handleButtonPress('UP')}
        onMouseUp={() => handleButtonRelease('UP')}
      >↑</button>
      <button></button>
      <button 
        id="dpad-left"
        onTouchStart={() => handleButtonPress('LEFT')}
        onTouchEnd={() => handleButtonRelease('LEFT')}
        onMouseDown={() => handleButtonPress('LEFT')}
        onMouseUp={() => handleButtonRelease('LEFT')}
      >←</button>
      <button></button>
      <button 
        id="dpad-right"
        onTouchStart={() => handleButtonPress('RIGHT')}
        onTouchEnd={() => handleButtonRelease('RIGHT')}
        onMouseDown={() => handleButtonPress('RIGHT')}
        onMouseUp={() => handleButtonRelease('RIGHT')}
      >→</button>
      <button></button>
      <button 
        id="dpad-down"
        onTouchStart={() => handleButtonPress('DOWN')}
        onTouchEnd={() => handleButtonRelease('DOWN')}
        onMouseDown={() => handleButtonPress('DOWN')}
        onMouseUp={() => handleButtonRelease('DOWN')}
      >↓</button>
      <button></button>
    </div>
  );
};

export default DPad;