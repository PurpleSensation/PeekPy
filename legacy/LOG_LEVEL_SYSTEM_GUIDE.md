# Log Class Level System Architecture (Updated)

## Overview
The `Log` class implements a hierarchical logging system with visual indentation, timing, and selective output control. This document explains the core level system and its **new improved behavior**.

## Core Concepts

### 1. Level System
- **`self.level`**: Current nesting depth (0 = root, 1+ = nested)
- **`self.DEBUG`**: Visibility threshold controlling output verbosity
- **Ring Buffers**: Fixed-size arrays tracking state for each level

### 2. New Improved Output Control Logic

#### `up()` Method Behavior:
```python
if DEBUG >= new_level:          # Full decorated output
    # Show decorated header with level info: "• ─── Header [L1] ───"
elif DEBUG == new_level - 1:    # Minimal parent visibility
    # Show simple format: "Header... "
else:                           # Completely suppressed
    # No output at all
```

#### `down()` Method Behavior:
```python
if DEBUG > new_level:           # Full closure
    # Show complete closure: "• ─ exit_msg ─── • timing"
elif DEBUG == new_level:        # Complete the "..." message
    # Show inline completion: "exit_msg • timing" or "✔ • timing"
else:                          # Completely suppressed
    # No output at all
```

### 3. Visual Formatting
- **Decorated Headers**: `• ────── Header [L1] ──────` for full visibility
- **Minimal Headers**: `Header... ` for parent visibility
- **Level Info**: `[L1]`, `[L2]`, etc. in decorated headers
- **Timing**: Always shown when closure is displayed

## Key Methods (Updated)

### `up(header="...")` 
**Purpose**: Enter new scope level with clearer output rules
**New Behavior**:
1. Check skip mechanism
2. Increment level (with bounds checking)
3. Initialize timing and state for new level
4. **NEW**: Output based on precise DEBUG/level relationship:
   - `DEBUG >= level`: Decorated header with level number
   - `DEBUG == level-1`: Simple "header..." format
   - `DEBUG < level-1`: Silent

### `down(exit_msg=False)`
**Purpose**: Exit current scope level with matching closure style
**New Behavior**:
1. Check skip mechanism
2. Calculate elapsed time for scope
3. Update performance history (if enabled)
4. **NEW**: Output based on precise DEBUG/level relationship:
   - `DEBUG > new_level`: Full decorated closure
   - `DEBUG == new_level`: Inline completion of "..." message
   - `DEBUG < new_level`: Silent

### Special Handling
- **Empty Headers**: `header="..."` suppresses output even when DEBUG level would normally show it
- **Custom Exit Messages**: Shown instead of default "───" when provided
- **Timing**: Always included in closure messages when displayed

## Usage Examples

### Example 1: DEBUG=1 (Minimal Mode)
```python
log.set_debug_level(1)
log.up("Main Process")      # Shows: "• ─── Main Process [L1] ───"
log.up("Sub Process")       # Shows: "Sub Process... "
log.down("completed")       # Shows: "completed • 0.1s"
log.down("finished")        # Shows: "• ─ finished ─ • 0.2s"
```

### Example 2: DEBUG=2 (Verbose Mode)
```python
log.set_debug_level(2)
log.up("Level 1")           # Shows: "• ─── Level 1 [L1] ───"
log.up("Level 2")           # Shows: "• ─── Level 2 [L2] ───"
log.up("Level 3")           # Shows: "Level 3... "
log.down("L3 done")         # Shows: "L3 done • 0.05s"
log.down("L2 done")         # Shows: "• ─ L2 done ─ • 0.1s"
log.down("L1 done")         # Shows: "• ─ L1 done ─ • 0.15s"
```

## Advanced Features (Unchanged)

### Skip Mechanism
- **Purpose**: Conditionally suppress up/down output without breaking call structure
- **Behavior**: Level changes still occur, only visual output is suppressed

### Method Tracking
- **Purpose**: Automatic debug level management for method tracing
- **Behavior**: Enables debugging for specific scoped block, auto-resets on exit

### Performance History
- **Purpose**: Accumulate timing statistics per scope header
- **Storage**: `{header: [call_count, total_time]}` dictionary

## Recent Bug Fixes

### Closure Alignment Fix (June 2025)
Fixed a critical alignment issue where closure brackets were appearing at the wrong indentation level. The problem was that the prefix was being updated before the closure output, causing misaligned brackets.

**Before:**
```
   • ────── Process [L1] ──────
   │ Work happening...
 • ─ completed ─ • 0.1s        # Misaligned!
```

**After:**
```
   • ────── Process [L1] ──────
   │ Work happening...
   • ─ completed ─ • 0.1s      # Properly aligned!
```

**Fix:** Preserve the original prefix before decrementing the level in `down()` method.

## Design Improvements (Updated)

### 1. **Clearer Logic**: Precise DEBUG/level comparisons eliminate ambiguity
### 2. **Better Pairing**: up() and down() outputs are visually matched
### 3. **Level Visibility**: Level numbers `[L1]`, `[L2]` make nesting depth explicit
### 4. **Consistent Timing**: Timing always shown when closure is displayed
### 5. **Graceful Degradation**: Empty headers handled elegantly

## Migration Notes

The new behavior is **backward compatible** - existing code will work but may see slightly different output formatting. The core functionality (timing, nesting, skip mechanism) remains unchanged.

### Key Changes:
- Level information `[L1]` now appears in decorated headers
- Empty headers `"..."` are handled more gracefully
- Output pairing between up/down is more consistent
- DEBUG level comparisons are more precise

## Troubleshooting

### Common Issues
- **Unexpected silence**: Check if DEBUG level matches your expectations for the nesting depth
- **Missing level info**: Level numbers only appear in fully decorated headers (DEBUG >= level)
- **Timing not shown**: Timing only appears when closure messages are displayed

### Debug Strategies
- Use `log.set_debug_level(3)` to see all output during development
- Remember: `DEBUG >= level` for full decoration, `DEBUG == level-1` for minimal
- Empty headers always suppress output regardless of DEBUG level
