# -=--==-=--==-=--==-=--== Logging Utility -=--==-=--==-=--==-=--==
import time as tm, numpy as np
import re, os, shutil, pathlib
from typing import List, Dict, Optional, Union, Tuple
from math import floor
n_indent = 0

class Log:
    """Lightweight hierarchical logger with indented console output.

    The public interface is fully backward‑compatible with the original
    *Log* class but several long‑standing bugs have been fixed and the
    behaviour was made more predictable.
    """
    # ────────────────────────────────────────────────────────── init ──
    def __init__(self, logpath: str = "logs/log.txt", n_buffer: int = 40):
        # ═══════════════════════════════════════════════════════════════════
        # CORE LEVEL SYSTEM:
        # - self.level: Current indentation depth (0 = root, 1+ = nested)
        # - self.DEBUG: Visibility threshold (controls which levels show output)
        #   * DEBUG >= level: show full decorated output for this level
        #   * DEBUG == level-1: show minimal "header..." format
        #   * DEBUG < level: suppress output entirely
        # - Ring buffers track state for each level (size = n_buffer)
        # ═══════════════════════════════════════════════════════════════════
        
        self.DEBUG: int = 0                    # output visibility threshold  
        self.level: int = 0                    # current nesting/indentation level
        self.muted: bool = False               # global mute flag
        self._mute_level: Optional[int] = None # indent level where mute started

        # runtime house‑keeping
        self.logpath:   str     = logpath
        self.n_buffer:  int     = n_buffer    # max nesting depth (ring buffer size)
        self.prefix:    str     = "\n  "      # visual indentation string (updated by _set_level)
        self.softflag:  bool    = False
        self.cumline:   str     = None
        self.l_count:   int     = 0           # line counter for current scope

        # time + header ring buffers (indexed by level)
        self._time_level:    List[float]     = [0.0] * n_buffer    # start time for each level
        self._header_level:  List[str]       = ["..."] * n_buffer # header text for each level

        # history log (for performance analysis)
        self._h_log:     bool                    = False
        self._timelog:   Dict[str, List[float]]  = {}  # header -> [call_count, total_time]

        # special control mechanisms
        self._tracking:  bool                    = False    # method tracking mode flag
        self._skip_next:  int                    = False    # level to skip (for conditional suppression)
        
        # ascii‑art separators
        self.set_style("minimal")  # default style
    def __call__(self, msg: str):
        """Log a message at the current indentation level."""
        if self.muted or self.DEBUG < self.level:
            return self
        if self.softflag:
            self.softflag = False
            self.addItem(None)
        print(f"{self.prefix} {msg}", end="", flush=True)
        return self
    
    # ─────────────────────────────────────────────────────── up & down ──
    def up(self, header: str = "..."):
        """Increase indentation level (clamped to *n_buffer‑1*).
        
        Creates a new scope level for hierarchical logging with timing and visual indentation.
        Each call to up() should be matched with a corresponding down() call.
        
        Output behavior:
        - DEBUG >= new_level: Show decorated header with hline containing level info
        - DEBUG == new_level-1: Show simple "header..." message (if header provided)
        - DEBUG < new_level-1: Suppress all output
        """
        # Handle skip mechanism: if skip() was called at current level, 
        # decrement the skip counter and bypass this up() call entirely
        if self._skip_next:
            self._skip_next += 1
            if self._skip_next == 2:                
                return self
        
        # Increment indentation level (with bounds checking in _set_level)
        self._set_level(self.level + 1)
        
        # Initialize counters and timing for this new level
        self.l_count = 0  # Reset line count for this scope
        self._time_level[self.level] = tm.time()  # Start timing this scope
        self._header_level[self.level] = header   # Store header for this level
        
        # Early exit if globally muted
        if self.muted:
            return self
            
        # Output formatting depends on DEBUG level relative to new level:
        
        # Case 1: DEBUG >= new level (full verbose mode)
        # Show decorated header with hline containing level information
        if self.DEBUG >= self.level:
            if header != "...":  # Only show if meaningful header
                rnd_start = np.random.choice(self.separators)[:40]
                rnd_end = np.random.choice(self.separators)[:10]
                decorated_header = f"{self.prefix[:-2]}{self.prefix[:-1]}• {rnd_start} {header} {rnd_end}"
                # Truncate to prevent overly long lines (75 char limit)
                print(decorated_header[:min(75, len(decorated_header))], end="", flush=True)
            
        # Case 2: DEBUG == new_level-1 (minimal parent visibility mode)
        # Show simple "header..." format if header is provided
        elif self.DEBUG == self.level - 1:
            if header != "...":  # Only show if meaningful header
                print(f"{self.prefix[:-1]}{header}... ", end="", flush=True)
                
        # Case 3: DEBUG < new_level-1 (suppressed)
        # No output - completely silent
        
        return self
    def down(self, exit_msg: Union[str, bool] = False):
        """Decrease indentation level and display scope completion with timing.
        
        Closes the current scope level, calculates elapsed time, and displays 
        completion message based on DEBUG level. Should match every up() call.
        
        Output behavior:
        - DEBUG > new_level: Show full closure with bracket/separator and timing
        - DEBUG == new_level: Complete the "..." message with inline exit_msg and timing
        - DEBUG < new_level: Suppress all output
        """
        # Handle skip mechanism: if skip was set for the level above current,
        # clear the skip flag and bypass this down() call
        if self._skip_next:
            self._skip_next -= 1
            if self._skip_next == 1:
                self._skip_next = False
                return self
            elif self._skip_next == 0:
                self.warning("down() was called after skip().")
                self._skip_next = False
            
            
        if self.level == 0:
            self.warning(f"down() called from level 0 with header '{self._header_level[0]}'. Previous headers: {self._header_level}")
        # Calculate timing and retrieve scope information
        t_span: float = tm.time() - self._time_level[self.level]  # Time elapsed in this scope
        header = self._header_level[self.level]                   # Header for this scope
        self.l_count += 1  # Increment line count for this scope
        
        # Handle method tracking: stop tracking if we're closing the tracked scope
        if self.level == self._tracking:
            self._tracking = False
            self.DEBUG = 0  # Reset debug level when tracking ends
        
        # Accumulate timing history for performance analysis (if enabled)
        if self._h_log:
            # Track call count and total time per header type
            self._timelog.setdefault(header, [0, 0])
            self._timelog[header][0] += 1      # Increment call count
            self._timelog[header][1] += t_span # Add elapsed time
        
        current_prefix = self.prefix  # Save current prefix for output alignment
        # Decrement the indentation level (handles bounds checking)
        self._set_level(self.level - 1)
        new_level = self.level  # This is the level we're returning to
        
        # Skip output if globally muted
        if self.muted:
            return self
        
        # Output formatting based on DEBUG level relative to new level:        
        # Case 1: DEBUG > new_level (verbose mode - show full closure): display complete scope closure with decorative elements and timing
        if self.DEBUG > new_level:
            # Only show closure if the scope had a meaningful header
            if header != "...":
                rnd_end = np.random.choice(self.sep_ends)
                
                # Default exit message if none provided
                if exit_msg is False:
                    exit_msg = "───"
                
                # Close any active itemized list before printing scope end
                self.addItem(None)
                
                # Print scope completion using ORIGINAL level's prefix for proper alignment
                print(f"{current_prefix[:-1]}╰{self.lines_sep[0][:20]} {exit_msg} {rnd_end}  • {t2str(t_span)}", end=" ", flush=True)
                self.blank()  # Add a blank line after the closure for readability
        
        # Case 2: DEBUG == new_level (minimal mode - complete the "..." message)
        # Show inline completion for the scope that was opened with "header..."
        elif self.DEBUG == new_level:
            # Only show completion if the scope had a meaningful header
            if header != "...":
                if exit_msg is False:
                    # No explicit exit message - just show success tick and timing
                    self.inline(f"done  • {t2str(t_span)}")
                else:
                    # Show provided exit message with timing
                    self.inline(f"{exit_msg}  • {t2str(t_span)}")
                    
        # Case 3: DEBUG < new_level (suppressed)
        # No output - completely silent
        
        return self
    def skip(self):
        """Track the next level increase and skip it.
        
        Sets up a mechanism to bypass the next up()/down() pair's OUTPUT ONLY. 
        When skip() is called, it records the current level. The subsequent up() 
        call at this level will suppress its visual output (no header display), 
        and the matching down() call will also suppress its completion message.
        
        IMPORTANT: The level changes still occur internally - only the visual 
        output is suppressed. Nested logging calls between the skipped up/down 
        pair will work normally and use the incremented level for indentation.
        
        Example:
            log.skip()      # Mark current level for skipping output
            log.up("test")  # Level increments, but no visual header shown
            log("msg")      # This shows normally at the incremented level
            log.down()      # Level decrements, but no completion message shown
        """
        if not self._skip_next:
            # Record the current level where skip was requested
            self._skip_next = 1
        else:
            self.warning("skip() already set, ignoring.")
        return self
    
    # ──────────────────────────────────────────────── mute / un‑mute ──
    def mute(self):
        """Silence all output until :py:meth:`unmute` is called."""
        if not self.muted:
            self.muted = True
            self._mute_level = self.level
        return self
    def unmute(self):
        """Re‑enable output (idempotent)."""
        if self.muted and (self._mute_level is None or self.level <= self._mute_level):
            self.muted = False
            self._mute_level = None
        return self

    # ────────────────────────────────────────────────────── setters ──
    def _set_level(self, new_level: int):
        """Internal helper for clamping + state update.
        
        Safely updates the current indentation level with bounds checking,
        and updates the visual prefix string for consistent output formatting.
        """
        # Clear the header for the current level before changing
        # self._header_level[self.level] = "..."
        
        # Bounds checking with user warnings
        if new_level >= self.n_buffer:
            self.warning(f"Log level {new_level} exceeds buffer size {self.n_buffer}. Clamping to {self.n_buffer - 1}.")
        elif new_level < 0:
            # self.warning(f"Log level {new_level} is below 0. Clamping to 0.")
            new_level = 0

            
        # Apply bounds: clamp between 0 and n_buffer-1
        self.level = min(new_level, self.n_buffer - 1)
        
        # Update visual prefix: base "\n  " + vertical bars for each indentation level
        # Example: level 0 = "\n  ", level 1 = "\n   │", level 2 = "\n   │ │", etc.
        self.prefix = "\n  " + " │" * self.level if self.level else "\n  "
        return self
    def set_level(self, new_level: int): # public wrapper kept for compatibility
        return self._set_level(new_level)
    def ground(self):
        """Reset to root level (0) and clear all state except DEBUG."""
        self.reset()._set_level(0)

        return self
    def set_style(self, style: str):
        """ Set the style of the log output.
            Available styles:
            - "reinassance": Uses ornate ASCII art separators.
            - "minimal": Uses simple horizontal lines as separators.
        """
        if style == "reinassance":
            # ascii‑art separators
            self.separators = [
                '--=---===--==--=---==-',
                '-=---=-===-==----===-=-',
                '--=-====-----=-===---=-',
                '-==--=----===-=---==--=-',
                '--==-=---==--=---==---=-',
                '--=---==-===----==-=--=-',
            ]
            self.sep_ends = [
                '-=--',
                '-==-=--',
                '-==-=--=',
                '-==-=---=',
                '---==---=',
                '-=-==---=',
                '---==-=--=',
                '-==-=-----=-',
                '-=-==---===--=',
                '-===-=-----==-',
                '-==-----=-==--=',
                '-===-=-----=-==',
                '-===----==-=--=',
                '-==--==---=-',
            ]
            self.lines_sep = [
            "===----=-===-==----===-=-----==--===-----=--==-----=-===--=------="
            "====--=-----==-=-==----===---==---=-==---===-=----===----=-------="
            "===-==----=----==-===--=------===-==--=-----===--=------===-=---=-"
            "===--=---==---===--==-------==----===--=---==----===---==-------=="
        ]
            self.short_sep = "--=-=="
        elif style == "minimal":
            self.separators = ['──────────────────────']
            self.sep_ends = ['─────────', '─────── -']
            self.short_sep = '─'
            self.lines_sep = ['────────────────────────────────────────────']
        else:
            raise ValueError(f"Unknown style: {style}. Available styles: 'reinassance', 'minimal'.")
        return self
    def set_debug_level(self, level: int):
        self.DEBUG = max(level, -1)
        return self
    def reset(self):
        """Return to pristine state (except *DEBUG*)."""
        debug_saved = self.DEBUG  # preserve verbosity
        self.__init__(self.logpath, self.n_buffer)
        self.DEBUG = debug_saved
        return self

    # ──────────────────────────────────────────────── logging api ──
    def log(self, message: str):
        if self.softflag:
            self.softflag = False
            self.blank()
        self._streamConsole(f"{self.prefix} {message}")
        return self
    def warning(self, message: str):
        if self.DEBUG >= self.level:
            self(f"⛔ {message}")
        else:
            tree_str = "/".join(self._header_level[: self.level + 1]) + "/"
            print(f"\n⛔ in {tree_str}:\n ─────> {message}")
        return self
    def softlog(self, message: str):
        if self.muted or self.DEBUG < self.level:
            return self
        if self.softflag:
            self._streamConsole(f"{self.prefix}{message}")
        else:
            self._streamConsole(f"{self.prefix}{message}", end="\r")
            self.softflag = True
        return self

    # ───────────────────────────────────────────── misc loggers ──
    def header(self, header: str):
        """Prints a decorated header of somewhat bigger size, and resets level to 0."""
        if self.muted or self.DEBUG < self.level:
            return self
        
        # Reset to root level for headers
        self._set_level(0)
        
        # ANSI escape codes for enhanced aesthetics
        BOLD = '\033[1m'
        BRIGHT_CYAN = '\033[96m'
        BRIGHT_YELLOW = '\033[93m'
        BRIGHT_MAGENTA = '\033[95m'
        RESET = '\033[0m'
        DIM = '\033[2m'
        
        # Create dynamic separators using existing patterns
        header_len = len(header)
        total_width = max(80, header_len + 20)
        
        # Top ornamental border with random separator
        top_sep = np.random.choice(self.separators) if hasattr(self, 'separators') else "═══════════"
        top_border = (top_sep * 3)[:total_width]
        
        # Create side ornaments
        left_ornament = "▓▒░"
        right_ornament = "░▒▓"
        
        # Mathematical/technical symbols for extra flair
        symbols = "∫∑∇∆∂αβγδθλμπσφω⚡⚙⌬◊◈◇"
        accent_symbol = np.random.choice(list(symbols))
        
        # Main header construction with Unicode art
        padding = (total_width - header_len - 8) // 2
        center_line = f"▓▒░{' ' * padding}{accent_symbol} {BOLD}{BRIGHT_CYAN}{header.upper()}{RESET} {accent_symbol}{' ' * padding}░▒▓"
        
        # Bottom border with different pattern
        bottom_sep = np.random.choice(self.sep_ends) if hasattr(self, 'sep_ends') else "─────"
        bottom_pattern = f"╰─{bottom_sep}{'─' * (total_width - len(bottom_sep) - 4)}{bottom_sep[::-1]}─╯"
        
        # Assemble the complete header
        print(f"\n{BRIGHT_YELLOW}╭{'─' * (total_width - 2)}╮{RESET}")
        print(f"{BRIGHT_YELLOW}│{RESET}{BRIGHT_MAGENTA}{top_border[:total_width-2]}{RESET}{BRIGHT_YELLOW}│{RESET}")
        print(f"{BRIGHT_YELLOW}│{RESET}{center_line[:total_width-2]}{BRIGHT_YELLOW}│{RESET}")
        print(f"{BRIGHT_YELLOW}│{RESET}{DIM}{' ' * (total_width-2)}{RESET}{BRIGHT_YELLOW}│{RESET}")
        print(f"{BRIGHT_YELLOW}{bottom_pattern}{RESET}")
        print(f"{DIM}   ◊ TransFusion Multi-Sensor Data Fusion System ◊{RESET}\n", flush=True)
        
        return self
        
    def inline(self, message: str):
        if not self.muted and self.DEBUG >= self.level:
            print(f" {message}", end="", flush=True)
        return self
    
    def blank(self):
        if not self.muted:
            self.log(" ")
        return self
    def hline(self, title: str = None, len: int = 50):
        """Print a horizontal line with an optional title."""
        if not self.muted and self.DEBUG >= self.level:
            if title is None:
                self(f"   {np.random.choice(self.lines_sep)[:len]}")
            else:
                sep1 = np.random.choice(self.lines_sep)[:20]
                sep2 = np.random.choice(self.lines_sep)[:20]
                self(f"   {sep1[::-1]} {title} {sep2}")
        return self
    
    
    def itemize(self, items:List|Dict, header: str = "items", n_wrap: int = 50):
        if not self.muted and self.DEBUG >= self.level:
            if isinstance(items, dict):
                items = [f"{k}: {v}" for k, v in items.items()]

            self.addItem(header, n_wrap)
            for it in items:
                self.addItem(it, n_wrap)
            self.addItem(None)
        return self
    def addItem(self, item: Optional[str], n_wrap: int = 40):
        # Create a global variable to store the indent positions
        global n_indent

        if self.muted or self.DEBUG < self.level:
            return self
        if item is None:
            if self.cumline is not None:
                self.log(self.cumline[:-2] + "]")
                self.cumline = None
            return self
        if self.cumline is None:
            self.cumline = f"• {item}: ["
            n_indent = len(self.cumline)
            self.softflag = True
            return self
        add = f"{item}; "
        if len(self.cumline) + len(add) > n_wrap:
            self.log(self.cumline)
            self.cumline = " " * n_indent + add
        else:
            self.cumline += add
        return self
    
    def list(self, items: List|Dict, 
         header: str = "items", 
         style: str = "dash",
         numbered: bool = False,
         indent_items: int = True,
         max_width: int = None,
         show_count: bool = False,
         filter_empty: bool = True,
         sort_items: bool = False,
         group_by_type: bool = False,
         compact: bool = False,
         color_code: bool = False):
        """
        Enhanced list method with rich formatting options.
        
        Args:
            items: List or Dict to display
            header: Header text for the list
            style: List style - "bullet", "arrow", "dash", "number", "roman", "custom"
            numbered: Force numbering (overrides style)
            indent_items: Custom indentation for items (auto-calculated if None)
            max_width: Maximum width for item text (wraps if exceeded)
            show_count: Show total count in header
            filter_empty: Remove None/empty items
            sort_items: Sort items alphabetically
            group_by_type: Group items by their type
            compact: Single-line format for short lists
            color_code: Use different markers for different value types
        """
        if self.muted or self.DEBUG < self.level:
            return self

        # Process items
        if isinstance(items, dict):
            # Pre-analyze keys to determine optimal tab alignment
            max_key_length = max(len(str(k)) for k in items.keys()) if items else 0
            formatted_items = []
            for k, v in items.items():
                key_str = str(k)
                padding = ' ' * (max_key_length - len(key_str) + 2)  # +2 for consistent spacing
                formatted_items.append(f"{key_str}:{padding}{v}")
            items = formatted_items
        
        # Filter empty items if requested
        if filter_empty:
            items = [item for item in items if item is not None and str(item).strip()]
        
        # Sort if requested
        if sort_items:
            items = sorted(items, key=str)
        
        # Group by type if requested
        if group_by_type:
            items = self._group_items_by_type(items)
        
        header_sep = "⚙"     
        # header_sep = header_sep[:min(4, len(header_sep))]
        # Calculate indentation based on current level
        if indent_items:
            base_indent = ""
            item_indent = " " * (len(header_sep) + 5)+ "├"  # Indentation for items
        else:
            base_indent = ""
            item_indent = " " * 3  # Default indentation for items

        # Show count in header if requested
        count_suffix = f" ({len(items)} items)" if show_count else ""
        
        # Check for compact mode
        if compact and len(items) <= 3 and all(len(str(item)) < 20 for item in items):
            self.itemize(items, header, n_wrap=max_width)
            return self
        
        # Print header with decorative elements
        if show_count: 
            self.log(f"{base_indent}{header_sep} {header}: {count_suffix} elements ")
        else:
            self.log(f"{base_indent}{header_sep} {header}:")
        
        # Process each item
        for i, item in enumerate(items):
            marker = self._get_list_marker(i, style, numbered, color_code, item)
            formatted_item = self._format_list_item(str(item), max_width, item_indent)
            if i == 0:
                self.log(f"{item_indent[:-8]}    ╰─┬{marker} {formatted_item}")
            else:
                self.log(f"{item_indent}{marker} {formatted_item}")
        self.log(f"{item_indent[:-1]}╰───────────")
        return self
    def _group_items_by_type(self, items):
        """Group items by their type and return organized list."""
        from collections import defaultdict
        groups = defaultdict(list)
        
        for item in items:
            if isinstance(item, str) and ":" in item:
                key, value = item.split(":", 1)
                try:
                    # Try to determine type from value
                    val = value.strip()
                    if val.replace(".", "").replace("-", "").isdigit():
                        groups["Numbers"].append(item)
                    elif val.lower() in ["true", "false"]:
                        groups["Booleans"].append(item)
                    else:
                        groups["Strings"].append(item)
                except:
                    groups["Mixed"].append(item)
            else:
                groups["Items"].append(item)
        
        # Flatten groups with headers
        result = []
        for group_name, group_items in groups.items():
            if len(groups) > 1:  # Only show group headers if multiple groups
                result.append(f"[{group_name}]")
            result.extend(group_items)
        
        return result
    def _get_list_marker(self, index: int, style: str, numbered: bool, color_code: bool, item):
        """Generate appropriate list marker based on style and options."""
        if numbered or style == "number":
            return f"{index + 1}."
        elif style == "roman":
            roman_nums = ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"]
            return f"{roman_nums[min(index, 9)]}."
        elif style == "arrow":
            return "→"
        elif style == "dash":
            return "─"
        elif color_code and isinstance(item, str) and ":" in item:
            # Color code based on value type
            value = item.split(":", 1)[1].strip()
            if value.replace(".", "").replace("-", "").isdigit():
                return "▲"  # Numbers
            elif value.lower() in ["true", "false"]:
                return "◆"  # Booleans
            else:
                return "●"  # Strings
        elif style == "custom":
            # Use random separator elements for artistic effect
            if hasattr(self, 'separators'):
                custom_chars = ["•", "▪", "▫", "‣", "⁃"]
                return np.random.choice(custom_chars)
            return "•"
        else:  # bullet (default)
            return "•"
    def _format_list_item(self, item: str, max_width: int, indent: str) -> str:
        """Format individual list item with optional width wrapping."""
        if max_width is None:
            return item
        
        if len(item) <= max_width:
            return item
        
        # Simple word wrapping
        words = item.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= max_width:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(" ".join(current_line))
        
        # Join with proper indentation for continuation lines
        continuation_indent = " " * (len(indent) + 2)
        return f"\n{continuation_indent}".join(lines)

    def tree(self, data: Dict, header: str = "tree", 
        show_types: bool = False, max_depth: int = None):
        """
        Display nested dictionary/object as an indented tree structure.
        
        Args:
        data: Dictionary or nested structure to display
        header: Header for the tree
        show_types: Show type information for values
        max_depth: Maximum depth to traverse
        """
        if self.muted or self.DEBUG < self.level:
            return self

        # Root level - show header with decorative elements
        self.log(f"⚙ {header}")

        # Calculate base indentation based on current level
        base_indent = " " * min(len(header), 2)

        # No data or empty container
        if not data:
            self.log(f"{base_indent}╰─ (empty)")
            return self
        
        # Process the nested structure recursively with proper indentation tracking
        self._tree_recursive(data, base_indent, " ", "", False, 0, max_depth, show_types)
        
        # Add closing line at root level
        self.blank()
        
        return self
    def _tree_recursive(self, data, level_indent,
                        parent_indent, connector,
                        is_last_branch, depth,
                        max_depth, show_types):
        """Helper method for tree() to handle nested recursion with proper indentation."""
        # Stop if we've reached max depth
        if max_depth is not None and depth > max_depth: return        
        # No data or empty container
        if not data:    return       
        
        # Calculate this level's indentation
        base_indent = parent_indent + connector + " " * 3
        # Process each item
        items = list(data.items() if isinstance(data, dict) else enumerate(data))
        last_idx = len(items) - 1
        
        for i, (key, value) in enumerate(items):
            # Determine if this is the last item at this level
            is_last = i == last_idx
            is_first = i == 0

            
            this_indent = base_indent if is_first else base_indent
            
            # Choose the right branch character based on position
            branch = " ╰─" if is_last else ("╰┬" if is_first else " ├─")
            
            # Create next level's connector
            next_connector = "   " if is_last else " │ "
            
            # Handle nested dictionary
            if isinstance(value, dict) and value:
                type_info = f" ({type(value).__name__})" if show_types else ""
                self.log(f"{level_indent}{this_indent}{branch}◻ {key}{type_info}")
                
                # Recursively process nested data
                self._tree_recursive(value, level_indent, this_indent, 
                                  next_connector, is_last, depth + 1, 
                                  max_depth, show_types)
            
            # Handle list/array
            elif isinstance(value, (list, tuple)) and value:
                count_info = f"[{len(value)} items]"
                type_info = f" ({type(value).__name__})" if show_types else ""
                self.log(f"{level_indent}{this_indent}{branch} {key}{type_info} {count_info}:")
                
                # Process list items
                for j, item in enumerate(value):
                    item_is_last = j == len(value) - 1
                    item_branch = " ╰─" if item_is_last else " ├─"
                    item_type = f" ({type(item).__name__})" if show_types else ""
                    self.log(f"{level_indent}{this_indent}{next_connector}{item_branch} {item}{item_type}")
            
            # Handle leaf node
            else:
                type_info = f" ({type(value).__name__})" if show_types else ""
                self.log(f"{level_indent}{this_indent}{branch} {key}: {value}{type_info}")
    # ─────────────────────────────────────────────────── filtering ──
    def trackMe(self, header: str = "Tracked", debug_level: int = 1):
        if self._tracking:
            return self
        self.reset()
        self.DEBUG = debug_level
        self.up(header + "(tracking)")
        self._tracking = self.level
        return self
    def log_history(self, active: bool = True):
        if active == self._h_log:
            return self
        if active:
            self.log("Initialising History Log…")
        self._h_log = bool(active)
        return self
    
    # ───────────────────────────────────── low‑level console sink ──
    def _streamConsole(self, message: str, end: str = ""):
        if self.muted:
            return self
        if self.softflag and end != "\r":
            self.softflag = False
            self.addItem(None)
        if self.DEBUG >= self.level:
            print(message, end=end, flush=True)
        return self

