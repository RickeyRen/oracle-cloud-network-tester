"""配置模块 - Oracle Cloud服务器配置和测试参数"""

from typing import Dict, Any

# Oracle Cloud免费VPS服务器列表
ORACLE_SERVERS: Dict[str, Dict[str, Any]] = {
    "美国东部（阿什本）": {
        "endpoint": "iaas.us-ashburn-1.oraclecloud.com",
        "region": "us-ashburn-1",
        "location": "美国弗吉尼亚州"
    },
    "美国西部（凤凰城）": {
        "endpoint": "iaas.us-phoenix-1.oraclecloud.com", 
        "region": "us-phoenix-1",
        "location": "美国亚利桑那州"
    },
    "美国西部（圣何塞）": {
        "endpoint": "iaas.us-sanjose-1.oraclecloud.com",
        "region": "us-sanjose-1", 
        "location": "美国加利福尼亚州"
    },
    "加拿大（多伦多）": {
        "endpoint": "iaas.ca-toronto-1.oraclecloud.com",
        "region": "ca-toronto-1",
        "location": "加拿大安大略省"
    },
    "巴西（圣保罗）": {
        "endpoint": "iaas.sa-saopaulo-1.oraclecloud.com",
        "region": "sa-saopaulo-1",
        "location": "巴西"
    },
    "智利（圣地亚哥）": {
        "endpoint": "iaas.sa-santiago-1.oraclecloud.com",
        "region": "sa-santiago-1",
        "location": "智利"
    },
    "英国（伦敦）": {
        "endpoint": "iaas.uk-london-1.oraclecloud.com",
        "region": "uk-london-1",
        "location": "英国"
    },
    "德国（法兰克福）": {
        "endpoint": "iaas.eu-frankfurt-1.oraclecloud.com",
        "region": "eu-frankfurt-1",
        "location": "德国"
    },
    "瑞士（苏黎世）": {
        "endpoint": "iaas.eu-zurich-1.oraclecloud.com",
        "region": "eu-zurich-1",
        "location": "瑞士"
    },
    "荷兰（阿姆斯特丹）": {
        "endpoint": "iaas.eu-amsterdam-1.oraclecloud.com",
        "region": "eu-amsterdam-1",
        "location": "荷兰"
    },
    "法国（马赛）": {
        "endpoint": "iaas.eu-marseille-1.oraclecloud.com",
        "region": "eu-marseille-1",
        "location": "法国"
    },
    "沙特阿拉伯（吉达）": {
        "endpoint": "iaas.me-jeddah-1.oraclecloud.com",
        "region": "me-jeddah-1",
        "location": "沙特阿拉伯"
    },
    "阿联酋（迪拜）": {
        "endpoint": "iaas.me-dubai-1.oraclecloud.com",
        "region": "me-dubai-1",
        "location": "阿联酋"
    },
    "以色列（耶路撒冷）": {
        "endpoint": "iaas.il-jerusalem-1.oraclecloud.com",
        "region": "il-jerusalem-1",
        "location": "以色列"
    },
    "南非（约翰内斯堡）": {
        "endpoint": "iaas.af-johannesburg-1.oraclecloud.com",
        "region": "af-johannesburg-1",
        "location": "南非"
    },
    "印度（孟买）": {
        "endpoint": "iaas.ap-mumbai-1.oraclecloud.com",
        "region": "ap-mumbai-1",
        "location": "印度"
    },
    "印度（海得拉巴）": {
        "endpoint": "iaas.ap-hyderabad-1.oraclecloud.com",
        "region": "ap-hyderabad-1",
        "location": "印度"
    },
    "新加坡": {
        "endpoint": "iaas.ap-singapore-1.oraclecloud.com",
        "region": "ap-singapore-1",
        "location": "新加坡"
    },
    "澳大利亚（墨尔本）": {
        "endpoint": "iaas.ap-melbourne-1.oraclecloud.com",
        "region": "ap-melbourne-1",
        "location": "澳大利亚"
    },
    "澳大利亚（悉尼）": {
        "endpoint": "iaas.ap-sydney-1.oraclecloud.com",
        "region": "ap-sydney-1",
        "location": "澳大利亚"
    },
    "日本（东京）": {
        "endpoint": "iaas.ap-tokyo-1.oraclecloud.com",
        "region": "ap-tokyo-1",
        "location": "日本"
    },
    "日本（大阪）": {
        "endpoint": "iaas.ap-osaka-1.oraclecloud.com",
        "region": "ap-osaka-1",
        "location": "日本"
    },
    "韩国（首尔）": {
        "endpoint": "iaas.ap-seoul-1.oraclecloud.com",
        "region": "ap-seoul-1",
        "location": "韩国"
    },
    "韩国（春川）": {
        "endpoint": "iaas.ap-chuncheon-1.oraclecloud.com",
        "region": "ap-chuncheon-1",
        "location": "韩国"
    }
}

# 测试配置
TEST_CONFIG = {
    "ping_count": 5,            # ping测试次数 (减少到5次，加快速度)
    "ping_timeout": 2,          # ping超时时间（秒）(减少到2秒)
    "connection_tests": 3,      # HTTPS连接测试次数 (减少到3次)
    "connection_timeout": 3,    # HTTPS连接超时时间（秒）(减少到3秒)
    "max_workers": 15,          # 最大并发线程数 (增加并发数)
}

# 评分权重配置
SCORE_WEIGHTS = {
    "latency": 0.4,        # 延迟权重 40%
    "packet_loss": 0.3,    # 丢包率权重 30%
    "connection": 0.2,     # 连接时间权重 20%
    "jitter": 0.1,         # 抖动权重 10%
}

# Flask配置
FLASK_CONFIG = {
    "host": "0.0.0.0",
    "port": 5001,
    "debug": False,
    "threaded": True
}