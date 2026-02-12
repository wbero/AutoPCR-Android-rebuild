#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoPCR Android 后台服务
作为前台服务运行，保持后端服务器持续运行
"""

import os
import sys

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def main():
    """服务主函数"""
    import asyncio
    from autopcr.http_server.httpserver import HttpServer
    from autopcr.db.dbstart import db_start
    from autopcr.module.crons import queue_crons
    
    print("[AutoPCR Service] 启动后台服务...")
    
    # 创建事件循环
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # 初始化数据库
        loop.run_until_complete(db_start())
        
        # 设置定时任务
        queue_crons()
        
        # 创建服务器
        server = HttpServer(host='127.0.0.1', port=13200)
        
        print("[AutoPCR Service] 服务器启动在 http://127.0.0.1:13200")
        
        # 运行服务器
        server.run_forever(loop)
        
    except Exception as e:
        print(f"[AutoPCR Service] 服务错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
