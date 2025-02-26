import React, { useCallback } from 'react';
import useDebounce from './useDebounce';

const ActionButton = ({ type, position, label }) => {
  const buttonId = `button-${type.toLowerCase().split('_').pop()}`;
  
  const handleButtonPress = useDebounce(() => {
    window.wsManager?.sendCommand(`p ${type}`);
  }, 150);

  const handleButtonRelease = useCallback(() => {
    window.wsManager?.sendCommand(`r ${type}`);
  }, [type]);

  return (
    <button
      id={buttonId}
      className="action-button"
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

export default ActionButton;