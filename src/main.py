#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoPCR Android 主入口
整合Python后端服务和WebView前端
"""

import os
import sys
import time
import threading
import webbrowser

# 设置Kivy环境
os.environ['KIVY_NO_CONSOLELOG'] = '1'
os.environ['KIVY_WINDOW'] = 'sdl2'

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import StringProperty

# 导入Android相关库
try:
    from android.permissions import request_permissions, Permission
    from android.storage import app_storage_path
    IS_ANDROID = True
except ImportError:
    IS_ANDROID = False

# 确保目录存在
def ensure_directories():
    """创建必要的目录结构"""
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
    """后台服务器线程"""
    def __init__(self):
        super().__init__(daemon=True)
        self.running = False
        self.server = None
        
    def run(self):
        """启动Quart服务器"""
        try:
            import asyncio
            from autopcr.http_server.httpserver import HttpServer
            from autopcr.db.dbstart import db_start
            from autopcr.module.crons import queue_crons
            
            # 创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 初始化数据库
            loop.run_until_complete(db_start())
            
            # 设置定时任务
            queue_crons()
            
            # 创建服务器 (只监听本地)
            self.server = HttpServer(host='127.0.0.1', port=13200)
            self.running = True
            
            print("[AutoPCR] 服务器启动在 http://127.0.0.1:13200")
            
            # 运行服务器
            self.server.run_forever(loop)
            
        except Exception as e:
            print(f"[AutoPCR] 服务器错误: {e}")
            import traceback
            traceback.print_exc()
    
    def stop(self):
        """停止服务器"""
        self.running = False

class WebViewWidget(BoxLayout):
    """WebView容器"""
    status_text = StringProperty("正在启动服务...")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        
        # 状态标签
        self.status_label = Label(
            text=self.status_text,
            size_hint_y=None,
            height='40dp',
            font_size='16sp'
        )
        self.add_widget(self.status_label)
        
        # WebView将在服务器启动后加载
        Clock.schedule_once(self.check_server, 1)
    
    def check_server(self, dt):
        """检查服务器是否启动"""
        # 尝试连接服务器
        import urllib.request
        try:
            urllib.request.urlopen('http://127.0.0.1:13200/daily/', timeout=2)
            self.status_text = "服务已启动"
            self.status_label.text = self.status_text
            self.load_webview()
        except:
            # 继续等待
            Clock.schedule_once(self.check_server, 1)
    
    def load_webview(self):
        """加载WebView"""
        try:
            # 尝试使用系统浏览器或内置WebView
            if IS_ANDROID:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                
                intent = Intent(Intent.ACTION_VIEW)
                intent.setData(Uri.parse('http://127.0.0.1:13200/daily/'))
                PythonActivity.mActivity.startActivity(intent)
            else:
                # 桌面环境使用系统浏览器
                webbrowser.open('http://127.0.0.1:13200/daily/')
                
        except Exception as e:
            print(f"[AutoPCR] WebView加载失败: {e}")
            self.status_text = f"请手动访问: http://127.0.0.1:13200/daily/"
            self.status_label.text = self.status_text

class AutoPCRApp(App):
    """Kivy应用主类"""
    
    def build(self):
        """构建应用界面"""
        # 设置窗口标题和大小
        self.title = 'AutoPCR'
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        
        # 请求Android权限
        if IS_ANDROID:
            request_permissions([
                Permission.INTERNET,
                Permission.ACCESS_NETWORK_STATE,
            ])
        
        # 确保目录存在
        ensure_directories()
        
        # 创建主布局
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # 标题
        title_label = Label(
            text='AutoPCR 自动清日常',
            font_size='24sp',
            size_hint_y=None,
            height='60dp'
        )
        layout.add_widget(title_label)
        
        # 状态信息
        self.status_label = Label(
            text='正在启动后端服务...',
            font_size='16sp',
            size_hint_y=None,
            height='40dp'
        )
        layout.add_widget(self.status_label)
        
        # 打开浏览器按钮
        open_btn = Button(
            text='打开网页界面',
            size_hint_y=None,
            height='50dp',
            font_size='18sp'
        )
        open_btn.bind(on_press=self.open_browser)
        layout.add_widget(open_btn)
        
        # 说明标签
        info_label = Label(
            text='服务启动后，点击上方按钮访问管理界面\n或手动访问: http://127.0.0.1:13200/daily/',
            font_size='14sp'
        )
        layout.add_widget(info_label)
        
        # 启动服务器
        self.server_thread = ServerThread()
        self.server_thread.start()
        
        # 定时检查服务器状态
        Clock.schedule_interval(self.check_server_status, 1)
        
        return layout
    
    def check_server_status(self, dt):
        """检查服务器状态"""
        import urllib.request
        try:
            urllib.request.urlopen('http://127.0.0.1:13200/daily/', timeout=1)
            self.status_label.text = '✓ 服务运行正常'
            self.status_label.color = (0.3, 0.8, 0.3, 1)  # 绿色
            return False  # 停止定时器
        except:
            return True  # 继续检查
    
    def open_browser(self, instance):
        """打开浏览器"""
        try:
            webbrowser.open('http://127.0.0.1:13200/daily/')
        except Exception as e:
            self.status_label.text = f'打开浏览器失败: {e}'
    
    def on_stop(self):
        """应用停止时清理"""
        if hasattr(self, 'server_thread'):
            self.server_thread.stop()

def main():
    """主函数"""
    # 添加当前目录到Python路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # 运行Kivy应用
    AutoPCRApp().run()

if __name__ == '__main__':
    main()
