// Handle fullscreen functionality
document.addEventListener('DOMContentLoaded', () => {
    const fullscreenPrompt = document.getElementById('fullscreen-prompt');
    const container = document.querySelector('.container');

    function enterFullscreen() {
        if (document.documentElement.requestFullscreen) {
            document.documentElement.requestFullscreen();
        } else if (document.documentElement.webkitRequestFullscreen) {
            document.documentElement.webkitRequestFullscreen();
        }
        fullscreenPrompt.style.display = 'none';
        
        // Force screen orientation to landscape if supported
        if (screen.orientation && screen.orientation.lock) {
            screen.orientation.lock('landscape').catch(err => console.warn('Orientation lock failed:', err));
        }
    }

    function handleResize() {
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
        
        // Adjust joystick size based on screen dimensions
        const joystickZones = document.querySelectorAll('.joystick-zone');
        const minDimension = Math.min(window.innerWidth * 0.3, window.innerHeight * 0.4);
        joystickZones.forEach(zone => {
            zone.style.width = `${minDimension}px`;
            zone.style.height = `${minDimension}px`;
        });
    }

    fullscreenPrompt.addEventListener('click', enterFullscreen);
    window.addEventListener('resize', handleResize);
    handleResize(); // Initial call
});