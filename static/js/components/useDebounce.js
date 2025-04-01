import { useCallback, useRef } from 'react';

const useDebounce = (callback, delay = 100) => {
  const timeoutRef = useRef(null);
  const lastPressTime = useRef(0);

  return useCallback((...args) => {
    const now = Date.now();
    
    // If it's been less than the delay since the last press, ignore this press
    if (now - lastPressTime.current < delay) {
      return;
    }

    lastPressTime.current = now;
    
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    
    timeoutRef.current = setTimeout(() => {
      callback(...args);
      timeoutRef.current = null;
    }, 0);
  }, [callback, delay]);
};

export default useDebounce;