import time
import logging
from functools import wraps
from typing import Callable, Any
import psutil
import os

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    @staticmethod
    def measure_execution_time(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            start_memory = psutil.Process(os.getpid()).memory_info().rss
            
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                end_time = time.time()
                end_memory = psutil.Process(os.getpid()).memory_info().rss
                
                execution_time = end_time - start_time
                memory_usage = (end_memory - start_memory) / 1024 / 1024  # Convert to MB
                
                logger.info(
                    f"Function {func.__name__} executed in {execution_time:.2f} seconds, "
                    f"memory usage: {memory_usage:.2f} MB"
                )
        
        return wrapper

    @staticmethod
    def get_system_metrics() -> dict:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu_usage': cpu_percent,
            'memory_usage': {
                'total': memory.total / (1024 * 1024 * 1024),  # GB
                'used': memory.used / (1024 * 1024 * 1024),    # GB
                'percent': memory.percent
            },
            'disk_usage': {
                'total': disk.total / (1024 * 1024 * 1024),    # GB
                'used': disk.used / (1024 * 1024 * 1024),      # GB
                'percent': disk.percent
            }
        } 