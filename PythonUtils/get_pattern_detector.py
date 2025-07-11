#!/usr/bin/env python3
"""
Regex Pattern Detector and Replacer for .get() method calls

This script provides regex patterns to detect .get() method calls and 
demonstrates how to automatically substitute them with dictionary access syntax.

Example:
    config.get("latent_period", 5.0) → config["latent_period"]
    self.config.get("noise_std", 0.2) → self.config["noise_std"]
"""

import re
import sys
from typing import List, Tuple

def detect_get_patterns(text: str) -> List[Tuple[str, str, str, str]]:
    """
    Detect .get() method patterns in the given text.
    
    Args:
        text: The input text to search
        
    Returns:
        List of tuples containing (full_match, object, key, default_value)
    """
    # Regex pattern to match .get() calls
    # Explanation:
    # (\w+(?:\.\w+)*) - captures object name (can include dots like self.config)
    # \.get\(          - matches .get(
    # (["\'])          - captures opening quote (single or double)
    # ([^"']+)         - captures the key inside quotes
    # \2               - matches the same quote type as opening
    # ,\s*             - matches comma and optional whitespace
    # ([^)]+)          - captures the default value
    # \)               - matches closing parenthesis
    
    pattern = r'(\w+(?:\.\w+)*)\.get\((["\'])([^"\']+)\2,\s*([^)]+)\)'
    
    matches = []
    for match in re.finditer(pattern, text):
        full_match = match.group(0)
        object_name = match.group(1)
        quote_type = match.group(2)
        key = match.group(3)
        default_value = match.group(4)
        
        matches.append((full_match, object_name, key, default_value))
    
    return matches

def replace_get_with_bracket_access(text: str, remove_defaults: bool = True) -> str:
    """
    Replace .get() calls with bracket access syntax.
    
    Args:
        text: The input text to process
        remove_defaults: If True, removes default values and uses bracket access.
                        If False, keeps the logic but shows the transformation.
    
    Returns:
        Modified text with replacements
    """
    pattern = r'(\w+(?:\.\w+)*)\.get\((["\'])([^"\']+)\2,\s*([^)]+)\)'
    
    def replacement(match):
        object_name = match.group(1)
        quote_type = match.group(2)
        key = match.group(3)
        default_value = match.group(4)
        
        if remove_defaults:
            # Simple bracket access (assumes key exists)
            return f'{object_name}[{quote_type}{key}{quote_type}]'
        else:
            # Keep the default logic but show the pattern
            return f'{object_name}["{key}"]  # was: .get("{key}", {default_value})'
    
    return re.sub(pattern, replacement, text)

