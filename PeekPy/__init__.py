"""
PeekPy - Hierarchical Console Logging
=====================================

Professional hierarchical logging utilities for Python applications.

This package provides high-quality, production-ready tools for:
- Advanced hierarchical logging with visual formatting
- Console tables and progress bars
- Python code analysis and documentation utilities

Released under CC0 - Public Domain Dedication.

Contributors: Open source community
License: CC0 1.0 Universal (Public Domain)
"""

__version__ = "1.0.0"
__author__ = "PeekPy Contributors"
__email__ = "contributors@github.com"
__license__ = "CC0-1.0"

# Import main classes for convenience
try:
    from .log import Log, ConsoleTable, ProgressBar, t2str, DebugChars
    from .peekPy import PeekPy, ConsoleStream, HTMLStream
    
    __all__ = [
        # Logging utilities
        'Log', 'ConsoleTable', 'ProgressBar', 't2str', 'DebugChars',
        # CSV utilities  
        'timeParse', 'splitCSV', 'diffCSV', 'copyCSV',
        # Code analysis
        'PeekPy', 'ConsoleStream', 'HTMLStream',
        'get_pattern_detector',
    ]
    
except ImportError as e:
    # Graceful degradation for missing dependencies
    import warnings
    if "No module named 'log'" not in str(e):  # Only warn for real issues
        warnings.warn(f"Some modules could not be imported: {e}")
    __all__ = []

def get_version():
    """Return the current version of CoreMarine Utils."""
    return __version__

def get_info():
    """Return package information."""
    return {
        'name': 'PeekPy',
        'version': __version__,
        'author': __author__,
        'license': __license__,
        'description': 'Hierarchical console logging utilities for Python'
    }

def setup_logging(style='minimal', debug_level=0):
    """
    Convenience function to set up logging with sensible defaults.
    
    Args:
        style: Visual style ('minimal', 'reinassance')
        debug_level: Verbosity level (0=normal, 1=verbose, 2=debug)
    
    Returns:
        Log: Configured logger instance
    """
    try:
        log = Log()
        log.set_style(style)
        log.set_debug_level(debug_level)
        return log
    except NameError:
        raise ImportError("Log class not available. Check dependencies.")

# Package metadata for setup.py
METADATA = {
    'name': 'peekpy',
    'version': __version__,
    'description': 'Hierarchical console logging utilities for Python',
    'long_description': __doc__,
    'author': __author__,
    'author_email': __email__,
    'license': __license__,
    'python_requires': '>=3.8',
    'install_requires': [
        'numpy>=1.20.0',
        'pandas>=1.3.0',
    ],
    'extras_require': {
        'full': [
            'pygments>=2.10.0',
            'matplotlib>=3.3.0',
        ]
    }
}
