import sys
import os
import socket
import threading
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView

# Helper to find an available local port
def find_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port

# Quiet HTTP server handler to suppress console logs
class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

# Background HTTP server thread worker
def start_local_server(port, root_dir):
    class CustomDirHandler(QuietHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=root_dir, **kwargs)
            
    # Allow port re-use to prevent bind errors on restarts
    TCPServer.allow_reuse_address = True
    server = TCPServer(('127.0.0.1', port), CustomDirHandler)
    
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    return server

class MainWindow(QMainWindow):
    def __init__(self, port):
        super().__init__()
        self.setWindowTitle("SciMath Visual Studio - Desktop Console")
        self.resize(1280, 820)
        self.setMinimumSize(960, 640)
        
        # Setup WebEngine view
        self.browser = QWebEngineView(self)
        self.setCentralWidget(self.browser)
        
        # Load local webapp served from background server
        self.browser.load(QUrl(f"http://127.0.0.1:{port}/index.html"))

def main():
    # Resolve the client assets source path (handles PyInstaller bundle temp dir _MEIPASS)
    if hasattr(sys, '_MEIPASS'):
        base_dir = os.path.join(sys._MEIPASS, 'src')
    else:
        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
        
    if not os.path.exists(base_dir):
        print(f"Error: Client directory not found at: {base_dir}")
        sys.exit(1)
        
    port = find_free_port()
    
    # Fire up quiet assets server on local thread
    server = start_local_server(port, base_dir)
    print(f"SciMath local engine background server started on port {port}.")
    
    # Enable High DPI scaling for crisp rendering on high-res displays
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Launch Qt application main frame loop
    app = QApplication(sys.argv)
    window = MainWindow(port)
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
