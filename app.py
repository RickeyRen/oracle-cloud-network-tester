#!/usr/bin/env python3
"""Oracle Cloud VPS 网络测试工具 - 主应用"""

import asyncio
import json
import threading
import logging
from flask import Flask, render_template, jsonify
from flask_cors import CORS

from src import (
    ORACLE_SERVERS, 
    FLASK_CONFIG,
    NetworkTester,
    get_public_ip
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)

# 全局变量
tester = NetworkTester()
test_results = {}
test_thread = None


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/ip')
def get_ip():
    """获取公网IP"""
    try:
        ip_info = get_public_ip()
        return jsonify(ip_info)
    except Exception as e:
        logger.error(f"Error getting IP: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/servers')
def get_servers():
    """获取服务器列表"""
    return jsonify(ORACLE_SERVERS)


@app.route('/api/test/start', methods=['POST'])
def start_test():
    """开始测试"""
    global test_thread, test_results
    
    if tester.is_testing:
        return jsonify({"error": "测试正在进行中"}), 400
    
    # 清空之前的结果
    test_results = {}
    
    # 在新线程中启动测试
    test_thread = threading.Thread(target=run_async_test, daemon=True)
    test_thread.start()
    
    return jsonify({"message": "测试已开始", "total": len(ORACLE_SERVERS)})


@app.route('/api/test/status')
def get_test_status():
    """获取测试状态"""
    status = tester.get_status()
    status["results"] = list(test_results.values())
    return jsonify(status)


@app.route('/api/test/results')
def get_test_results():
    """获取测试结果"""
    results = list(test_results.values())
    # 按评分排序
    results.sort(key=lambda x: x.get('score', 0), reverse=True)
    return jsonify(results)


def update_result(result):
    """更新单个测试结果"""
    test_results[result['name']] = result


def run_async_test():
    """在独立线程中运行异步测试"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # 运行测试
        results = loop.run_until_complete(
            tester.test_all_servers(ORACLE_SERVERS, update_result)
        )
        
        logger.info(f"测试完成，共测试 {len(results)} 个服务器")
        
    except Exception as e:
        logger.error(f"测试过程出错: {e}")
    finally:
        loop.close()


if __name__ == '__main__':
    logger.info("Starting Oracle Network Test Server...")
    logger.info(f"Server will run on http://localhost:{FLASK_CONFIG['port']}")
    
    app.run(
        host=FLASK_CONFIG['host'],
        port=FLASK_CONFIG['port'],
        debug=FLASK_CONFIG['debug'],
        threaded=FLASK_CONFIG['threaded']
    )