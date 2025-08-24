"""工具函数模块"""

import requests
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def get_public_ip() -> Dict[str, Any]:
    """获取公网IP地址和位置信息"""
    
    # 专门的IPv4和IPv6检测API
    ipv4_apis = [
        "https://api.ipify.org?format=json",
        "https://ipv4.icanhazip.com",
        "https://ipv4.jsonip.com"
    ]
    
    ipv6_apis = [
        "https://api6.ipify.org?format=json", 
        "https://ipv6.icanhazip.com",
        "https://ipv6.jsonip.com"
    ]
    
    # 详细信息API
    detail_apis = [
        {
            "url": "http://ip-api.com/json/",
            "parser": lambda r: {
                "country": r.get("country", "Unknown"),
                "city": r.get("city", "Unknown"),
                "region": r.get("regionName", "Unknown"),
                "isp": r.get("isp", "Unknown"),
                "location": f"{r.get('city', 'Unknown')}, {r.get('country', 'Unknown')}"
            }
        },
        {
            "url": "https://ipapi.co/json/",
            "parser": lambda r: {
                "country": r.get("country_name", "Unknown"),
                "city": r.get("city", "Unknown"),
                "region": r.get("region", "Unknown"),
                "isp": r.get("org", "Unknown"),
                "location": f"{r.get('city', 'Unknown')}, {r.get('country_name', 'Unknown')}"
            }
        },
        {
            "url": "https://ipinfo.io/json",
            "parser": lambda r: {
                "country": r.get("country", "Unknown"),
                "city": r.get("city", "Unknown"),
                "region": r.get("region", "Unknown"),
                "isp": r.get("org", "Unknown"),
                "location": f"{r.get('city', 'Unknown')}, {r.get('country', 'Unknown')}"
            }
        }
    ]
    
    result = {
        "ipv4": "Unknown",
        "ipv6": "Unknown", 
        "country": "Unknown",
        "city": "Unknown",
        "region": "Unknown",
        "isp": "Unknown",
        "location": "Unknown, Unknown"
    }
    
    # 获取IPv4地址
    for api_url in ipv4_apis:
        try:
            response = requests.get(api_url, timeout=3)
            if response.status_code == 200:
                if api_url.endswith('json'):
                    data = response.json()
                    result["ipv4"] = data.get("ip", "Unknown")
                else:
                    result["ipv4"] = response.text.strip()
                if result["ipv4"] != "Unknown":
                    break
        except Exception as e:
            logger.debug(f"Failed to get IPv4 from {api_url}: {e}")
            continue
    
    # 获取IPv6地址
    for api_url in ipv6_apis:
        try:
            response = requests.get(api_url, timeout=3)
            if response.status_code == 200:
                if api_url.endswith('json'):
                    data = response.json()
                    result["ipv6"] = data.get("ip", "Unknown")
                else:
                    result["ipv6"] = response.text.strip()
                if result["ipv6"] != "Unknown":
                    break
        except Exception as e:
            logger.debug(f"Failed to get IPv6 from {api_url}: {e}")
            continue
    
    # 获取详细信息（使用主要IP地址）
    primary_ip = result["ipv4"] if result["ipv4"] != "Unknown" else result["ipv6"]
    for api in detail_apis:
        try:
            response = requests.get(api["url"], timeout=5)
            if response.status_code == 200:
                data = response.json()
                # 检查API是否返回了有效数据
                if data and isinstance(data, dict):
                    detail = api["parser"](data)
                    # 确保至少有一些有用的信息
                    if any(v != "Unknown" for v in detail.values()):
                        result.update(detail)
                        logger.debug(f"Successfully got details from {api['url']}")
                        break
                    else:
                        logger.debug(f"API {api['url']} returned all Unknown values")
                else:
                    logger.debug(f"API {api['url']} returned invalid data: {data}")
        except Exception as e:
            logger.debug(f"Failed to get details from {api['url']}: {e}")
            continue
    
    # 保持向后兼容性
    result["ip"] = primary_ip
    
    return result


def format_latency(latency: float) -> str:
    """格式化延迟显示"""
    if latency >= 999:
        return "超时"
    return f"{latency:.1f}ms"


def format_percentage(value: float) -> str:
    """格式化百分比显示"""
    return f"{value:.1f}%"


def get_latency_color(latency: float) -> str:
    """根据延迟返回对应的颜色类名"""
    if latency < 50:
        return "excellent"
    elif latency < 100:
        return "good"
    elif latency < 200:
        return "fair"
    elif latency < 300:
        return "poor"
    else:
        return "bad"


def get_score_color(score: float) -> str:
    """根据评分返回对应的颜色类名"""
    if score >= 90:
        return "excellent"
    elif score >= 75:
        return "good"
    elif score >= 60:
        return "fair"
    elif score >= 40:
        return "poor"
    else:
        return "bad"