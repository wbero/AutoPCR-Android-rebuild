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
except ImportError:
    IS_ANDROID = False

# Ensure directories exist
def ensure_directories():
    """Create necessary directory structure"""
    if IS_ANDROID:
        root_dir = app_storage_path()
    else:
        root_dir = os.path.dirname(os.path.abspath(__file__))
    
    dirs = [
        os.path.join(root_dir, 'cache'),
        os.path.join(root_dir, 'cache', 'db'),
        os.path.join(root_dir, 'cache', 'http_server'),
        os.path.join(root_dir, 'cache', 'token'),
        os.path.join(root_dir, 'result'),
        os.path.join(root_dir, 'log'),
    ]
    
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    
    return root_dir

class ServerThread(threading.Thread):
    """Backend server thread"""
    def __init__(self):
        super().__init__(daemon=True)
        self.running = False
        self.server = None
        
    def run(self):
        """Start Quart server"""
        try:
            import asyncio
            from autopcr.http_server.httpserver import HttpServer
            from autopcr.db.dbstart import db_start
            from autopcr.module.crons import queue_crons
            
            # Create new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Initialize database
            loop.run_until_complete(db_start())
            
            # Setup cron jobs
            queue_crons()
            
            # Create server (listen on localhost only)
            self.server = HttpServer(host='127.0.0.1', port=13200)
            self.running = True
            
            print("[AutoPCR] Server started at http://127.0.0.1:13200")
            
            # Run server
            self.server.run_forever(loop)
            
        except Exception as e:
            print(f"[AutoPCR] Server error: {e}")
            import traceback
            traceback.print_exc()
    
    def stop(self):
        """Stop server"""
        self.running = False

class AutoPCRApp(App):
    """Kivy App Main Class"""
    
    def build(self):
        """Build app UI"""
        # Set window title and size
        self.title = 'AutoPCR'
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        
        # Request Android permissions
        if IS_ANDROID:
            request_permissions([
                Permission.INTERNET,
                Permission.ACCESS_NETWORK_STATE,
            ])
        
        # Ensure directories exist
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
        self.server_thread = ServerThread()
        self.server_thread.start()
        
        # Check server status periodically
        Clock.schedule_interval(self.check_server_status, 1)
        
        return layout
    
    def check_server_status(self, dt):
        """Check server status"""
        import urllib.request
        try:
            urllib.request.urlopen('http://127.0.0.1:13200/daily/', timeout=1)
            self.status_label.text = 'Service Running'
            self.status_label.color = (0.3, 0.8, 0.3, 1)  # Green
            return False  # Stop timer
        except:
            return True  # Continue checking
    
    def open_browser(self, instance):
        """Open browser"""
        try:
            webbrowser.open('http://127.0.0.1:13200/daily/')
        except Exception as e:
            self.status_label.text = f'Failed to open browser: {e}'
    
    def on_stop(self):
        """Cleanup when app stops"""
        if hasattr(self, 'server_thread'):
            self.server_thread.stop()

def main():
    """Main function"""
    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Run Kivy app
    AutoPCRApp().run()

if __name__ == '__main__':
    main()
