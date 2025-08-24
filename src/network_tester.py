"""网络测试核心模块"""

import asyncio
import aiohttp
import subprocess
import platform
import re
import statistics
import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from .config import TEST_CONFIG, SCORE_WEIGHTS

logger = logging.getLogger(__name__)


class NetworkTester:
    """网络测试核心类"""
    
    def __init__(self):
        self.test_results: Dict[str, Any] = {}
        self.test_progress: int = 0
        self.total_servers: int = 0
        self.is_testing: bool = False
        self.executor = ThreadPoolExecutor(max_workers=TEST_CONFIG["max_workers"])
        
    def ping_host(self, host: str, count: int = None, timeout: int = None) -> Dict[str, Any]:
        """执行ping测试"""
        count = count or TEST_CONFIG["ping_count"]
        timeout = timeout or TEST_CONFIG["ping_timeout"]
        
        system = platform.system().lower()
        
        if system == "windows":
            cmd = ["ping", "-n", str(count), "-w", str(timeout * 1000), host]
        elif system == "darwin":
            cmd = ["ping", "-c", str(count), "-W", str(timeout * 1000), host]
        else:
            cmd = ["ping", "-c", str(count), "-W", str(timeout), host]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout * count + 5
            )
            
            output = result.stdout
            
            # 解析ping结果
            latencies = []
            
            # macOS/Linux统计行格式
            stats_pattern = r'round-trip min/avg/max/stddev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)'
            stats_match = re.search(stats_pattern, output)
            
            if stats_match:
                min_lat = float(stats_match.group(1))
                avg_lat = float(stats_match.group(2))
                max_lat = float(stats_match.group(3))
                stddev = float(stats_match.group(4))
                
                # 生成模拟的延迟列表用于计算
                latencies = [avg_lat] * count
                
                return {
                    "min": min_lat,
                    "avg": avg_lat,
                    "max": max_lat,
                    "jitter": stddev,
                    "packet_loss": self._parse_packet_loss(output),
                    "success": True
                }
            
            # Windows格式或单个响应解析
            time_pattern = r'(?:time=|时间=)([\d.]+)\s*ms'
            time_matches = re.findall(time_pattern, output)
            
            if time_matches:
                latencies = [float(t) for t in time_matches]
                
                if latencies:
                    return {
                        "min": min(latencies),
                        "avg": statistics.mean(latencies),
                        "max": max(latencies),
                        "jitter": statistics.stdev(latencies) if len(latencies) > 1 else 0,
                        "packet_loss": self._parse_packet_loss(output),
                        "success": True
                    }
            
            # 如果没有解析到延迟，检查是否全部丢包
            packet_loss = self._parse_packet_loss(output)
            if packet_loss == 100:
                return {
                    "min": 999,
                    "avg": 999,
                    "max": 999,
                    "jitter": 0,
                    "packet_loss": 100,
                    "success": False,
                    "error": "100% packet loss"
                }
            
            return {
                "min": 999,
                "avg": 999,
                "max": 999,
                "jitter": 0,
                "packet_loss": 100,
                "success": False,
                "error": "Failed to parse ping output"
            }
            
        except subprocess.TimeoutExpired:
            return {
                "min": 999,
                "avg": 999,
                "max": 999,
                "jitter": 0,
                "packet_loss": 100,
                "success": False,
                "error": "Ping timeout"
            }
        except Exception as e:
            logger.error(f"Ping error for {host}: {str(e)}")
            return {
                "min": 999,
                "avg": 999,
                "max": 999,
                "jitter": 0,
                "packet_loss": 100,
                "success": False,
                "error": str(e)
            }
    
    def _parse_packet_loss(self, output: str) -> float:
        """解析丢包率"""
        loss_patterns = [
            r'(\d+(?:\.\d+)?)\s*%\s*(?:packet\s*)?loss',
            r'(\d+(?:\.\d+)?)\s*%\s*丢失',
            r'丢包率\s*=\s*(\d+(?:\.\d+)?)\s*%'
        ]
        
        for pattern in loss_patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return float(match.group(1))
        
        return 0.0
    
    async def test_connection_time(self, endpoint: str) -> Dict[str, Any]:
        """测试HTTPS连接时间"""
        url = f"https://{endpoint}"
        times = []
        
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False),
            timeout=aiohttp.ClientTimeout(total=TEST_CONFIG["connection_timeout"])
        ) as session:
            for _ in range(TEST_CONFIG["connection_tests"]):
                try:
                    start_time = asyncio.get_event_loop().time()
                    async with session.head(url) as response:
                        end_time = asyncio.get_event_loop().time()
                        connection_time = (end_time - start_time) * 1000
                        times.append(connection_time)
                except Exception as e:
                    logger.debug(f"Connection test failed for {endpoint}: {str(e)}")
                    times.append(999)
                
                await asyncio.sleep(0.1)
        
        if times:
            valid_times = [t for t in times if t < 999]
            if valid_times:
                return {
                    "avg": statistics.mean(valid_times),
                    "min": min(valid_times),
                    "max": max(valid_times),
                    "success": True
                }
        
        return {
            "avg": 999,
            "min": 999,
            "max": 999,
            "success": False
        }
    
    def calculate_score(self, result: Dict[str, Any]) -> float:
        """计算综合评分"""
        # 延迟评分
        latency = result.get("latency", 999)
        if latency < 50:
            latency_score = 100
        elif latency < 100:
            latency_score = 90
        elif latency < 200:
            latency_score = 70
        elif latency < 300:
            latency_score = 50
        else:
            latency_score = max(0, 30 - (latency - 300) / 10)
        
        # 丢包率评分
        packet_loss = result.get("packet_loss", 100)
        packet_loss_score = max(0, 100 - packet_loss * 2)
        
        # 连接时间评分
        connection_time = result.get("connection_time", 999)
        if connection_time < 100:
            connection_score = 100
        elif connection_time < 200:
            connection_score = 80
        elif connection_time < 500:
            connection_score = 60
        else:
            connection_score = max(0, 40 - (connection_time - 500) / 20)
        
        # 抖动评分
        jitter = result.get("jitter", 999)
        if jitter < 5:
            jitter_score = 100
        elif jitter < 10:
            jitter_score = 80
        elif jitter < 20:
            jitter_score = 60
        else:
            jitter_score = max(0, 40 - jitter)
        
        # 加权计算总分
        total_score = (
            latency_score * SCORE_WEIGHTS["latency"] +
            packet_loss_score * SCORE_WEIGHTS["packet_loss"] +
            connection_score * SCORE_WEIGHTS["connection"] +
            jitter_score * SCORE_WEIGHTS["jitter"]
        )
        
        return round(total_score, 2)
    
    async def test_server(self, name: str, server_info: Dict[str, str], 
                         callback: Optional[callable] = None) -> Dict[str, Any]:
        """测试单个服务器"""
        endpoint = server_info["endpoint"]
        region = server_info["region"]
        location = server_info["location"]
        
        result = {
            "name": name,
            "endpoint": endpoint,
            "region": region,
            "location": location,
            "status": "testing"
        }
        
        try:
            # Ping测试
            ping_result = await asyncio.get_event_loop().run_in_executor(
                self.executor, self.ping_host, endpoint
            )
            
            result.update({
                "latency": ping_result["avg"],
                "min_latency": ping_result["min"],
                "max_latency": ping_result["max"],
                "jitter": ping_result["jitter"],
                "packet_loss": ping_result["packet_loss"]
            })
            
            # 连接时间测试
            connection_result = await self.test_connection_time(endpoint)
            result["connection_time"] = connection_result["avg"]
            
            # 计算评分
            result["score"] = self.calculate_score(result)
            result["status"] = "completed"
            
        except Exception as e:
            logger.error(f"Error testing {name}: {str(e)}")
            result.update({
                "latency": 999,
                "min_latency": 999,
                "max_latency": 999,
                "jitter": 0,
                "packet_loss": 100,
                "connection_time": 999,
                "score": 0,
                "status": "error",
                "error": str(e)
            })
        
        # 更新进度
        self.test_progress += 1
        
        # 调用回调函数
        if callback:
            if asyncio.iscoroutinefunction(callback):
                await callback(result)
            else:
                callback(result)
        
        return result
    
    async def test_all_servers(self, servers: Dict[str, Dict[str, str]], 
                              callback: Optional[callable] = None) -> List[Dict[str, Any]]:
        """并发测试所有服务器"""
        self.test_progress = 0
        self.total_servers = len(servers)
        self.is_testing = True
        
        tasks = []
        for name, info in servers.items():
            task = self.test_server(name, info, callback)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 过滤掉异常结果
        valid_results = []
        for r in results:
            if isinstance(r, dict):
                valid_results.append(r)
            else:
                logger.error(f"Task exception: {r}")
        
        self.is_testing = False
        return valid_results
    
    def get_status(self) -> Dict[str, Any]:
        """获取测试状态"""
        return {
            "is_testing": self.is_testing,
            "progress": self.test_progress,
            "total": self.total_servers
        }