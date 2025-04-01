import { useState, useEffect } from 'react';

const useFullscreen = () => {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showPrompt, setShowPrompt] = useState(true);

  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement || !!document.webkitFullscreenElement);
      if (document.fullscreenElement || document.webkitFullscreenElement) {
        setShowPrompt(false);
      }
    };

    const handleResize = () => {
      const vh = window.innerHeight * 0.01;
      document.documentElement.style.setProperty('--vh', `${vh}px`);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
    window.addEventListener('resize', handleResize);
    handleResize(); // Initial call

    // Cleanup
    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
      document.removeEventListener('webkitfullscreenchange', handleFullscreenChange);
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  const enterFullscreen = async () => {
    try {
      if (document.documentElement.requestFullscreen) {
        await document.documentElement.requestFullscreen();
      } else if (document.documentElement.webkitRequestFullscreen) {
        await document.documentElement.webkitRequestFullscreen();
      }
      
      // Force screen orientation to landscape if supported
      if (screen.orientation && screen.orientation.lock) {
        try {
          await screen.orientation.lock('landscape');
        } catch (err) {
          console.warn('Orientation lock failed:', err);
        }
      }
      
      setIsFullscreen(true);
      setShowPrompt(false);
    } catch (error) {
      console.error('Error entering fullscreen:', error);
    }
  };

  return {
    isFullscreen,
    showPrompt,
    enterFullscreen
  };
};

export default useFullscreen;