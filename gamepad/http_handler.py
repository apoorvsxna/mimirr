from http.server import SimpleHTTPRequestHandler
import os

class NoCacheHTTPHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler that prevents caching and serves static files."""
    
    def end_headers(self) -> None:
        """Add no-cache headers to all responses."""
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def log_message(self, format: str, *args) -> None:
        """Suppress default logging."""
        pass

    def translate_path(self, path: str) -> str:
        """Translate URL paths to filesystem paths."""
        # Remove query parameters if any
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        
        # Get the project root directory (one level up from the 'gamepad' package)
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Convert URL path to filesystem path
        if path == '/':
            # Serve index.html for root path
            return os.path.join(root_dir, 'static', 'index.html')
        
        # Remove leading slash and join with static directory
        path = path.lstrip('/')
        if path.startswith('dist/'):
            # Handle dist directory files
            return os.path.join(root_dir, 'static', path)
        return os.path.join(root_dir, 'static', path)

    def do_GET(self):
        """Handle GET requests."""
        try:
            super().do_GET()
        except Exception as e:
            if self.server.config.debug:
                print(f"Error serving {self.path}: {str(e)}")
            self.send_error(404, f"File not found: {self.path}")