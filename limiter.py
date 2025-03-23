from functools import wraps
from flask import request, jsonify
import time
from collections import defaultdict

# 使用字典存储请求记录
request_records = defaultdict(list)

def cleanup_old_records(ip, window):
    """清理过期的请求记录"""
    current = time.time()
    request_records[ip] = [timestamp for timestamp in request_records[ip] 
                          if current - timestamp < window]

def rate_limit(limit=2, window=60):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 获取客户端IP地址
            ip = request.remote_addr
            
            # 清理过期记录
            cleanup_old_records(ip, window)
            
            # 获取当前IP的请求次数
            request_count = len(request_records[ip])
            
            if request_count < limit:
                # 添加新的请求记录
                current = time.time()
                request_records[ip].append(current)
                return f(*args, **kwargs)
            else:
                return jsonify({
                    'error': '请求过于频繁，请稍后再试',
                    'retry_after': window
                }), 429
                
        return decorated_function
    return decorator