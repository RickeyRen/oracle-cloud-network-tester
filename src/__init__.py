"""Oracle Network Test Package"""

from .config import ORACLE_SERVERS, TEST_CONFIG, SCORE_WEIGHTS, FLASK_CONFIG
from .network_tester import NetworkTester
from .utils import get_public_ip, format_latency, format_percentage

__version__ = "2.1.0"
__author__ = "Oracle Network Test Contributors"

__all__ = [
    "ORACLE_SERVERS",
    "TEST_CONFIG", 
    "SCORE_WEIGHTS",
    "FLASK_CONFIG",
    "NetworkTester",
    "get_public_ip",
    "format_latency",
    "format_percentage"
]