#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoPCR Android Main Entry
Integrates Python backend service and WebView frontend
"""

import os
import sys
import time
import threading
import webbrowser
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger('AutoPCR')

# Set Kivy environment
os.environ['KIVY_NO_CONSOLELOG'] = '1'
os.environ['KIVY_WINDOW'] = 'sdl2'

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import StringProperty

# Import Android libraries
try:
    from android.permissions import request_permissions, Permission
    from android.storage import app_storage_path
    IS_ANDROID = True
    logger.info("Running on Android")
except ImportError:
    IS_ANDROID = False
    logger.info("Running on Desktop")

# Ensure directories exist
def ensure_directories():
    """Create necessary directory structure"""
    if IS_ANDROID:
        root_dir = app_storage_path()
    else:
        root_dir = os.path.dirname(os.path.abspath(__file__))
    
    logger.info(f"Root directory: {root_dir}")
    
    dirs = [
        os.path.join(root_dir, 'cache'),
        os.path.join(root_dir, 'cache', 'db'),
        os.path.join(root_dir, 'cache', 'http_server'),
        os.path.join(root_dir, 'cache', 'token'),
        os.path.join(root_dir, 'result'),
        os.path.join(root_dir, 'log'),
    ]
    
    for d in dirs:
        try:
            os.makedirs(d, exist_ok=True)
            logger.info(f"Created directory: {d}")
        except Exception as e:
            logger.error(f"Failed to create directory {d}: {e}")
    
    return root_dir

class ServerThread(threading.Thread):
    """Backend server thread"""
    def __init__(self, status_callback=None):
        super().__init__(daemon=True)
        self.running = False
        self.server = None
        self.status_callback = status_callback
        self.error_msg = None
        
    def run(self):
        """Start Quart server"""
        logger.info("Server thread started")
        try:
            import asyncio
            logger.info("Imported asyncio")
            
            from autopcr.http_server.httpserver import HttpServer
            logger.info("Imported HttpServer")
            
            from autopcr.db.dbstart import db_start
            logger.info("Imported db_start")
            
            from autopcr.module.crons import queue_crons
            logger.info("Imported queue_crons")
            
            # Create new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            logger.info("Created event loop")
            
            # Initialize database
            logger.info("Initializing database...")
            loop.run_until_complete(db_start())
            logger.info("Database initialized")
            
            # Setup cron jobs
            logger.info("Setting up cron jobs...")
            queue_crons()
            logger.info("Cron jobs setup complete")
            
            # Create server (listen on localhost only)
            logger.info("Creating HTTP server...")
            self.server = HttpServer(host='127.0.0.1', port=13200)
            self.running = True
            
            logger.info("Server started at http://127.0.0.1:13200")
            if self.status_callback:
                Clock.schedule_once(lambda dt: self.status_callback("Server Started"), 0)
            
            # Run server
            self.server.run_forever(loop)
            
        except Exception as e:
            self.error_msg = str(e)
            logger.error(f"Server error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            if self.status_callback:
                Clock.schedule_once(lambda dt: self.status_callback(f"Error: {e}"), 0)
    
    def stop(self):
        """Stop server"""
        self.running = False

class AutoPCRApp(App):
    """Kivy App Main Class"""
    
    def build(self):
        """Build app UI"""
        logger.info("Building app UI...")
        
        # Set window title and size
        self.title = 'AutoPCR'
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        
        # Request Android permissions
        if IS_ANDROID:
            logger.info("Requesting Android permissions...")
            try:
                request_permissions([
                    Permission.INTERNET,
                    Permission.ACCESS_NETWORK_STATE,
                ])
                logger.info("Permissions requested")
            except Exception as e:
                logger.error(f"Failed to request permissions: {e}")
        
        # Ensure directories exist
        logger.info("Ensuring directories...")
        ensure_directories()
        
        # Create main layout
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Title
        title_label = Label(
            text='AutoPCR',
            font_size='24sp',
            size_hint_y=None,
            height='60dp'
        )
        layout.add_widget(title_label)
        
        # Status info
        self.status_label = Label(
            text='Starting backend service...',
            font_size='16sp',
            size_hint_y=None,
            height='40dp'
        )
        layout.add_widget(self.status_label)
        
        # Open browser button
        open_btn = Button(
            text='Open Web Interface',
            size_hint_y=None,
            height='50dp',
            font_size='18sp'
        )
        open_btn.bind(on_press=self.open_browser)
        layout.add_widget(open_btn)
        
        # Info label
        info_label = Label(
            text='After service starts, click button above\nor visit: http://127.0.0.1:13200/daily/',
            font_size='14sp'
        )
        layout.add_widget(info_label)
        
        # Start server
        logger.info("Starting server thread...")
        self.server_thread = ServerThread(status_callback=self.update_status)
        self.server_thread.start()
        
        # Check server status periodically
        Clock.schedule_interval(self.check_server_status, 2)
        
        return layout
    
    def update_status(self, msg):
        """Update status label"""
        self.status_label.text = msg
    
    def check_server_status(self, dt):
        """Check server status"""
        import urllib.request
        try:
            urllib.request.urlopen('http://127.0.0.1:13200/daily/', timeout=1)
            self.status_label.text = 'Service Running'
            self.status_label.color = (0.3, 0.8, 0.3, 1)  # Green
            logger.info("Service is running")
            return False  # Stop timer
        except Exception as e:
            if self.server_thread.error_msg:
                self.status_label.text = f'Error: {self.server_thread.error_msg[:50]}'
                self.status_label.color = (0.8, 0.3, 0.3, 1)  # Red
                logger.error(f"Service error: {self.server_thread.error_msg}")
                return False  # Stop timer
            logger.debug(f"Service not ready yet: {e}")
            return True  # Continue checking
    
    def open_browser(self, instance):
        """Open browser"""
        logger.info("Opening browser...")
        try:
            webbrowser.open('http://127.0.0.1:13200/daily/')
        except Exception as e:
            logger.error(f"Failed to open browser: {e}")
            self.status_label.text = f'Failed to open browser: {e}'
    
    def on_stop(self):
        """Cleanup when app stops"""
        logger.info("App stopping...")
        if hasattr(self, 'server_thread'):
            self.server_thread.stop()

def main():
    """Main function"""
    logger.info("AutoPCR starting...")
    
    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    logger.info(f"Python path: {sys.path}")
    logger.info(f"Current directory: {current_dir}")
    
    # Run Kivy app
    AutoPCRApp().run()

if __name__ == '__main__':
    main()
