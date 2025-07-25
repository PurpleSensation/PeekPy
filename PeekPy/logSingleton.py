# -*- coding: utf-8 -*-
"""
Simple Logging Singleton for TransFusion

A focused, robust singleton implementation specifically for sharing 
a single Log instance across all TransFusion modules.
"""

import threading
from typing import Optional
from PeekPy.log import Log

class LogSingleton:
    """
    Thread-safe singleton for managing a shared Log instance.
    
    Simple, focused implementation that ensures all TransFusion modules
    access the same Log object with synchronized debug levels.
    """
    
    _instance: Optional['LogSingleton'] = None
    _lock: threading.Lock = threading.Lock()
    _log: Optional[Log] = None
    
    def __new__(cls) -> 'LogSingleton':
        if cls._instance is None:
            with cls._lock:
                # Double-check locking pattern
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_log(self) -> Log:
        """Get the shared Log instance, creating it if necessary."""
        if self._log is None:
            with self._lock:
                if self._log is None:
                    self._log = Log()
        return self._log
    
    def set_debug_level(self, level: int) -> Log:
        """Set debug level on the shared log instance."""
        log = self.get_log()
        log.set_debug_level(level)
        return log
    
    def reset_log(self) -> Log:
        """Reset the log instance (useful for testing)."""
        with self._lock:
            self._log = Log()
        return self._log

# Global singleton instance
_singleton = LogSingleton()

def get_shared_log() -> Log:
    """Get the shared Log instance used across all TransFusion modules."""
    return _singleton.get_log()

def configure_debug_level(level: int = 0) -> Log:
    """Configure the debug level for all TransFusion modules."""
    return _singleton.set_debug_level(level)

def reset_shared_log() -> Log:
    """Reset the shared log (mainly for testing)."""
    return _singleton.reset_log()
