import React, { useEffect, useRef } from 'react';

const Joystick = ({ type, position }) => {
  const joystickRef = useRef(null);
  const joystickInstanceRef = useRef(null);
  const joystickId = `${type.toLowerCase()}-joystick`;

  useEffect(() => {
    if (joystickRef.current && window.nipplejs) {
      const options = {
        mode: 'static',
        position: { left: '50%', top: '50%' },
        color: 'white',
        size: 120,
        restOpacity: 0.5,
        lockX: false,
        lockY: false,
        zone: joystickRef.current
      };

      joystickInstanceRef.current = window.nipplejs.create(options);

      // Setup joystick events
      let lastUpdate = 0;
      const updateThreshold = 1000 / 60; // 60fps limit

      joystickInstanceRef.current.on('move', (evt, data) => {
        const now = Date.now();
        if (now - lastUpdate < updateThreshold) return;
        lastUpdate = now;

        if (data?.instance?.frontPosition) {
          const x = Math.round(((data.instance.frontPosition.x + 50) / 100) * 65535);
          const y = Math.round(((50 - data.instance.frontPosition.y) / 100) * 65535);
          
          const command = type === 'LEFT_THUMB' ? 'vjl' : 'vjr';
          window.wsManager?.sendCommand(`${command} ${x}|${y}`);
        }
      });

      joystickInstanceRef.current.on('end', () => {
        const command = type === 'LEFT_THUMB' ? 'vjl' : 'vjr';
        window.wsManager?.sendCommand(`${command} 32767|32767`);
      });
    }

    return () => {
      if (joystickInstanceRef.current) {
        joystickInstanceRef.current.destroy();
      }
    };
  }, [type]);

  return (
    <div 
      ref={joystickRef}
      id={joystickId}
      className="joystick-zone"
      style={{
        position: 'absolute',
        left: position.x,
        top: position.y,
        transform: 'translate(-50%, -50%)'
      }}
    />
  );
};

export default Joystick;