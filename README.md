# PeekPy - Hierarchical Console Logging

A hierarchical logging system for Python that handles nested console logs with indentation and clean terminal output.


```
 ◻ ────────────────────── Welcome to PeekPy ──────────
 │ Python library for  organised, hierarchical console logging
 │ Turns chaotic print statements into structured logs
 │ Ready to see how it works?
 │  
 │
 │ ◻ ────────────────────── Core Features ──────────
 │ │ ✨ Hierarchical nesting with automatic indentation
 │ │ 🎯 Simple: Follow up()/down() pattern
 │ │ ⚙ 📊 Built-in resources:
 │ │     ╰─┬─ Standard logging and status refresh
 │ │       ├─ Emojis and Unicode support
 │ │       ├─ Tables, lists, trees, and progress bars
 │ │       ╰───────────
 │ ◻──────────────────── simple & clean ─────────  • 0.0s
 │  
 ◻──────────────────── ─── ─────── -  • 0.0s
```

## Quick Start - Multi-Module Logging

For projects that need shared logging across multiple modules, copy the `PeekPy/logSingleton.py` file to your project and use it:

```python
# Copy PeekPy/logSingleton.py to your_project/logSingleton.py
# Then use in any module:
from your_project.logSingleton import get_shared_log, configure_debug_level

log = get_shared_log()

def process_data():
    log.up("Processing sensor data")
    log.log("Loading files...")
    log.down("Complete")

# Configure debug level from anywhere:
configure_debug_level(2)  # All modules get this level
```

This ensures all modules share the **exact same logger instance** with synchronized debug levels.

## Installation

```bash
git clone https://github.com/PurpleSensation/PeekPy.git
cd PeekPy
pip install -e .
```

Import the logging module: `from PeekPy.log import Log`

Zero external dependencies (just standard library).

## Basic Logging Usage

```python
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

### Recommended Approach - Copy the Singleton:

Copy `PeekPy/logSingleton.py` to your project and use it:

```python
# Copy PeekPy/logSingleton.py to your_project/logSingleton.py
from your_project.logSingleton import get_shared_log, configure_debug_level

log = get_shared_log()

def process_data():
    log.up("Processing sensor data")
    log.log("Loading files...")
    log.down("Complete")

# Set debug level from anywhere - all modules get it:
configure_debug_level(2)
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

