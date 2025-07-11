#!/usr/bin/env python3
"""
Apply .get() pattern replacements to all Python files in transFusion folder
"""

import sys
import os
# sys.path.append('.')
this_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(this_dir)
sys.path.append(os.path.dirname(this_dir))
from PythonUtils.get_pattern_detector import replace_file_get_patterns

# Define the transFusion folder path
transfusion_folder = r'transFusion'

# List of Python files to process
python_files = [
    '__init__.py',
    'fusionLayer.py',
    'msdfConfig.py', 
    'msdfNN.py',
    'msdfNoise.py',
    'msdfPlot.py',
    'msdfSensors.py',
    'msdfTraining.py'
]

def main():
    print("Applying .get() pattern replacements to transFusion Python files")
    print("=" * 60)
    
    success_count = 0
    failure_count = 0
    
    for py_file in python_files:
        file_path = os.path.join(transfusion_folder, py_file)
        
        print(f"\n🔄 Processing: {py_file}")
        print("-" * 30)
        
        if os.path.exists(file_path):
            try:
                success = replace_file_get_patterns(file_path, backup=True, mode="bracket")
                if success:
                    success_count += 1
                    print(f"✅ {py_file} - SUCCESS")
                else:
                    failure_count += 1
                    print(f"❌ {py_file} - FAILED")
            except Exception as e:
                failure_count += 1
                print(f"❌ {py_file} - ERROR: {e}")
        else:
            print(f"⚠️  {py_file} - FILE NOT FOUND")
            failure_count += 1
    
    print(f"\n" + "=" * 60)
    print(f"SUMMARY:")
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {failure_count}")
    print(f"📁 Backup files created with .backup extension")

if __name__ == "__main__":
    main()