def analyze_file(file_path: str):
    """
    Analyze a file for .get() patterns and show statistics.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        matches = detect_get_patterns(content)
        
        print(f"Analysis of {file_path}")
        print("=" * 50)
        print(f"Total .get() patterns found: {len(matches)}")
        print()
        
        if matches:
            print("Found patterns:")
            print("-" * 30)
            for i, (full_match, obj, key, default) in enumerate(matches, 1):
                print(f"{i:2d}. {full_match}")
                print(f"    Object: {obj}")
                print(f"    Key: '{key}'")
                print(f"    Default: {default}")
                print(f"    Would become: {obj}[\"{key}\"]")
                print()
        
        # Show unique objects and keys
        objects = set(match[1] for match in matches)
        keys = set(match[2] for match in matches)
        
        print(f"Unique objects using .get(): {len(objects)}")
        for obj in sorted(objects):
            print(f"  - {obj}")
        print()
        
        print(f"Unique keys accessed: {len(keys)}")
        for key in sorted(keys):
            print(f"  - '{key}'")
        
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"Error reading file: {e}")

def demo_patterns():
    """
    Demonstrate the regex pattern with example strings.
    """
    test_strings = [
        'config.get("latent_period", 5.0)',
        'self.config.get("noise_std", 0.2)',
        'train_config.get("max_latent_period", 30.0)',
        'df.attrs.get("label", f"sensor_{s_id}")',
        'meta_data.get("sensors", [])',
        'cfg.get("min_period", 0.1)',
        'self.config.get("diffusion_steps", 100)',
    ]
    
    print("REGEX PATTERN DEMONSTRATION")
    print("=" * 50)
    print("Pattern: r'(\\w+(?:\\.\\w+)*)\\.get\\(([\"\\'])([^\"\\']*)\\2,\\s*([^)]+)\\)'")
    print()
    print("Test strings and their detection:")
    print("-" * 40)
    
    for test_str in test_strings:
        matches = detect_get_patterns(test_str)
        if matches:
            print(f"✓ FOUND: {test_str}")
            for full_match, obj, key, default in matches:
                print(f"  → Object: '{obj}', Key: '{key}', Default: {default}")
                print(f"  → Replacement: {obj}[\"{key}\"]")
        else:
            print(f"✗ NOT FOUND: {test_str}")
        print()
    
    print("\nAUTOMATIC REPLACEMENT DEMO:")
    print("-" * 30)
    sample_code = '''
    def example_function(self, config):
        self.lr = config.get("lr", 1e-3)
        self.noise_std = self.config.get("noise_std", 0.2)
        period = train_config.get("latent_period", 5.0)
        return period
    '''
    
    print("Original code:")
    print(sample_code)
    
    print("After replacement (bracket access):")
    replaced = replace_get_with_bracket_access(sample_code, remove_defaults=True)
    print(replaced)
    
    print("After replacement (with comments):")
    replaced_commented = replace_get_with_bracket_access(sample_code, remove_defaults=False)
    print(replaced_commented)

def replace_file_get_patterns(file_path: str, backup: bool = True, mode: str = "bracket") -> bool:
    """
    Replace all .get() patterns in a file with bracket access.
    
    Args:
        file_path: Path to the file to modify
        backup: If True, creates a backup file with .backup extension
        mode: "bracket" for simple bracket access, "commented" for bracket with comments
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Read the original file
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Create backup if requested
        if backup:
            backup_path = file_path + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            print(f"Backup created: {backup_path}")
        
        # Detect patterns before replacement
        matches_before = detect_get_patterns(original_content)
        print(f"Found {len(matches_before)} .get() patterns to replace")
        
        # Perform replacement
        if mode == "commented":
            new_content = replace_get_with_bracket_access(original_content, remove_defaults=False)
        else:
            new_content = replace_get_with_bracket_access(original_content, remove_defaults=True)
        
        # Verify replacement worked
        matches_after = detect_get_patterns(new_content)
        
        # Write the modified content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✓ Successfully replaced {len(matches_before) - len(matches_after)} patterns")
        if matches_after:
            print(f"⚠ Warning: {len(matches_after)} patterns still remain (might be complex cases)")
        
        return True
        
    except Exception as e:
        print(f"Error processing file: {e}")
        return False

if __name__ == "__main__":
    print("GET() Pattern Detector and Replacer")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        
        # Check for replacement mode
        if len(sys.argv) > 2 and sys.argv[2] in ["--replace", "--replace-commented"]:
            mode = "commented" if sys.argv[2] == "--replace-commented" else "bracket"
            print(f"REPLACEMENT MODE: {mode}")
            print("=" * 40)
            
            # Show what will be replaced
            print("Preview of changes:")
            analyze_file(file_path)
            
            # Ask for confirmation (or proceed automatically)
            print("\n" + "="*50)
            print("🔄 PROCEEDING WITH REPLACEMENT...")
            
            success = replace_file_get_patterns(file_path, backup=True, mode=mode)
            
            if success:
                print("✅ File replacement completed successfully!")
                print("📁 Original file backed up with .backup extension")
            else:
                print("❌ File replacement failed!")
        else:
            # Analyze the provided file
            analyze_file(file_path)
    else:
        # Run demonstration
        demo_patterns()
        
        print("\n" + "="*50)
        print("USAGE:")
        print("  python get_pattern_detector.py [file_path] [--replace|--replace-commented]")
        print("  - Without file_path: Shows pattern demonstration")
        print("  - With file_path only: Analyzes the specified file")
        print("  - With --replace: Replaces .get() with bracket access")
        print("  - With --replace-commented: Replaces with comments showing original")