# Logging Types
There are various formatted logging tools you can use, here is an example containing the main ones:
```python
log("Next is a complete example of output showcase:")
    log.up("Logging Example") # lvl 1
    log("Operations can be nested using up()/down()")
    log("Call log.up(header) to start a new level:")
    log.up("level heading") # lvl 2
    log("📥 Loading files - sample msg")
    list_items = [
        "Intuitive up()/down() pattern",
        "Professional console output", 
        "Debug complex workflows easily",
        "Built-in progress tracking",
        "Customizable appearance"
    ]
    log("Collections can be displayed lists:")
    log.list(list_items, header="Key Benefits", style="bullet")
    log("✅ Validation complete")
    
    log.up("Processing") # lvl 3
    log("🔄 Applying transformations")
    log("📈 Computing metrics")
    
    log.up("Analysis") # lvl 4
    log("🧮 Running calculations")
    log("⚡ Optimizing parameters")
    
    sample_config = {
        "logging": {
            "style": "minimal",
            "debug_level": 1,
            "features": ["nesting", "tables", "progress"]
        },
        "output": {
            "format": "console",
            "colors": True,
            "unicode": True
        }
    }
    log("... also as trees...:")
    log.tree(sample_config, header="sample tree", show_types=True)
    log("Other tools are present, but less developed")
    log.down("analysis finished") # lvl 3    
    log("The object also includes small linting and time registration tools")
    log.down("processing finished") # lvl 2
    log("As well as helper methods to locally modify the log behavior")
    log.down("Pipeline complete") # lvl 1
    # Demonstrate table functionality
    log("Support for tables:")
    table = log.consoleTable(
        headers=["         Feature        ", "    Status     ", "  Rating  "], 
        formats=["{}", "{}", "{:.1f}/10"],
        title="sample table"
    )
    table.add_row("Hierarchical Logging", "✅ Ready", 9.5)
    table.add_row("Auto-Indentation", "✅ Ready", 9.0)
    table.add_row("Progress Tracking", "✅ Ready", 8.8)
    table.add_row("Data Trees", "✅ Ready", 9.2)
    table.close()
    log.down("end of example") # lvl 0
```
output:
```
 ◻ ────────────────────── Logging Example ──────────
 │ Operations can be nested using up()/down()
 │ Call log.up(header) to start a new level:
 │
 │ ◻ ────────────────────── level heading ──────────
 │ │ 📥 Loading files - sample msg
 │ │ Collections can be displayed lists:
 │ │ ⚙ Key Benefits:
 │ │     ╰─┬• Intuitive up()/down() pattern
 │ │       ├• Professional console output
 │ │       ├• Debug complex workflows easily
 │ │       ├• Built-in progress tracking
 │ │       ├• Customizable appearance
 │ │       ╰───────────
 │ │ ✅ Validation complete
 │ │
 │ │ ◻ ────────────────────── Processing ──────────
 │ │ │ 🔄 Applying transformations
 │ │ │ 📈 Computing metrics
 │ │ │
 │ │ │ ◻ ────────────────────── Analysis ──────────
 │ │ │ │ 🧮 Running calculations
 │ │ │ │ ⚡ Optimizing parameters
 │ │ │ │ ... also as trees...:
 │ │ │ │   ⚙ sample tree
 │ │ │ │      ─┬○ Logging:                    ─┬○ Output:                  
 │ │ │ │       ╰─┬─ style = minimal (str)      ╰─┬─ format = console (str) 
 │ │ │ │         ├─ debug_level = 1 (int)        ├─ colors = True (bool)   
 │ │ │ │         ╰─┬─ nesting                    ╰─ unicode = True (bool)  
 │ │ │ │           ├─ tables                                               
 │ │ │ │           ╰─ progress                                             
 │ │ │ │                                                                   
 │ │ │ │  
 │ │ │ │ Other tools are present, but less developed
 │ │ │ ◻──────────────────── analysis finished ─────────  • 0.0s
 │ │ │  
 │ │ │ The object also includes small linting and time registration tools
 │ │ ◻──────────────────── processing finished ─────────  • 0.0s
 │ │  
 │ │ As well as helper methods to locally modify the log behavior
 │ ◻──────────────────── Pipeline complete ─────── -  • 0.1s
 │  
 │ Support for tables:
 │  
 │ ╭──────────────────── sample table ────────────────────╮
 │ │                                                       │
 │ │         Feature         │     Status      │   Rating  │
 │ │  Hierarchical Logging   │     ✅ Ready     │   9.5/10  │
 │ │    Auto-Indentation     │     ✅ Ready     │   9.0/10  │
 │ │   Progress Tracking     │     ✅ Ready     │   8.8/10  │
 │ │       Data Trees        │     ✅ Ready     │   9.2/10  │
 │ ╰───────────────────────────────────────────────────────╯
 │  
 ◻──────────────────── end of example ─────── -  • 0.1s
```


### Print messages
```python
log.log("Regular message")           # Standard log
log.softlog("Status update")         # Overwrites previous line
log.inline("continued...")           # Continues current line
log.warning("Something's wrong")     # Warning message
log.blank()                          # Empty line
```

### Console Tables

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

### Lists and Trees

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

### Progress Bars

```python
progress = log.progressBar(header="Processing")
# Use progress methods for tracking long operations
```

## That's it

Simple hierarchical logging for console output. The system handles nesting automatically - just follow the `up()`/`down()` pattern and it tracks indentation levels for you.

No fancy features, no complex configuration. Import and use.
