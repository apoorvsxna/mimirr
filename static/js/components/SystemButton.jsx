import React, { useCallback } from 'react';
import useDebounce from './useDebounce';

const SystemButton = ({ type, position, label }) => {
  const handleButtonPress = useDebounce(() => {
    window.wsManager?.sendCommand(`p ${type}`);
  }, 150);

  const handleButtonRelease = useCallback(() => {
    window.wsManager?.sendCommand(`r ${type}`);
  }, [type]);

  return (
    <button
      className="system-button"
      style={{
        position: 'absolute',
        left: position.x,
        top: position.y,
        transform: 'translate(-50%, -50%)'
      }}
      onTouchStart={handleButtonPress}
      onTouchEnd={handleButtonRelease}
      onMouseDown={handleButtonPress}
      onMouseUp={handleButtonRelease}
    >
      {label}
    </button>
  );
};

export default SystemButton;