class ConsoleTable:
    def __init__(self,
                 headers: list,
                 log: Log = None,
                 formats: list = None,
                 header: str = "",
                 compact: bool = False):
        """
        Initializes the ConsoleTable with a list of headers and an optional list of formats.
        The width of each column is determined by the maximum length of its header.
        Prints the headers right away.

        :param headers: List of column headers
        :param log: Log instance for logging the table data
        :param formats: Optional list of string formats (e.g., ':.2f', ':.0%', etc.)
        :param padding: Padding between columns
        :param margin: Margin around the table
        """
        if log is None:
            log = Log()
        self.log: Log = log
        log.blank()
        # define headers and formats
        self.headers: list = headers
        self.formats: list = formats if formats else ['{}'] * len(headers)

        # check formats and headers length
        if len(self.formats) != len(self.headers):
            raise ValueError("Number of formats must match the number of headers.")

        # define padding and margin
        self.sep = " │ "
        self.margin:        str     = "│ "        # Margin for the table
        self.padding:       int     = 0     # Padding for each column

        # Calculate widths based on headers
        self.min_width: int = 5  # Minimum width for each column
        self.col_widths: list    = [max(self.min_width, len(header))
                                       for header in headers]
        self.rows:          list    = []

        self.width = None
        if compact:
            # If compact mode is enabled, use a single space as padding
            self.sep = " "
            self.margin = "│"
            # Substitute every space in headers for underbars _
            self.headers = [header.replace(" ", "_") for header in self.headers]
            # Print headers immediately when the table is initialized   
            self.__print_headers(header)
        else:
            self.__print_headers(header)
    def add_row(self, *args):
        """ As input, accepts either as many positional arguments as there are headers"""

        # If its a collection of keyword arguments, convert to list
        row = [arg for arg in args]
        if len(row) != len(self.headers):
            raise ValueError("Row length does not match the number of headers.")

        # Format the row values and calculate widths
        row = [self.formats[i].format(item) for i, item in enumerate(row)]

        # Update column widths if necessary
        self.col_widths = [max(self.col_widths[i], len(row[i]), self.min_width)
                           for i in range(len(row))
        ]

        # Store the formatted row (if needed later)
        self.rows.append(row)

        # Print the newly added row
        self.__print_row(row)
    def close(self):
        """ Closes the table by printing a closing line."""
        self.log(f"╰{'─'*(self.width - 2)}╯").blank()
        return self
    # private methods
    def __add_padding(self, side: str = "right") -> str:
        "Adds padding to the headers or rows based on the specified side."
        pad = self.padding * " "
        if side == "right":
            self.headers = [header + pad for header in self.headers]
        elif side == "left":
            self.headers = [pad + header for header in self.headers]
        elif side == "both":
            self.headers = [pad + header + pad for header in self.headers]
        self.col_widths: list    = [max(len(header), self.min_width)
                                       for header in self.headers]

    def __print_headers(self, header: str):
        """Prints the headers of the table."""
        cols_str    = self.sep.join(header.center(self.col_widths[i])
                                 for i, header in enumerate(self.headers))
        cols_str    = self.margin + cols_str + self.margin[::-1]
        self.width  = len(cols_str)

        line_len     = self.width - (len(header) + 4)
        line         = np.random.choice(self.log.lines_sep)[:line_len//2]        
        header_str  = f"╭{line} {header} {line}╮"
        blank_str   = f"│{' '*(self.width-2)}│"
        
        self.log(header_str).log(blank_str).log(cols_str)
    def __print_row(self, row):
        """
        Prints a single row of data with the appropriate spacing.
        :param row: The row of formatted data to print
        """
        self.log(self.margin + self.sep.join(str(item).center(self.col_widths[i]) for i, item in enumerate(row)) + self.margin[::-1])

class progressBar:
    """ A class to handle an inline progress bar using the Log instance.

    Attributes:
        log (Log): The Log instance used for output.
        total_length (int): Total number of bars representing 100% progress.
        current_bars (int): The number of bars currently printed.
        closed (bool): Whether the progress bar has been closed.
    """
    def __init__(self, log: Log, total_length: int = 60, header: str = "progress"):
        """
        Initializes the progress bar with a Log instance and total length.
        Args:
            log (Log): The Log instance used for output.
            total_length (int): Total number of bars representing 100% progress.
            header (bool): Whether to print a header line before the bar.
        """
        self.log = log
        self.total_length = int(total_length)
        self.current_bars = 0
        self.closed = False
        self._header_printed = header  # Track if header was printed
        # Initialize the progress bar with header if requested.
        self.bars_samples = [
                            # '█', '▌', '▐', '▌', '█',
                            # '▓', '▒', '░',
                            # Low, single character bars
                            '█', '▇', '▆', '▅', '▄', '▃', '▂', '▁',

                            # Thiner bars
                            '▇', '▆', '▅', '▄', '▃', '▂', '▁',
                            # Thinner bars with different styles
                            # '▊', '▋', '▍', '▎', '▏', '▕',
                            # Empty bars
                            '■', '□']
        # self.char_bar = np.random.choice(self.bars_samples, 1)[0]
        if header:
            self.header(header)
        
        self.log("├ ")
    def update(self, progress_factor: float):
        """
        Updates the progress bar by printing any additional bars.

        Args:
            progress_factor (float): A number between 0 and 1 indicating progress.
                                    When >= 1, the progress bar closes automatically.
        """
        if self.closed:
            return
        # Determine the number of bars that should now be printed.
        new_bars = int(progress_factor * self.total_length)
        additional = new_bars - self.current_bars
        if additional > 0:
            self.bars(additional)
            self.current_bars = new_bars
        # Auto-close if complete.
        if progress_factor >= 1.0:
            self.close()
    def bars(self, n_bars: int = 1):
        """
        Adds a specified number of bars to the progress bar.

        Args:
            n_bars (int): The number of bars to add.
        """
        if self.log.DEBUG >= self.log.level:
            n_bars = int(n_bars)
            print('▄' * n_bars, end="")
        return self
    def header(self, title: str = "progress"):
        """
        Logs a line before the bar, with indicators at the initial and final positions.
        For example:
        0%__________________________________________________100%
        [ ================================================== ]
        """
        if self.closed:
            return
        sep_half = ' ' * floor((self.total_length - len(title)) / 2 + 1)
        box_top = f"╭{'─' * (self.total_length + 2)}╮"
        box_len = len(box_top)
        half_title = f"│ 0%{sep_half[:-3]}{title}"
        self.log(box_top).log(half_title + " " * (box_len - len(half_title) - 6) + "100% │")
        
        self.current_bars = 0
    def close(self):
        """
        Closes the progress bar by printing any remaining bars and finishing the line.
        """
        if self.closed: return
        debug_ok = self.log.DEBUG >= self.log.level
        if self.current_bars < self.total_length and debug_ok:
            self.bars(self.total_length - self.current_bars)
        self.closed = True
        if self.log.DEBUG == 0:
            return self
        elif debug_ok:
            print(" ┤", end="")
            self.log(f"╰{'─' * (self.total_length + 2)}╯")

    def remove(self):
        """
        Removes the progress bar and header lines from the console.
        This method uses ANSI escape sequences to move the cursor up and clear the lines.
        """
        # Ensure the progress bar is closed.
        if not self.closed:
            self.close()
        # Simply compute how many characters to remove and do. Assume we just printed the closing bracket and nothing else.
        n_lines = 2 + self.current_bars // self.total_length
        n_chars = self.total_length + 2
        # Move the cursor up and clear the lines.
        print(f"\033[F\033[K" * n_lines, end="", flush=True)
        # Reset the current bars to 0.
        self.current_bars = 0

# ─────────────────────────────────────────────────────────────────────────────
# Utility
# ─────────────────────────────────────────────────────────────────────────────
def t2str(time_val):
    """Convert a time value to a string, reporting second, minutes, hours or days depending on the magnitude."""
    if   time_val < 60: return f"{time_val:.1f}s"
    elif time_val < 3600: return f"{time_val/60:.1f}m"
    elif time_val < 24*3600: return f"{time_val/3600:.1f}h"
    elif time_val < 30*24*3600: return f"{time_val/(24*3600):.1f}d"
    elif time_val < 365*24*3600: return f"{time_val/(30*24*3600):.1f}mo"
    else: return f"{time_val/(365*24*3600):.1f}y"
def toggle(script_dir: str | os.PathLike,
           comment: bool = True,
           prefix : str = "log",
           backup : bool = True,
           indent_comment : str = "# ",
           verbose: bool = True) -> None:
    """
    Comment-out (or restore) *all* references to the logging helpers so that
    colleagues can run the code without the extra dependency *and* you can
    re-enable them later with one call.

    Parameters
    ----------
    script_dir : str | Path
        A single *.py* file or a directory that will be scanned **recursively**.
    comment : bool, default *True*
        • *True*  → prepend `# ` to every matching line.<br>
        • *False* → remove the *first* `#` if the rest of the line still matches.
    prefix : str, default ``"log"``
        Assumed variable name of the `Log()` instance in your scripts.
    backup : bool, default *True*
        Writes a sibling file *<name>.bak* before modifying anything.
    indent_comment : str, default ``"# "``
        Text that will be prepended when commenting out.
    verbose : bool
        Prints a tiny report to *stdout*.
    """
    p_dir = pathlib.Path(script_dir)
    if p_dir.is_file() and p_dir.suffix == ".py":
        files = [p_dir]
    else:
        files = list(p_dir.rglob("*.py"))

    # Regex: any line containing  log.<something>(   or   ConsoleTable(   …
    patt = re.compile(
        rf"""
        (^[ \t]*)                    # 1. existing left indent
        (                            #    start of the "interesting" chunk
            (?:{re.escape(prefix)}\s*\.)      #   log.…
          | ConsoleTable\s*\(                #   ConsoleTable(
          | progressBar\s*\(                 #   progressBar(
        ).*$
        """, re.X)

    changed = 0
    for fp in files:
        txt = fp.read_text(encoding="utf-8").splitlines(keepends=False)
        out = []

        for ln in txt:
            m = patt.match(ln.lstrip("# ").rstrip())   # test line *without* leading comment
            if comment:                      # ── we are disabling logging ──
                if m and not ln.lstrip().startswith("#"):
                    ln = m.group(1) + indent_comment + ln[len(m.group(1)):]  # keep indentation
                    changed += 1
            else:                            # ── we are enabling logging ──
                if ln.lstrip().startswith("#"):
                    core = ln.lstrip()[1:]       # remove first '#'
                    if patt.match(core.lstrip()):
                        # rebuild: keep left indent, drop the first '#'
                        indent = len(ln) - len(ln.lstrip())
                        ln = " " * indent + core.lstrip(" ")

                        changed += 1
            out.append(ln)

        if changed:
            if backup:
                shutil.copy(fp, fp.with_suffix(fp.suffix + ".bak"))
            fp.write_text("\n".join(out) + "\n", encoding="utf-8")

    if verbose:
        action = "commented" if comment else "restored"
        print(f"[toggle] {changed} lines {action} across {len(files)} file(s).")
def validate_updown(file_path: str,
                                up_name: str = "up",
                                down_name: str = "down"
                                ) -> List[Tuple[str, int]]:
    """
    Report every function/method whose `log.up()` / `log.down()` calls
    are not balanced.

    Parameters
    ----------
    file_path : str | Path
        Python source file to inspect.
    up_name / down_name : str
        Attribute names to look for (override only if you renamed them).

    Returns
    -------
    list[tuple[str, int]]
        • `qualified_name`  – “Class.method” or bare function name  
        • `delta`           – **ups − downs**  
          ( +ve ≡ missing `down()`, −ve ≡ extra `down()` )
    """
    import ast
    from pathlib import Path
    from typing import List, Tuple
    src = Path(file_path).read_text(encoding="utf-8")
    tree = ast.parse(src, filename=str(file_path))
    report: list[tuple[str, int]] = []

    class Visitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.cls_stack: list[str] = []

        # keep track of the class we are in
        def visit_ClassDef(self, node: ast.ClassDef):
            self.cls_stack.append(node.name)
            self.generic_visit(node)
            self.cls_stack.pop()

        def visit_FunctionDef(self, node: ast.FunctionDef):
            counts = {"up": 0, "down": 0}

            class CallCounter(ast.NodeVisitor):
                def visit_Call(self, call: ast.Call):  # noqa: N802
                    if isinstance(call.func, ast.Attribute):
                        attr = call.func.attr
                        if attr == up_name:
                            counts["up"] += 1
                        elif attr == down_name:
                            counts["down"] += 1
                    self.generic_visit(call)

            CallCounter().visit(node)

            delta = counts["up"] - counts["down"]
            if delta:                    # record only if unbalanced
                qname = ".".join(self.cls_stack + [node.name]) if self.cls_stack else node.name
                report.append((qname, delta))

            # still descend to nested defs
            self.generic_visit(node)

    Visitor().visit(tree)
    return report



# -*- coding: utf-8 -*-
"""
Debug Characters Reference Library
==================================

Comprehensive collection of Unicode special characters for enhanced debug aesthetics
in structural monitoring applications. Use these characters to create visually 
appealing separators, borders, indicators, and hierarchical structures in console output.

Author: TransFusion Development Team
License: Commercial - CoreMarine
"""

class DebugChars:
    """
    Extensive Unicode character collection for debug output aesthetics.
    Organized by category for easy selection and consistent styling.
    """
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # BOX DRAWING CHARACTERS - Perfect for frames and separators
    # ═══════════════════════════════════════════════════════════════════════════════
    
    # Single line box drawing
    SINGLE = {
        'horizontal': '─',      # ─
        'vertical': '│',        # │
        'bottom_horizontal': '─',  # ─
        'top_left': '┌',        # ┌
        'top_right': '┐',       # ┐
        'bottom_left': '└',     # └
        'bottom_right': '┘',    # ┘
        'cross': '┼',           # ┼
        'tee_up': '┴',          # ┴
        'tee_down': '┬',        # ┬
        'tee_left': '┤',        # ┤
        'tee_right': '├',       # ├
    }
    
    # Double line box drawing
    DOUBLE = {
        'horizontal': '═',      # ═
        'vertical': '║',        # ║
        'top_left': '╔',        # ╔
        'top_right': '╗',       # ╗
        'bottom_left': '╚',     # ╚
        'bottom_right': '╝',    # ╝
        'cross': '╬',           # ╬
        'tee_up': '╩',          # ╩
        'tee_down': '╦',        # ╦
        'tee_left': '╣',        # ╣
        'tee_right': '╠',       # ╠
    }
    
    # Heavy line box drawing
    HEAVY = {
        'horizontal': '━',      # ━
        'vertical': '┃',        # ┃
        'top_left': '┏',        # ┏
        'top_right': '┓',       # ┓
        'bottom_left': '┗',     # ┗
        'bottom_right': '┛',    # ┛
        'cross': '╋',           # ╋
        'tee_up': '┻',          # ┻
        'tee_down': '┳',        # ┳
        'tee_left': '┫',        # ┫
        'tee_right': '┣',       # ┣
    }
    
    # Mixed line styles
    MIXED = {
        'double_horizontal_single_vertical': '╫',  # ╫
        'single_horizontal_double_vertical': '╪',  # ╪
        'heavy_horizontal': '━',                   # ━
        'light_vertical': '│',                     # │
    }
    
    # Rounded corners
    ROUNDED = {
        'top_left': '╭',        # ╭
        'top_right': '╮',       # ╮
        'bottom_left': '╰',     # ╰
        'bottom_right': '╯',    # ╯
    }
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # DASHES AND HYPHENS - Various lengths and styles
    # ═══════════════════════════════════════════════════════════════════════════════
    
    DASHES = {
        'hyphen': '-',              # - (ASCII hyphen)
        'minus': '−',               # − (mathematical minus)
        'en_dash': '–',             # – (en dash)
        'em_dash': '—',             # — (em dash)
        'horizontal_bar': '―',      # ― (horizontal bar)
        'double_hyphen': '⸗',       # ⸗
        'wave_dash': '〜',          # 〜
        'swung_dash': '⁓',         # ⁓
        'bullet_operator': '∙',     # ∙
        'middle_dot': '·',          # ·
        'interpunct': '‧',          # ‧
    }
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # ARROWS AND POINTERS - Directional indicators
    # ═══════════════════════════════════════════════════════════════════════════════
    
    ARROWS = {
        # Basic arrows
        'left': '←',               # ←
        'up': '↑',                 # ↑
        'right': '→',              # →
        'down': '↓',               # ↓
        'up_down': '↕',            # ↕
        'left_right': '↔',         # ↔
        'north_east': '↗',         # ↗
        'north_west': '↖',         # ↖
        'south_east': '↘',         # ↘
        'south_west': '↙',         # ↙
        
        # Double arrows
        'double_left': '⇐',        # ⇐
        'double_up': '⇑',          # ⇑
        'double_right': '⇒',       # ⇒
        'double_down': '⇓',        # ⇓
        'double_left_right': '⇔',  # ⇔
        'double_up_down': '⇕',     # ⇕
        
        # Heavy arrows
        'heavy_left': '⬅',         # ⬅
        'heavy_up': '⬆',           # ⬆
        'heavy_right': '➡',        # ➡
        'heavy_down': '⬇',         # ⬇
        
        # Curved arrows
        'curved_left': '↶',        # ↶
        'curved_right': '↷',       # ↷
        'curved_up_left': '↰',     # ↰
        'curved_up_right': '↱',    # ↱
        'curved_down_left': '↲',   # ↲
        'curved_down_right': '↳',  # ↳
        
        # Special arrows
        'loop_left': '↺',          # ↺
        'loop_right': '↻',         # ↻
        'refresh': '⟲',            # ⟲
        'reload': '⟳',             # ⟳
        'return': '↩',             # ↩
        'enter': '⏎',              # ⏎
        'tab': '⇥',                # ⇥
        'shift_tab': '⇤',          # ⇤
    }
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # BULLETS AND MARKERS - Status indicators and list markers
    # ═══════════════════════════════════════════════════════════════════════════════
    
    BULLETS = {
        'bullet': '•',             # •
        'white_bullet': '◦',       # ◦
        'black_circle': '●',       # ●
        'white_circle': '○',       # ○
        'large_circle': '⭕',      # ⭕
        'heavy_circle': '⚫',      # ⚫
        'medium_circle': '⚬',     # ⚬
        'small_circle': '∘',       # ∘
        'ring': '◯',               # ◯
        'dotted_circle': '◉',      # ◉
        'circled_dot': '⊙',        # ⊙
        'target': '⌖',             # ⌖
        
        # Squares
        'black_square': '■',       # ■
        'white_square': '□',       # □
        'small_black_square': '▪', # ▪
        'small_white_square': '▫', # ▫
        'medium_black_square': '◼',# ◼
        'medium_white_square': '◻',# ◻
        
        # Diamonds
        'black_diamond': '♦',      # ♦
        'white_diamond': '♢',      # ♢
        'black_diamond_suit': '♦', # ♦
        'white_diamond_suit': '♢', # ♢
        'small_diamond': '⋄',      # ⋄
        'lozenge': '◊',            # ◊
        
        # Triangles
        'black_triangle': '▲',     # ▲
        'white_triangle': '△',     # △
        'black_triangle_down': '▼',# ▼
        'white_triangle_down': '▽',# ▽
        'triangle_right': '▶',     # ▶
        'triangle_left': '◀',      # ◀
        'triangle_up_small': '▴',  # ▴
        'triangle_down_small': '▾',# ▾
        'triangle_right_small': '▸',# ▸
        'triangle_left_small': '◂',# ◂
    }
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # MATHEMATICAL SYMBOLS - For equations and formulas
    # ═══════════════════════════════════════════════════════════════════════════════
    
    MATH = {
        # Basic operations
        'plus': '+',               # +
        'minus': '−',              # −
        'multiply': '×',           # ×
        'divide': '÷',             # ÷
        'equals': '=',             # =
        'not_equals': '≠',         # ≠
        'approximately': '≈',      # ≈
        'identical': '≡',          # ≡
        'proportional': '∝',       # ∝
        
        # Comparisons
        'less_than': '<',          # <
        'greater_than': '>',       # >
        'less_equal': '≤',         # ≤
        'greater_equal': '≥',      # ≥
        'much_less': '≪',          # ≪
        'much_greater': '≫',       # ≫
        
        # Set theory
        'element_of': '∈',         # ∈
        'not_element': '∉',        # ∉
        'subset': '⊂',             # ⊂
        'superset': '⊃',           # ⊃
        'subset_equal': '⊆',       # ⊆
        'superset_equal': '⊇',     # ⊇
        'intersection': '∩',       # ∩
        'union': '∪',              # ∪
        'empty_set': '∅',          # ∅
        
        # Logic
        'and': '∧',                # ∧
        'or': '∨',                 # ∨
        'not': '¬',                # ¬
        'implies': '⇒',            # ⇒
        'iff': '⇔',                # ⇔
        'therefore': '∴',          # ∴
        'because': '∵',            # ∵
        
        # Calculus
        'infinity': '∞',           # ∞
        'partial': '∂',            # ∂
        'integral': '∫',           # ∫
        'sum': '∑',                # ∑
        'product': '∏',            # ∏
        'nabla': '∇',              # ∇
        'delta': 'Δ',              # Δ
        'gradient': '∇',           # ∇
        
        # Greek letters (commonly used)
        'alpha': 'α',              # α
        'beta': 'β',               # β
        'gamma': 'γ',              # γ
        'delta_small': 'δ',        # δ
        'epsilon': 'ε',            # ε
        'theta': 'θ',              # θ
        'lambda': 'λ',             # λ
        'mu': 'μ',                 # μ
        'pi': 'π',                 # π
        'sigma': 'σ',              # σ
        'tau': 'τ',                # τ
        'phi': 'φ',                # φ
        'omega': 'ω',              # ω
    }
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # SEPARATORS AND DIVIDERS - For visual organization
    # ═══════════════════════════════════════════════════════════════════════════════
    
    SEPARATORS = {
        'section': '§',            # §
        'pilcrow': '¶',            # ¶
        'double_dagger': '‡',      # ‡
        'dagger': '†',             # †
        'asterisk': '∗',           # ∗
        'bullet_op': '∙',          # ∙
        'centered_dot': '⋅',       # ⋅
        'dot_operator': '⋅',       # ⋅
        'ring_operator': '∘',      # ∘
        'vertical_bar': '|',       # |
        'double_vertical': '‖',    # ‖
        'broken_bar': '¦',         # ¦
        'ellipsis': '…',           # …
        'midline_ellipsis': '⋯',   # ⋯
        'vertical_ellipsis': '⋮',  # ⋮
        'diagonal_ellipsis': '⋱', # ⋱
    }
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # BRACKETS AND DELIMITERS - For grouping and hierarchy
    # ═══════════════════════════════════════════════════════════════════════════════
    
    BRACKETS = {
        # Standard brackets
        'paren_left': '(',         # (
        'paren_right': ')',        # )
        'square_left': '[',        # [
        'square_right': ']',       # ]
        'curly_left': '{',         # {
        'curly_right': '}',        # }
        'angle_left': '⟨',         # ⟨
        'angle_right': '⟩',        # ⟩
        
        # Mathematical brackets
        'ceiling_left': '⌈',       # ⌈
        'ceiling_right': '⌉',      # ⌉
        'floor_left': '⌊',         # ⌊
        'floor_right': '⌋',        # ⌋
        'double_square_left': '⟦', # ⟦
        'double_square_right': '⟧',# ⟧
        
        # Decorative brackets
        'ornate_left': '❮',        # ❮
        'ornate_right': '❯',       # ❯
        'white_paren_left': '⦅',   # ⦅
        'white_paren_right': '⦆',  # ⦆
    }
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # STATUS AND WARNING SYMBOLS - For system feedback
    # ═══════════════════════════════════════════════════════════════════════════════
    
    STATUS = {
        # Success indicators
        'check': '✓',              # ✓
        'heavy_check': '✔',        # ✔
        # Emoji checks:
        "check_mark": '✅',         # ✅
        "heavy_check_mark": '✔️',  # ✔️
        "heavy_green_mark": '🟢',  # 🟢
        'ballot_check': '☑',       # ☑
        'cross_mark': '✗',         # ✗
        'heavy_cross': '✘',        # ✘
        'ballot_cross': '☒',       # ☒
        
        # Warning symbols
        'warning': '⚠',            # ⚠
        'caution': '⚡',           # ⚡
        'error': '⛔',             # ⛔
        'stop': '🛑',              # 🛑
        'exclamation': '❗',       # ❗
        'double_exclamation': '‼', # ‼
        'question': '❓',          # ❓
        'grey_question': '❔',     # ❔
        
        # Information
        'info': 'ℹ',               # ℹ
        'note': '📝',              # 📝
        'lightbulb': '💡',         # 💡
        'gear': '⚙',               # ⚙
        'wrench': '🔧',            # 🔧
        'hammer': '🔨',            # 🔨
        
        # Process indicators
        'hourglass': '⏳',         # ⏳
        'clock': '🕐',             # 🕐
        'stopwatch': '⏱',         # ⏱
        'timer': '⏲',             # ⏲
        'refresh_symbol': '♻',     # ♻
        'recycle': '♲',            # ♲
        'loop': '🔄',              # 🔄
        'repeat': '🔁',            # 🔁
    }
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # GEOMETRIC SHAPES - For visual emphasis
    # ═══════════════════════════════════════════════════════════════════════════════
    
    SHAPES = {
        # Basic shapes filled
        'circle_filled': '●',      # ●
        'square_filled': '■',      # ■
        'diamond_filled': '♦',     # ♦
        'triangle_filled': '▲',    # ▲
        'star_filled': '★',        # ★
        'heart_filled': '♥',       # ♥
        'spade_filled': '♠',       # ♠
        'club_filled': '♣',        # ♣
        
        # Basic shapes outline
        'circle_outline': '○',     # ○
        'square_outline': '□',     # □
        'diamond_outline': '♢',    # ♢
        'triangle_outline': '△',   # △
        'star_outline': '☆',       # ☆
        'heart_outline': '♡',      # ♡
        
        # Polygons
        'pentagon': '⬟',          # ⬟
        'hexagon': '⬢',           # ⬢
        'octagon': '⬣',           # ⬣
        
        # Special shapes
        'flower': '❀',            # ❀
        'snowflake': '❄',         # ❄
        'sun': '☀',               # ☀
        'moon': '☽',              # ☽
        'cloud': '☁',             # ☁
        'umbrella': '☂',          # ☂
    }
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # TECHNICAL SYMBOLS - For engineering applications
    # ═══════════════════════════════════════════════════════════════════════════════
    
    TECHNICAL = {
        # Electrical
        'ohm': 'Ω',                # Ω
        'micro': 'μ',              # μ
        'degree': '°',             # °
        'prime': '′',              # ′ (feet, arcminutes)
        'double_prime': '″',       # ″ (inches, arcseconds)
        'triple_prime': '‴',       # ‴
        
        # Units and measurements
        'angstrom': 'Å',           # Å
        'celsius': '℃',            # ℃
        'fahrenheit': '℉',         # ℉
        'kelvin': 'K',             # K
        'pound': '℔',              # ℔
        'ounce': '℥',              # ℥
        
        # Physics
        'planck': 'ℏ',             # ℏ (reduced Planck constant)
        'euler': 'ℯ',              # ℯ (Euler's number base)
        'imaginary': 'ⅈ',          # ⅈ (imaginary unit)
        'real_part': 'ℜ',          # ℜ
        'imaginary_part': 'ℑ',     # ℑ
        
        # Structural engineering
        'force': 'F',              # F
        'moment': 'M',             # M
        'stress': 'σ',             # σ
        'strain': 'ε',             # ε
        'modulus': 'E',            # E
        'poisson': 'ν',            # ν
        'density': 'ρ',            # ρ
        'acceleration': 'a',       # a
        'velocity': 'v',           # v
        'displacement': 'u',       # u
    }
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # SUPERSCRIPTS AND SUBSCRIPTS - For mathematical notation
    # ═══════════════════════════════════════════════════════════════════════════════
    
    SUPER = {
        '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
        '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
        '+': '⁺', '-': '⁻', '=': '⁼', '(': '⁽', ')': '⁾',
        'a': 'ᵃ', 'b': 'ᵇ', 'c': 'ᶜ', 'd': 'ᵈ', 'e': 'ᵉ',
        'f': 'ᶠ', 'g': 'ᵍ', 'h': 'ʰ', 'i': 'ⁱ', 'j': 'ʲ',
        'k': 'ᵏ', 'l': 'ˡ', 'm': 'ᵐ', 'n': 'ⁿ', 'o': 'ᵒ',
        'p': 'ᵖ', 'r': 'ʳ', 's': 'ˢ', 't': 'ᵗ', 'u': 'ᵘ',
        'v': 'ᵛ', 'w': 'ʷ', 'x': 'ˣ', 'y': 'ʸ', 'z': 'ᶻ'
    }
    
    SUB = {
        '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
        '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉',
        '+': '₊', '-': '₋', '=': '₌', '(': '₍', ')': '₎',
        'a': 'ₐ', 'e': 'ₑ', 'h': 'ₕ', 'i': 'ᵢ', 'j': 'ⱼ',
        'k': 'ₖ', 'l': 'ₗ', 'm': 'ₘ', 'n': 'ₙ', 'o': 'ₒ',
        'p': 'ₚ', 'r': 'ᵣ', 's': 'ₛ', 't': 'ₜ', 'u': 'ᵤ',
        'v': 'ᵥ', 'x': 'ₓ'
    }
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # FRACTIONS - Common mathematical fractions
    # ═══════════════════════════════════════════════════════════════════════════════
    
    FRACTIONS = {
        '1/2': '½',     '1/3': '⅓',     '2/3': '⅔',
        '1/4': '¼',     '3/4': '¾',     '1/5': '⅕',
        '2/5': '⅖',     '3/5': '⅗',     '4/5': '⅘',
        '1/6': '⅙',     '5/6': '⅚',     '1/7': '⅐',
        '1/8': '⅛',     '3/8': '⅜',     '5/8': '⅝',
        '7/8': '⅞',     '1/9': '⅑',     '1/10': '⅒'
    }
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # HELPER METHODS
    # ═══════════════════════════════════════════════════════════════════════════════
    
    @classmethod
    def get_all_categories(cls):
        """Return all available character categories."""
        return {
            'SINGLE': cls.SINGLE,
            'DOUBLE': cls.DOUBLE,
            'HEAVY': cls.HEAVY,
            'MIXED': cls.MIXED,
            'ROUNDED': cls.ROUNDED,
            'DASHES': cls.DASHES,
            'ARROWS': cls.ARROWS,
            'BULLETS': cls.BULLETS,
            'MATH': cls.MATH,
            'SEPARATORS': cls.SEPARATORS,
            'BRACKETS': cls.BRACKETS,
            'STATUS': cls.STATUS,
            'SHAPES': cls.SHAPES,
            'TECHNICAL': cls.TECHNICAL,
            'SUPER': cls.SUPER,
            'SUB': cls.SUB,
            'FRACTIONS': cls.FRACTIONS
        }
    
    @classmethod
    def create_border(cls, text, style='double', width=None):
        """
        Create a bordered text block using specified box drawing style.
        
        Args:
            text (str): Text to border
            style (str): Border style ('single', 'double', 'heavy', 'rounded')
            width (int): Fixed width (auto-calculated if None)
        
        Returns:
            str: Bordered text block
        """
        lines = text.split('\n')
        if width is None:
            width = max(len(line) for line in lines) + 4
        
        chars = getattr(cls, style.upper(), cls.DOUBLE)
        
        # Top border
        result = chars['top_left'] + chars['horizontal'] * (width - 2) + chars['top_right'] + '\n'
        
        # Content lines
        for line in lines:
            padding = width - len(line) - 4
            result += chars['vertical'] + ' ' + line + ' ' * padding + ' ' + chars['vertical'] + '\n'
        
        # Bottom border
        result += chars['bottom_left'] + chars['horizontal'] * (width - 2) + chars['bottom_right']
        
        return result
    
    @classmethod
    def create_separator(cls, char=None, length=80, style='double'):
        """
        Create a horizontal separator line.
        
        Args:
            char (str): Character to use (auto-selected if None)
            length (int): Length of separator
            style (str): Style category for auto-selection
        
        Returns:
            str: Separator line
        """
        if char is None:
            char = getattr(cls, style.upper(), cls.DOUBLE)['horizontal']
        return char * length
    
    @classmethod
    def format_with_arrows(cls, text, arrow_style='double_right'):
        """
        Format text with leading arrow indicators.
        
        Args:
            text (str): Text to format
            arrow_style (str): Arrow style from ARROWS category
        
        Returns:
            str: Formatted text with arrows
        """
        arrow = cls.ARROWS.get(arrow_style, cls.ARROWS['double_right'])
        return f"{arrow} {text}"
    
    @classmethod
    def status_indicator(cls, status, text):
        """
        Add status indicator to text.
        
        Args:
            status (str): Status type ('success', 'error', 'warning', 'info')
            text (str): Text to mark
        
        Returns:
            str: Text with status indicator
        """
        indicators = {
            'success': cls.STATUS['heavy_check'],
            'error': cls.STATUS['heavy_cross'],
            'warning': cls.STATUS['warning'],
            'info': cls.STATUS['info']
        }
        indicator = indicators.get(status, cls.STATUS['info'])
        return f"{indicator} {text}"


# ═══════════════════════════════════════════════════════════════════════════════
# USAGE EXAMPLES AND DEMONSTRATIONS
# ═══════════════════════════════════════════════════════════════════════════════

def demonstrate_characters():
    """Demonstrate the various character categories with visual examples."""
    
    print(DebugChars.create_border("DEBUG CHARACTER REFERENCE DEMONSTRATION", 'double', 60))
    print()
    
    # Box drawing demonstration
    print(DebugChars.create_separator(style='double'))
    print("BOX DRAWING STYLES")
    print(DebugChars.create_separator(style='double'))
    
    styles = ['single', 'double', 'heavy', 'rounded']
    for style in styles:
        demo_text = f"This is {style.upper()} style border"
        print(DebugChars.create_border(demo_text, style, 40))
        print()
    
    # Arrow demonstrations
    print(DebugChars.create_separator(style='heavy'))
    print("ARROW INDICATORS")
    print(DebugChars.create_separator(style='heavy'))
    
    arrow_examples = [
        ('right', 'Process flow'),
        ('double_right', 'Important flow'),
        ('heavy_right', 'Critical path'),
        ('curved_right', 'Return to step'),
        ('loop_right', 'Iteration cycle')
    ]
    
    for arrow, desc in arrow_examples:
        print(DebugChars.format_with_arrows(desc, arrow))
    print()
    
    # Status indicators
    print(DebugChars.create_separator(style='single'))
    print("STATUS INDICATORS")
    print(DebugChars.create_separator(style='single'))
    
    status_examples = [
        ('success', 'Data loaded successfully'),
        ('error', 'Failed to process sensor data'),
        ('warning', 'Sensor calibration needed'),
        ('info', 'Processing 1,000,000 data points')
    ]
    
    for status, message in status_examples:
        print(DebugChars.status_indicator(status, message))
    print()
    
    # Mathematical symbols
    print(DebugChars.create_separator(DebugChars.MATH['sum'], 50))
    print("MATHEMATICAL EXPRESSIONS")
    print(DebugChars.create_separator(DebugChars.MATH['sum'], 50))
    
    math_examples = [
        f"σ{DebugChars.SUB['x']} = √(Σ(x{DebugChars.SUB['i']} - μ){DebugChars.SUPER['2']} / n)",
        f"F = ma {DebugChars.ARROWS['right']} Force equation",
        f"∇ × B = μ{DebugChars.SUB['0']}J + μ{DebugChars.SUB['0']}ε{DebugChars.SUB['0']}∂E/∂t",
        f"E = mc{DebugChars.SUPER['2']} {DebugChars.SEPARATORS['section']} Einstein's equation"
    ]
    
    for expr in math_examples:
        print(f"  {expr}")
    print()
    
    # Hierarchical structure example
    print(DebugChars.create_separator(DebugChars.SEPARATORS['vertical_ellipsis'], 50))
    print("HIERARCHICAL DATA STRUCTURE")
    print(DebugChars.create_separator(DebugChars.SEPARATORS['vertical_ellipsis'], 50))
    
    hierarchy = f"""
{DebugChars.SINGLE['top_left']}{DebugChars.SINGLE['horizontal']} TransFusion Root
{DebugChars.SINGLE['vertical']} {DebugChars.SINGLE['tee_right']}{DebugChars.SINGLE['horizontal']} Sensor Data
{DebugChars.SINGLE['vertical']} {DebugChars.SINGLE['vertical']} {DebugChars.SINGLE['tee_right']}{DebugChars.SINGLE['horizontal']} GPS Data {DebugChars.STATUS['heavy_check']}
{DebugChars.SINGLE['vertical']} {DebugChars.SINGLE['vertical']} {DebugChars.SINGLE['tee_right']}{DebugChars.SINGLE['horizontal']} MRU Data {DebugChars.STATUS['heavy_check']}
{DebugChars.SINGLE['vertical']} {DebugChars.SINGLE['vertical']} {DebugChars.SINGLE['bottom_left']}{DebugChars.SINGLE['horizontal']} Inclinometer {DebugChars.STATUS['warning']}
{DebugChars.SINGLE['vertical']} {DebugChars.SINGLE['tee_right']}{DebugChars.SINGLE['horizontal']} Model Training
{DebugChars.SINGLE['vertical']} {DebugChars.SINGLE['vertical']} {DebugChars.SINGLE['tee_right']}{DebugChars.SINGLE['horizontal']} Epoch 1/10 {DebugChars.STATUS['info']}
{DebugChars.SINGLE['vertical']} {DebugChars.SINGLE['vertical']} {DebugChars.SINGLE['bottom_left']}{DebugChars.SINGLE['horizontal']} Loss: 0.0045 {DebugChars.ARROWS['down']}
{DebugChars.SINGLE['bottom_left']}{DebugChars.SINGLE['horizontal']} Results {DebugChars.STATUS['heavy_check']}
"""
    print(hierarchy)


# ═══════════════════════════════════════════════════════════════════════════════
# PRESET COMBINATIONS FOR COMMON USE CASES
# ═══════════════════════════════════════════════════════════════════════════════

class DebugPresets:
    """Pre-configured character combinations for common debug scenarios."""
    
    @staticmethod
    def progress_bar(progress, total, width=40, style='heavy'):
        """
        Create a Unicode progress bar.
        
        Args:
            progress (int): Current progress
            total (int): Total items
            width (int): Width of progress bar
            style (str): Style ('heavy', 'double', 'single')
        
        Returns:
            str: Formatted progress bar
        """
        chars = getattr(DebugChars, style.upper(), DebugChars.HEAVY)
        filled_width = int((progress / total) * width)
        empty_width = width - filled_width
        
        bar = chars['horizontal'] * filled_width + DebugChars.BULLETS['white_circle'] * empty_width
        percentage = (progress / total) * 100
        
        return f"{chars['vertical']}{bar}{chars['vertical']} {percentage:.1f}% ({progress}/{total})"
    
    @staticmethod
    def section_header(title, level=1):
        """
        Create hierarchical section headers.
        
        Args:
            title (str): Section title
            level (int): Header level (1-4)
        
        Returns:
            str: Formatted section header
        """
        styles = [
            (DebugChars.DOUBLE['horizontal'], DebugChars.DOUBLE['horizontal']),  # Level 1
            (DebugChars.SINGLE['horizontal'], DebugChars.SINGLE['horizontal']),  # Level 2
            (DebugChars.DASHES['en_dash'], ''),                                   # Level 3
            (DebugChars.BULLETS['bullet'], '')                                    # Level 4
        ]
        
        if level > len(styles):
            level = len(styles)
        
        prefix, suffix = styles[level - 1]
        
        if suffix:
            separator = prefix * 80
            return f"\n{separator}\n{title.upper()}\n{separator}\n"
        else:
            return f"\n{prefix} {title}\n"
    
    @staticmethod
    def data_table_row(values, widths, style='single'):
        """
        Create a formatted table row.
        
        Args:
            values (list): Row values
            widths (list): Column widths
            style (str): Border style
        
        Returns:
            str: Formatted table row
        """
        chars = getattr(DebugChars, style.upper(), DebugChars.SINGLE)
        row = chars['vertical']
        
        for value, width in zip(values, widths):
            padded_value = str(value).ljust(width)
            row += f" {padded_value} {chars['vertical']}"
        
        return row
    
    @staticmethod
    def matrix_display(matrix, precision=3):
        """
        Display a matrix with mathematical brackets.
        
        Args:
            matrix (list): 2D matrix
            precision (int): Decimal precision
        
        Returns:
            str: Formatted matrix
        """
        if not matrix:
            return "[]"
        
        # Format numbers
        formatted_matrix = []
        max_width = 0
        
        for row in matrix:
            formatted_row = []
            for val in row:
                if isinstance(val, (int, float)):
                    formatted_val = f"{val:.{precision}f}"
                else:
                    formatted_val = str(val)
                formatted_row.append(formatted_val)
                max_width = max(max_width, len(formatted_val))
            formatted_matrix.append(formatted_row)
        
        # Build matrix string
        result = []
        for i, row in enumerate(formatted_matrix):
            if i == 0:
                left_bracket = DebugChars.BRACKETS['square_left']
            elif i == len(formatted_matrix) - 1:
                left_bracket = DebugChars.BRACKETS['square_left']
            else:
                left_bracket = DebugChars.BRACKETS['square_left']
            
            if i == 0:
                right_bracket = DebugChars.BRACKETS['square_right']
            elif i == len(formatted_matrix) - 1:
                right_bracket = DebugChars.BRACKETS['square_right']
            else:
                right_bracket = DebugChars.BRACKETS['square_right']
            
            formatted_values = [val.rjust(max_width) for val in row]
            row_str = f"{left_bracket} {' '.join(formatted_values)} {right_bracket}"
            result.append(row_str)
        
        return '\n'.join(result)


# if __name__ == "__main__":
#     # Run demonstration when script is executed directly
#     demonstrate_characters()
    
#     print("\n" + DebugChars.create_separator(DebugChars.SHAPES['star_filled'], 60))
#     print("PRESET EXAMPLES")
#     print(DebugChars.create_separator(DebugChars.SHAPES['star_filled'], 60))
    
#     # Progress bar example
#     print(DebugPresets.progress_bar(75, 100, 30, 'heavy'))
#     print(DebugPresets.progress_bar(45, 100, 30, 'double'))
#     print()
    
#     # Section headers
#     print(DebugPresets.section_header("Main Analysis", 1))
#     print(DebugPresets.section_header("Data Processing", 2))
#     print(DebugPresets.section_header("Sensor Validation", 3))
#     print(DebugPresets.section_header("Individual Check", 4))
    
#     # Matrix example
#     sample_matrix = [
#         [1.234, 5.678, 9.012],
#         [3.456, 7.890, 1.234],
#         [5.678, 9.012, 3.456]
#     ]
#     print("Transformation Matrix:")
#     print(DebugPresets.matrix_display(sample_matrix, 3))





# ===----==----====---=-===--=- Aesthetics -====----=-===---=
# =-==-=-               [   =-==-=--=-==-=--=-==-=--=-==-=--=-==-= ]
# ===-==-=--=-          [   =-==-=--=-==-=--=-==-=--=-==-=--=-==-= ]
# =--==---==--          [   =--==---==--=--==---==----=--==---==--=]
# =-==---==-=--         [     =-==---==-=--=-==---==-=--=-==---==-=]
# =-==------==-=----    [     =-==------==-=----=-==------==-=----=]
# =-==-                 [      =-==-=-==-=-==-=-==-=-==-=-==-=-==-=]
# ==---=-=--            [==---=-=--==---=-=--==---=-=--==---=-=--==]
# =--=-=--=             [      =--=-=--==--=-=--==--=-=--==--=-=--=]
# ---=--==--=---        [---=--==--=------=--==--=------=--==--=---]
# --=-==-=--            [       ----=-==-=-----=-==-=-----=-==-=---]
# ==--=-=--             [    ==--=-=--==--=-=--==--=-=--==--=-=--==]
# =--==-=--=--==        [ =--==-=--=--===--==-=--=--===--==-=--=--=]
# =-==--=--==-=         [   =-==--=--==-==-==--=--==-==-==--=--==-=]
# -==--=-==-=--=--      [           -==--=-==-=--=---==--=-==-=--=-]
# =-==----==-=--        [=-==----==-=--=-==----==-=--=-==----==-=--]
# =-==--=--==-=--       [=-==--=--==-=--=-==--=--==-=--=-==--=--==-]
# ====---=-===--=       [   ===----==----====---=-===--=--===----==]
# ==--=---====---=--    [      ==--=---====---=--==--=---====---=--]

# Samples:
# -=-==---=
# ---==---=
# ---==-=--=
# ====----=-===---= =---===-=----===
# ===-----=-==--=
# ===----==-=--=
# ===-=----=-==---=
# ==--=-=--=
# -==-=-----=-
# ===-=--==-=----=-
# ==-=--==-==--=-==
# --=---==-===----==-=--=
# =-====-----=-===---=
# ==--=---====---=--
# ==-=--===--=-==
# ====---=-===--=
# =--===--==--=
# =-==----==-=--
# =-==------==-=----
# =-==---===--=
# ----===--=---==----===---==-
# ===----=-==---===----=-===---=
# ===--=---==----===---==-------==
# ----===--=---==----===---==-------==
# ==---=--==-=-==-==-=-==-=-==-=---=
# ==--==-=-==---===--==-=-==---===--==-=-==---=

# Separators:
# ──────────────────────────────────────────────────────────────────
# ===----=-===-==----===-=-----==--===-----=--==-----=-===--=------=
# ====--=-----==-=-==----===---==---=-==---===-=----===----=-------=
# ===-==----=----==-===--=------===-==--=-----===--=------===-=---=-
# ===--=---==---===--==-------==----===--=---==----===---==-------==