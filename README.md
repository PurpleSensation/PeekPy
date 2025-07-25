# PeekPy - Simple Python Logging Tools

A small collection of logging utilities I made for my own projects. The main component is a hierarchical logging system that I've been refining over time.

## Quick Start - Multi-Module Logging

For projects that need shared logging across multiple modules, create a simple singleton in your main project:

```python
# your_project/logSingleton.py
import threading
from PeekPy.log import Log

class LogSingleton:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.logger = Log()
        return cls._instance
    
    def get_shared_log(self):
        return self.logger

_singleton = LogSingleton()

def get_shared_log():
    return _singleton.get_shared_log()

def configure_debug_level(level):
    logger = get_shared_log()
    logger.DEBUG = level
    return logger
```

Then use in any module: `from your_project.logSingleton import get_shared_log; log = get_shared_log()`

## What's in here

- **Hierarchical logging** - Main feature, handles nested output with indentation
- **Console tables** - Simple table formatting for terminal output  
- **CSV utilities** - Basic time parsing and data processing tools
- **Code analysis** - Some Python code inspection helpers

The logging module is the most developed part. Everything else is just utility functions I needed along the way.

## Installation

No pip package - just clone and import:

```bash
git clone https://github.com/PurpleSensation/PeekPy.git
```

Add to your Python path or copy the files you need. Zero external dependencies (just standard library).

## Basic Logging Usage

```python
from PeekPy.log import Log

log = Log()
log.up("Starting process")
log.log("Step 1 complete")
log.log("Step 2 complete") 
log.down("Process finished")
```

Output:
```
◻ ────── Starting process ──────
 │ Step 1 complete
 │ Step 2 complete
◻ ──── Process finished ────
```

## Shared Logger Pattern

For projects needing synchronized logging across multiple modules, **we recommend implementing a simple singleton in your main project** rather than relying on PeekPy's built-in shared logging (which can be unreliable in complex scenarios).

### Recommended Approach - Local Singleton:

Create this in your main project:

```python
# your_project/logSingleton.py
import threading
from PeekPy.log import Log

class LogSingleton:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.logger = Log()
        return cls._instance
    
    def get_shared_log(self):
        return self.logger

_singleton = LogSingleton()

def get_shared_log():
    return _singleton.get_shared_log()

def configure_debug_level(level):
    logger = get_shared_log()
    logger.DEBUG = level
    return logger
```

Then create a clean interface:

```python
# your_project/logging_interface.py  
from .logSingleton import get_shared_log, configure_debug_level

log = get_shared_log()

def debug(level=0):
    return configure_debug_level(level)
```

Use in any module:

```python
# your_project/any_module.py
from .logging_interface import log

def process_data():
    log.up("Processing sensor data")
    log.log("Loading files...")
    log.down("Complete")
```

This ensures all modules share the **exact same logger instance** with synchronized debug levels.

### Alternative - PeekPy Built-in (Less Reliable):

```python
# your_project/__init__.py
from PeekPy.log import configure_shared_logging, get_shared_logger

def debug(level=0):
    return configure_shared_logging(level=level)

# your_project/some_module.py
from PeekPy.log import get_shared_logger
log = get_shared_logger()
```

**Note:** The built-in shared logging can sometimes create multiple instances in complex import scenarios. For critical applications, use the local singleton approach above.

## Debug Levels

Debug levels control the maximum nesting depth that will show output:
- **DEBUG >= level**: Shows full decorated output with brackets and timing
- **DEBUG == level-1**: Shows minimal "header..." format  
- **DEBUG < level**: Suppresses all output for that level

Example: If `DEBUG=1`, you'll see levels 0 and 1, but level 2+ will be silent.

## Other Logging Types

```python
log.log("Regular message")           # Standard log
log.softlog("Status update")         # Overwrites previous line
log.inline("continued...")           # Continues current line
log.warning("Something's wrong")     # Warning message
log.blank()                          # Empty line
```

## Console Tables

```python
table = log.consoleTable(
    headers=["Name", "Value", "Status"], 
    formats=["{}", "{:.2f}", "{}"],
    title="Results"
)
table.add_row("Item1", 3.14159, "OK")
table.add_row("Item2", 2.71828, "PASS") 
table.close()
```

## Lists and Trees

```python
# List items with various formatting options
log.list(["item1", "item2", "item3"], header="My Items", style="dash")

# Display nested data as a tree structure  
data = {"config": {"db": "localhost", "port": 5432}, "status": "active"}
log.tree(data, header="Configuration", show_types=True)

# Simple itemized lists
log.itemize([
    "Process started",
    "Data loaded", 
    "Calculations complete"
], "Status Updates")
```

## Progress Bars

```python
progress = log.progressBar(header="Processing")
# Use progress methods for tracking long operations
```

## That's it

Simple tools for console output and basic data processing. The logging system handles nesting automatically - just follow the `up()`/`down()` pattern and it tracks indentation levels for you.

No fancy features, no complex configuration. Import and use.
