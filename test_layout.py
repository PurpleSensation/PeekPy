#!/usr/bin/env python3
"""
Test script for text block assembler and multi-column tree layout.
This script develops and validates the layout functionality before integration.
"""

from typing import List, Dict, Tuple, Optional, Union
import textwrap

class TextBlockAssembler:
    """
    A generic text block layout handler that can arrange text blocks in a grid format.
    Supports relative positioning, automatic alignment, and flexible column widths.
    """
    
    def __init__(self, rows: int = 1, cols: int = 1, 
                 col_widths: Optional[List[int]] = None,
                 spacing: int = 2,
                 align: str = "left"):
        """
        Initialize the layout grid.
        
        Args:
            rows: Number of rows in the grid
            cols: Number of columns in the grid
            col_widths: List of column widths (auto-calculated if None)
            spacing: Space between columns
            align: Default alignment ("left", "right", "center")
        """
        self.rows = rows
        self.cols = cols
        self.spacing = spacing
        self.align = align
        self.col_widths = col_widths or [0] * cols
        
        # Grid to store text blocks - each cell contains list of lines
        self.grid: List[List[List[str]]] = [[[] for _ in range(cols)] for _ in range(rows)]
        
        # Track actual widths for auto-sizing
        self._actual_widths = [0] * cols
    
    def add_block(self, text: Union[str, List[str]], 
                  row: int = 0, col: int = 0,
                  width: Optional[int] = None,
                  align: Optional[str] = None) -> 'TextBlockAssembler':
        """
        Add a text block to the specified grid position.
        
        Args:
            text: Text content (string or list of lines)
            row: Target row position
            col: Target column position
            width: Override width for this block
            align: Override alignment for this block
        """
        if row >= self.rows or col >= self.cols:
            raise ValueError(f"Position ({row}, {col}) outside grid ({self.rows}, {self.cols})")
        
        # Convert text to list of lines
        if isinstance(text, str):
            lines = text.split('\n')
        else:
            lines = list(text)
        
        # Store the lines
        self.grid[row][col] = lines
        
        # Update width tracking
        max_line_width = max(len(line) for line in lines) if lines else 0
        if width:
            max_line_width = max(max_line_width, width)
        
        self._actual_widths[col] = max(self._actual_widths[col], max_line_width)
        
        return self
    
    def render(self) -> List[str]:
        """
        Render the complete layout as a list of output lines.
        """
        # Calculate final column widths
        final_widths = []
        for i, width in enumerate(self.col_widths):
            if width == 0:  # Auto-size
                final_widths.append(self._actual_widths[i])
            else:
                final_widths.append(max(width, self._actual_widths[i]))
        
        output_lines = []
        
        for row in range(self.rows):
            # Find the maximum number of lines in this row
            max_lines = max(len(self.grid[row][col]) for col in range(self.cols))
            
            # Process each line level in this row
            for line_idx in range(max_lines):
                line_parts = []
                
                for col in range(self.cols):
                    # Get the text for this position
                    cell_lines = self.grid[row][col]
                    if line_idx < len(cell_lines):
                        text = cell_lines[line_idx]
                    else:
                        text = ""  # Empty if this cell has fewer lines
                    
                    # Apply alignment and width
                    width = final_widths[col]
                    align = self.align  # Could be overridden per cell in future
                    
                    if align == "left":
                        formatted = text.ljust(width)
                    elif align == "right":
                        formatted = text.rjust(width)
                    else:  # center
                        formatted = text.center(width)
                    
                    line_parts.append(formatted)
                
                # Join with spacing
                output_lines.append((' ' * self.spacing).join(line_parts))
        
        return output_lines


def test_basic_layout():
    """Test basic layout functionality."""
    print("=== Basic Layout Test ===")
    
    assembler = TextBlockAssembler(rows=1, cols=3, spacing=2)
    
    assembler.add_block("Left\nColumn", row=0, col=0)
    assembler.add_block("Middle\nColumn\nWith More", row=0, col=1)
    assembler.add_block("Right", row=0, col=2)
    
    result = assembler.render()
    for line in result:
        print(f"'{line}'")
    print()


def test_tree_layout():
    """Test tree-like structure with multiple columns."""
    print("=== Tree Layout Test ===")
    
    # Sample data structure similar to TransFusion parameters
    data = {
        "Optimization": {
            "dropout": 0.1,
            "batch_size": 32,
            "lr": 0.001,
            "gradient_clip": 2,
            "scheduler_rate": 1
        },
        "Regularization": {
            "VAO": False,
            "lambda_dif": 0,
            "lambda_fft": 0.0,
            "lambda_der": 0.3,
            "lambda_off": 0.0,
            "norm_strategy": "percentile_95"
        },
        "Latent_Grid": {
            "dynamic_grid": False,
            "grid_size": 128,
            "latent_dim": 64
        }
    }
    
    def render_tree_branch(key: str, value: dict, is_first: bool = False, is_last: bool = False) -> List[str]:
        """Render a single tree branch as lines of text."""
        lines = []
        
        # Determine the branch connector for the header
        if is_first:
            header_branch = "╰┬◻"
        elif is_last:
            header_branch = "╰─◻"  
        else:
            header_branch = "├─◻"
        
        # Add the header line
        lines.append(f"      {header_branch} {key}")
        
        # Add the items with proper tree structure
        items = list(value.items())
        for i, (k, v) in enumerate(items):
            item_is_last = i == len(items) - 1
            
            if is_last and item_is_last:
                # Last item in last branch - no continuation
                item_branch = "         ╰─"
            elif is_last:
                # Not last item in last branch
                item_branch = "         ├─"
            elif item_is_last:
                # Last item in non-last branch
                item_branch = "      │  ╰─"
            else:
                # Regular item in non-last branch
                item_branch = "      │  ├─"
            
            lines.append(f"{item_branch} {k}: {v}")
        
        return lines
    
    # Test with 2 columns
    print("2-column layout:")
    assembler = TextBlockAssembler(rows=1, cols=3, spacing=2)
    
    # Add main connector
    connector_lines = ["   ╰┬──────────────────┬──────────────"]
    assembler.add_block(connector_lines, row=0, col=0)
    
    # Process first level items in pairs
    items = list(data.items())
    
    # First column: Optimization
    if len(items) > 0:
        branch1 = render_tree_branch(items[0][0], items[0][1], is_first=True, is_last=False)
        assembler.add_block(branch1, row=0, col=1)
    
    # Second column: Regularization  
    if len(items) > 1:
        branch2 = render_tree_branch(items[1][0], items[1][1], is_first=False, is_last=True)
        assembler.add_block(branch2, row=0, col=2)
    
    result = assembler.render()
    for line in result:
        print(line)
    
    print()
    print("3-column layout:")
    assembler3 = TextBlockAssembler(rows=1, cols=4, spacing=2)
    
    # Add connector for 3 columns
    connector3_lines = ["   ╰┬────────────┬────────────┬──────────"]
    assembler3.add_block(connector3_lines, row=0, col=0)
    
    # Add all three branches
    for i, (key, value) in enumerate(items[:3]):
        is_first = i == 0
        is_last = i == len(items[:3]) - 1
        branch = render_tree_branch(key, value, is_first=is_first, is_last=is_last)
        assembler3.add_block(branch, row=0, col=i+1)
    
    result = assembler3.render()
    for line in result:
        print(line)
    print()


if __name__ == "__main__":
    test_basic_layout()
    test_tree_layout()
