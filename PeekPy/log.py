# -=--==-=--==-=--==-=--== Logging Utility -=--==-=--==-=--==-=--==
import time as tm, numpy as np
import re, os, shutil, pathlib
from typing import List, Dict, Optional, Union, Tuple
from math import floor
n_indent = 0


# ─────────────────────────────────────────────────────────────────────────────
# Debug Characters
# ─────────────────────────────────────────────────────────────────────────────
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
        }   
        # Top border
        
    
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

class ConsoleTable:
    def __init__(self,
                 headers: list,
                 log: "Log" = None,
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
        self.margin:        str     = "│"        # Margin for the table
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
        row = [self.formats[i].format(item).replace('e+0', 'e').replace('e-0', 'e-') for i, item in enumerate(row)]

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

class ProgressBar:
    """ A class to handle an inline progress bar using the Log instance.

    Attributes:
        log (Log): The Log instance used for output.
        total_length (int): Total number of bars representing 100% progress.
        current_bars (int): The number of bars currently printed.
        closed (bool): Whether the progress bar has been closed.
    """
    def __init__(self, log: "Log", total_length: int = 60, header: str = "progress"):
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

class TextBlockAssembler:
    """
    Generic text block assembler for creating complex multi-column layouts.
    
    This class provides a flexible framework for positioning text blocks in a grid-like
    layout, supporting various alignment modes and automatic content fitting.
    """
    
    def __init__(self, rows: int, cols: int, col_widths: List[int] = None, 
                 default_align: str = "left", cell_padding: int = 1):
        """
        Initialize the text block assembler.
        
        Args:
            rows: Number of rows in the grid
            cols: Number of columns in the grid  
            col_widths: List of column widths (auto-calculated if None)
            default_align: Default text alignment ("left", "right", "center")
            cell_padding: Padding between columns
        """
        self.rows = rows
        self.cols = cols
        self.col_widths = col_widths or [20] * cols  # Default 20 chars per column
        self.default_align = default_align
        self.cell_padding = cell_padding
        
        # Internal grid storage: grid[row][col] = list of lines
        self.grid = [[[] for _ in range(cols)] for _ in range(rows)]
        self.max_lines_per_row = [0] * rows
        
    def add_block(self, row: int, col: int, content: Union[str, List[str]], 
                  align: str = None):
        """
        Add a text block to the specified grid position.
        
        Args:
            row: Target row (0-based)
            col: Target column (0-based)
            content: String or list of strings to place in the cell
            align: Text alignment for this cell (overrides default)
        """
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            raise ValueError(f"Position ({row}, {col}) out of bounds")
            
        # Convert content to list of lines
        if isinstance(content, str):
            lines = content.split('\n')
        else:
            lines = content
            
        # Apply alignment
        alignment = align or self.default_align
        col_width = self.col_widths[col]
        
        aligned_lines = []
        for line in lines:
            if alignment == "left":
                aligned_lines.append(line.ljust(col_width))
            elif alignment == "right":
                aligned_lines.append(line.rjust(col_width))
            elif alignment == "center":
                aligned_lines.append(line.center(col_width))
            else:
                aligned_lines.append(line.ljust(col_width))  # Default to left
                
        # Add to grid
        self.grid[row][col] = aligned_lines
        
        # Update max lines for this row
        self.max_lines_per_row[row] = max(self.max_lines_per_row[row], len(aligned_lines))
        
    def render(self) -> List[str]:
        """
        Render the complete grid as a list of formatted lines.
        
        Returns:
            List of strings representing the formatted output
        """
        output_lines = []
        
        for row in range(self.rows):
            max_lines = self.max_lines_per_row[row]
            
            # For each line within this row
            for line_idx in range(max_lines):
                line_parts = []
                
                for col in range(self.cols):
                    cell_content = self.grid[row][col]
                    
                    # Get the content for this line (or empty if cell has fewer lines)
                    if line_idx < len(cell_content):
                        content = cell_content[line_idx]
                    else:
                        content = " " * self.col_widths[col]
                    
                    line_parts.append(content)
                
                # Join with padding
                padding = " " * self.cell_padding
                output_lines.append(padding.join(line_parts))
                
        return output_lines

class TreeRenderer:
    """
    Dedicated class for handling complex tree rendering with multi-column support.
    Provides modular, maintainable tree layout functionality.
    """
    
    def __init__(self, log_instance):
        """Initialize with reference to Log instance for output."""
        self.log = log_instance
        self.terminal_width = 75
        self.min_col_width = 10
        
    def render_tree(self, data: Dict, header: str, cols: int = 1, show_types: bool = False, max_depth: int = None):
        """
        Main entry point for tree rendering.
        
        Args:
            data: Dictionary or nested structure to display
            header: Header for the tree
            cols: Number of columns for first-level categories
            show_types: Show type information for values
            max_depth: Maximum depth to traverse
        """
        if self.log.muted or self.log.DEBUG < self.log.level:
            return
            # Calculate base indentation
        base_indent = "│ "
        # Show header with matching indentation
        self.log(f"{base_indent}⚙ {header}")

        # Handle empty data
        if not data:
            self.log.log(f"{base_indent}╰─ (empty)")
            return
            
        # Choose rendering strategy
        if cols > 1 and isinstance(data, dict):
            self._render_multi_column(data, base_indent, cols, max_depth, show_types)
        else:   self._single_column(data, base_indent, max_depth, show_types)
    
    def _render_multi_column(self, data: Dict, base_indent: str, cols: int, 
                           max_depth: int, show_types: bool):
        """Handle multi-column layout with smart width allocation and no truncation."""
        items = list(data.items())
        
        if not items:
            return
            
        # PHASE 1: Generate all content and calculate individual item widths
        item_contents = []
        item_widths = []
        
        for key, value in items:
            lines = self._generate_lines(key, value, max_depth, show_types, 0)
            item_contents.append(lines)
            # Calculate the actual width needed for this item (no truncation)
            max_width = max(len(line) for line in lines) if lines else 0
            item_widths.append(max_width)
        
        # PHASE 2: Smart grouping - distribute items optimally into rows
        available_width = self.terminal_width - 6  # Account for base indent and borders
        optimal_groups = self._compute_grouping(item_widths, cols, available_width)
        
        # PHASE 3: Render each group as a row
        self._row_separator(base_indent, optimal_groups[0] if optimal_groups else [])
        
        for group_idx, group_widths in enumerate(optimal_groups):
            # Get the items for this group
            start_idx = sum(len(g) for g in optimal_groups[:group_idx])
            group_items = item_contents[start_idx:start_idx + len(group_widths)]
            
            # Render row separator (except for first row)
            if group_idx > 0:
                self._row_separator(base_indent, group_widths)
            
            # Pad all items in group to same height
            max_height = max(len(item) for item in group_items) if group_items else 0
            for item in group_items:
                while len(item) < max_height:
                    item.append("")
            
            # Render the group content
            self._render_row(base_indent, group_items, group_widths)
        
        # Render bottom border
        self._bottom_border(base_indent, optimal_groups[-1] if optimal_groups else [])

    def _compute_grouping(self, item_widths: List[int], max_cols: int, available_width: int) -> List[List[int]]:
        """
        Optimally group items into rows to maximize space usage without exceeding available width.
        Returns list of groups, where each group is a list of column widths.
        """
        groups = []
        current_group = []
        current_width = 0
        padding_per_col = 1  # Space between columns
        
        for item_width in item_widths:
            # Calculate width if we add this item to current group
            needed_width = item_width
            if current_group:  # Add padding if not the first item in group
                needed_width += padding_per_col
            
            total_width = current_width + needed_width
            
            # Check if we can fit this item in current group
            can_fit = (total_width <= available_width and len(current_group) < max_cols)
            
            if can_fit and current_group:  # Add to current group
                current_group.append(item_width)
                current_width = total_width
            else:  # Start new group
                if current_group:  # Save current group if it exists
                    groups.append(current_group)
                current_group = [item_width]
                current_width = item_width
        
        # Add the last group
        if current_group:
            groups.append(current_group)
        
        return groups

    def _render_row(self, base_indent: str, group_items: List[List[str]], 
                                        group_widths: List[int]):
        """Render row content without column separators."""
        max_height = max(len(item) for item in group_items) if group_items else 0
        
        for line_idx in range(max_height):
            line_parts = [base_indent + "  │"]
            
            for col_idx, item_lines in enumerate(group_items):
                if col_idx < len(group_widths):
                    col_width = group_widths[col_idx]
                    
                    # Get the content for this line
                    if line_idx < len(item_lines) and item_lines[line_idx].strip():
                        content = item_lines[line_idx].ljust(col_width)
                    else:
                        content = " " * col_width
                    
                    line_parts.append(content)
                    
                    # Add spacing between columns (except for last column)
                    if col_idx < len(group_items) - 1:
                        line_parts.append("    ")  # 4 spaces instead of separator
            
            # Add closing border and render
            line_parts.append(" ")
            self.log.log("".join(line_parts))
    
    def _distribute_to_rows(self, items: List, cols: int) -> List[List]:
        """Distribute items into rows using round-robin for balanced columns."""
        # Calculate how many complete rows we'll have
        items_per_row = cols
        rows = []
        
        for i in range(0, len(items), items_per_row):
            row_items = items[i:i + items_per_row]
            rows.append(row_items)
        
        return rows
    
    def _generate_lines(self, key: str, value, max_depth: int, 
                           show_types: bool, col_idx: int) -> List[str]:
        """Generate tree lines for a single item."""
        lines = []
             
        if isinstance(value, dict) and value:
            type_info = f" ({type(value).__name__})" if show_types else ""
            lines.append(f" ╰ {key}{type_info}:")            
            # Process nested items
            sub_items = list(value.items())
            for i, (sub_key, sub_value) in enumerate(sub_items):
                is_last = i == len(sub_items) - 1
                
                if isinstance(sub_value, (dict, list, tuple)) and sub_value:
                    # Nested structure
                    connector = ""
                    branch = "╰┬ " if is_last else "├┬ "
                    lines.append(f"{connector}{branch}{sub_key}")
                    
                    # Handle list content
                    if isinstance(sub_value, list):
                        display_items = sub_value[:3]
                        for j, item in enumerate(display_items):
                            is_item_last = j == len(display_items) - 1 and len(sub_value) <= 3
                            item_branch = "╰─ " if is_item_last else "├─ "
                            next_connector = "       " if is_last else " │     "
                            lines.append(f"{connector}{next_connector}{item_branch}{item}")
                        
                        if len(sub_value) > 3:
                            next_connector = "       " if is_last else " │     "
                            lines.append(f"{connector}{next_connector}╰─ ... and {len(sub_value) - 3} more")
                else:
                    # Leaf node
                    connector = "   "
                    branch = "╰─ " if is_last else "├─ "
                    type_info_leaf = f" ({type(sub_value).__name__})" if show_types else ""
                    lines.append(f"{connector}{branch}{sub_key} = {sub_value}{type_info_leaf}")
        
        elif isinstance(value, (list, tuple)) and value:
            count_info = f"[{len(value)} items]"
            type_info = f" ({type(value).__name__})" if show_types else ""
            lines.append(f"  ╰─ {key}{type_info} {count_info}")
            
            # Process list items (limit to 3)
            display_items = value[:3]
            for j, item in enumerate(display_items):
                item_is_last = j == len(display_items) - 1 and len(value) <= 3
                item_branch = "╰─ " if item_is_last else "├─ "
                connector = "      "
                item_type = f" ({type(item).__name__})" if show_types else ""
                lines.append(f"{connector}{item_branch}{item}{item_type}")
            
            if len(value) > 3:
                lines.append(f"      ╰─ ... and {len(value) - 3} more")
        
        # Handle leaf node
        else:
            type_info = f" ({type(value).__name__})" if show_types else ""
            lines.append(f"  ╰─ {key}: {value}{type_info}")
        
        return lines
    
    def _compute_widths(self, max_widths: List[int], cols: int) -> List[int]:
        """Calculate optimal column widths based on content and terminal size."""
        if not max_widths:
            return []
            
        # Account for borders and separators: base_indent(2) + "  │"(3) + separators + "│"(1)
        border_overhead = 6  # Total border characters
        separator_overhead = (len(max_widths) - 1) if len(max_widths) > 1 else 0  # │ between columns
        available_width = self.terminal_width - border_overhead - separator_overhead
        
        # Add minimal padding to each column
        padded_widths = [w + 2 for w in max_widths]  # Just 2 chars padding per column
        total_content_width = sum(padded_widths)
        
        if total_content_width <= available_width:
            # Use content-based widths with padding
            return [max(self.min_col_width, w) for w in padded_widths]
        else:
            # Scale proportionally to fit terminal
            scale_factor = available_width / total_content_width
            return [max(self.min_col_width, int(w * scale_factor)) for w in padded_widths]
    
    def _row_separator(self, base_indent: str, col_widths: List[int]):
        """Render separator line between rows without column separators."""
        if not col_widths:
            return
            
        sep_parts = [base_indent + "  ├─"]
        # connector = DebugChars.SINGLE['tee_down']
        connector = "○"
        sep_parts.append(connector + "─"*10)
        sep_parts.extend([" " * (col_widths[i - 1] + 3 - 12) + "─"*2 + connector + "─" * 10 for i in range(1, len(col_widths))])
        
        self.log("".join(sep_parts))
    
    def _single_column(self, data, base_indent: str, max_depth: int, show_types: bool):
        """Render traditional single-column tree (delegates to existing method)."""
        # This would use the existing _tree_recursive logic
        self.log._tree_recursive(data, base_indent, " ", "", False, 0, max_depth, show_types)
    
    def _bottom_border(self, base_indent: str, col_widths: List[int]):
        """Render bottom border for multi-column layout without column separators."""
        if not col_widths:  return
            
        # border_parts = [base_indent + "  ╰"]
        # total_content_width = sum(col_widths) + (len(col_widths) - 1) * 4  # 4 spaces between columns
        # border_parts.append("─" * total_content_width)
        # border_parts.append("╯")        
        # self.log.log("".join(border_parts))
    
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
        if self._skip_next != False:
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
                decorated_header = f"{self.prefix[:-2]}{self.prefix[:-1]}◻ {rnd_start} {header} {rnd_end}"
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
        if self._skip_next != False:
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
        
        current_prefix = str(self.prefix)  # Save current prefix for output alignment
        # Decrement the indentation level (handles bounds checking)
        self._set_level(self.level - 1)
        new_level = int(self.level)  # This is the level we're returning to
        
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
        self._header_level[self.level] = "..."
        
        # Bounds checking with user warnings
        if new_level >= self.n_buffer:
            self.warning(f"Log level {new_level} exceeds buffer size {self.n_buffer}. Clamping to {self.n_buffer - 1}.")
        elif new_level < 0:
            self.warning(f"Log level {new_level} is below 0. Clamping to 0.")
            new_level = 0

            
        # Apply bounds: clamp between 0 and n_buffer-1
        self.level = min(new_level, self.n_buffer - 1)
        
        # Update visual prefix: base "\n  " + vertical bars for each indentation level
        # Example: level 0 = "\n  ", level 1 = "\n   │", level 2 = "\n   │ │", etc.
        self.prefix = "\n" + " │" * self.level if self.level else "\n  "
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
    
    
    def itemize(self, items: Union[List, Dict], header: str = "items", n_wrap: int = 50):
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
    
    def list(self, items: Union[List, Dict], 
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
        show_types: bool = False, max_depth: int = None, cols: int = 3):
        """
        Display nested dictionary/object as an indented tree structure.
        
        Args:
        data: Dictionary or nested structure to display
        header: Header for the tree
        show_types: Show type information for values
        max_depth: Maximum depth to traverse
        cols: Number of columns for first-level categories (default: 1)
        """
        # Use the modular TreeRenderer for cleaner, more maintainable code
        renderer = TreeRenderer(self)
        renderer.render_tree(data, header, cols, show_types, max_depth)
        
        # Add closing blank line
        self.blank()
        return self
    def _tree_recursive(self, data, level_indent,
                        parent_indent, connector,
                        is_last_branch, depth,
                        max_depth, show_types):
        """Helper method for tree() to handle nested recursion with proper indentation."""
        # Stop if we've reached max depth
        if max_depth is not None and depth > max_depth:     return        
        # No data or empty container
        if not data:    return       
        
        # Calculate this level's indentation
        this_base_indent = parent_indent + connector
        # Process each item
        items = list(data.items() if isinstance(data, dict) else enumerate(data))
        last_idx = len(items) - 1
        
        for i, (key, value) in enumerate(items):
            # Determine if this is the last item at this level
            is_last = i == last_idx
            is_first = i == 0

            
            this_indent = this_base_indent if is_first else this_base_indent
            
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
    def _tree_multi_column(self, data, cols, max_depth, show_types):
        """
        Handle multi-column layout for first-level categories using TextBlockAssembler.
        """
        items = list(data.items())
        
        # Calculate column distribution
        items_per_col = len(items) // cols
        if len(items) % cols > 0:
            items_per_col += 1
        
        # Calculate column distribution - use round-robin for better balance
        columns = [[] for _ in range(cols)]
        for i, item in enumerate(items):
            col_idx = i % cols  # Round-robin distribution
            columns[col_idx].append(item)
        
        # PRE-ANALYSIS PHASE: Generate all column content first to calculate proper dimensions
        column_content = []
        max_column_lines = 0
        max_column_widths = []
        
        for col_idx, col_items in enumerate(columns):
            lines = []
            max_line_width = 0
            
            for i, (key, value) in enumerate(col_items):
                is_first_in_col = i == 0
                
                # Generate the tree lines for this item
                item_lines = self._generate_tree_lines(key, value, max_depth, show_types, 
                                                     is_first_in_col, col_idx)
                lines.extend(item_lines)
                
                # Track maximum line width for this column
                for line in item_lines:
                    max_line_width = max(max_line_width, len(line))
                
                # Add spacing between items (except for last item)
                if i < len(col_items) - 1:
                    lines.append("")
            
            column_content.append(lines)
            max_column_lines = max(max_column_lines, len(lines))
            max_column_widths.append(max_line_width + 4)  # Add padding
        
        # Calculate proper column widths based on content analysis
        terminal_width = 80  # Standard terminal width
        available_width = terminal_width - len(self.base_indent) - 2  # Account for margins
        
        # Distribute width proportionally, but ensure minimum column width
        total_content_width = sum(max_column_widths)
        min_col_width = 15  # Minimum readable column width
        
        if total_content_width <= available_width:
            # Use content-based widths with balanced padding
            col_widths = []
            for w in max_column_widths:
                if w > 0:
                    col_widths.append(max(min_col_width, w + 3))
                else:
                    col_widths.append(0)
        else:
            # Scale down proportionally if content is too wide
            scale_factor = available_width / total_content_width
            col_widths = []
            for w in max_column_widths:
                if w > 0:
                    col_widths.append(max(min_col_width, int(w * scale_factor)))
                else:
                    col_widths.append(0)
        
        line = self.setp_line(col_widths)
        
        
        
        
        # Pad all columns to same height
        for lines in column_content:
            while len(lines) < max_column_lines:
                lines.append("")
        
        # Output the columns line by line, properly aligned with calculated widths
        for line_idx in range(max_column_lines):
            line_parts = [self.base_indent + "   │"]  # Start with base indentation
            
            for col_idx, content in enumerate(column_content):
                if col_idx < len(col_widths) and col_widths[col_idx] > 0:
                    if line_idx < len(content) and content[line_idx].strip():
                        # Format the content to fit the calculated column width
                        formatted_content = content[line_idx].ljust(col_widths[col_idx])
                        line_parts.append(formatted_content)
                    else:
                        # Empty content for this line
                        line_parts.append(" " * col_widths[col_idx])
            
            # Join and output the line (remove extra empty line issue)
            complete_line = "".join(line_parts).rstrip()
            if complete_line.strip():  # Only output truly non-empty lines
                self(complete_line)
    def setp_line(self, col_widths: List[int]):        
        # Create column separators line with proper widths
        sep_parts = []
        for i in range(len(col_widths)):
            if col_widths[i] > 0:  # Only add separator if column has content
                if i == 0:
                    sep_parts.append("╰┬──┬" + "─" * (col_widths[i] - 4))
                elif i == len(col_widths) - 1:
                    sep_parts.append("┬" + "─" * 3)
                else:
                    sep_parts.append("┬" + "─" * col_widths[i])
        # Only show separator if we have multiple columns with content
        if len([w for w in col_widths if w > 0]) > 1:
            self(f"{self.base_indent}  {''.join(sep_parts)}")
    def _generate_tree_lines(self, key, value, max_depth, show_types, is_first_in_col, col_idx):
        """
        Generate tree lines for a single key-value pair in multi-column layout.
        """
        lines = []
        
        # Handle nested dictionary
        if isinstance(value, dict) and value:
            type_info = f" ({type(value).__name__})" if show_types else ""
            
            # First line with the category name
            lines.append(f"  ╰─◻ {key}{type_info}")
            
            # Process nested items
            sub_items = list(value.items())
            for i, (sub_key, sub_value) in enumerate(sub_items):
                is_last = i == len(sub_items) - 1
                
                if isinstance(sub_value, (dict, list, tuple)) and sub_value:
                    # Nested structure
                    if is_first_in_col and col_idx == 0:
                        connector = "      "
                        branch = "╰┬ " if is_last else "├┬ "
                    elif is_first_in_col:
                        connector = "    "
                        branch = "╰┬ " if is_last else "├┬ "
                    else:
                        connector = "    "
                        branch = "╰┬ " if is_last else "├┬ "
                    
                    lines.append(f"{connector}{branch}{sub_key}")
                    
                    # Handle list content specially
                    if isinstance(sub_value, list):
                        display_items = sub_value[:3]  # Show first 3 items
                        for j, item in enumerate(display_items):
                            is_item_last = j == len(display_items) - 1 and len(sub_value) <= 3
                            item_branch = "╰─ " if is_item_last else "├─ "
                            next_connector = "     " if is_last else " │   "
                            lines.append(f"{connector}{next_connector}{item_branch}{item}")
                        
                        if len(sub_value) > 3:
                            next_connector = "     " if is_last else " │   "
                            lines.append(f"{connector}{next_connector}╰─ ... and {len(sub_value) - 3} more")
                else:
                    # Leaf node
                    if is_first_in_col and col_idx == 0:
                        connector = "   │   "
                        branch = "╰─ " if is_last else "├─ "
                    elif is_first_in_col:
                        connector = "    "
                        branch = "╰─ " if is_last else "├─ "
                    else:
                        connector = "    "
                        branch = "╰─ " if is_last else "├─ "
                    
                    type_info_leaf = f" ({type(sub_value).__name__})" if show_types else ""
                    lines.append(f"{connector}{branch}{sub_key}: {sub_value}{type_info_leaf}")
        
        # Handle list/array
        elif isinstance(value, (list, tuple)) and value:
            count_info = f"[{len(value)} items]"
            type_info = f" ({type(value).__name__})" if show_types else ""
            
            if is_first_in_col and col_idx == 0:
                lines.append(f"  ╰┬ {key}{type_info} {count_info}")
            elif is_first_in_col:
                lines.append(f"╰┬ {key}{type_info} {count_info}")
            else:
                lines.append(f"├─ {key}{type_info} {count_info}")
            
            # Process list items (limit to avoid too much content)
            display_items = value[:3]  # Limit to first 3 items
            for j, item in enumerate(display_items):
                item_is_last = j == len(display_items) - 1 and len(value) <= 3
                item_branch = "╰─ " if item_is_last else "├─ "
                if is_first_in_col and col_idx == 0:
                    connector = "   │   "
                elif is_first_in_col:
                    connector = "    "
                else:
                    connector = "    "
                item_type = f" ({type(item).__name__})" if show_types else ""
                lines.append(f"{connector}{item_branch}{item}{item_type}")
            
            if len(value) > 3:
                if is_first_in_col and col_idx == 0:
                    connector = "   │   "
                elif is_first_in_col:
                    connector = "    "
                else:
                    connector = "    "
                lines.append(f"{connector}╰─ ... and {len(value) - 3} more")
        
        # Handle leaf node
        else:
            type_info = f" ({type(value).__name__})" if show_types else ""
            lines.append(f"  ╰─ {key}: {value}{type_info}")
        
        return lines
    
    def consoleTable(self, headers: list, formats: list, title = "Table") -> ConsoleTable:
        """
        Create a ConsoleTable instance with the specified headers and formats.
        
        :param headers: List of column headers
        :param formats: Optional list of string formats (e.g., ':.2f', ':.0%', etc.)
        :return: ConsoleTable instance
        """
        return ConsoleTable(headers, log=self, formats=formats, header = title)
    def progressBar(self, header: str = "Progress") -> ProgressBar:
        """ Create a ProgressBar instance for tracking progress."""
        return ProgressBar(header = header, log=self)

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
def toggle(script_dir: Union[str, os.PathLike],
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