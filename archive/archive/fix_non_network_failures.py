#!/usr/bin/env python3
"""Fix non-network test failures."""

import re
from pathlib import Path

def fix_valuation_providers():
    """Fix Valuation Provider __init__ signatures to accept **kwargs."""
    
    files_to_fix = [
        'src/akshare_one/modules/valuation/eastmoney.py',
        'src/akshare_one/modules/valuation/legu.py',
        'src/akshare_one/modules/index/eastmoney.py',
        'src/akshare_one/modules/index/sina.py',
    ]
    
    for file_path in files_to_fix:
        if not Path(file_path).exists():
            print(f"Skipping {file_path} - file doesn't exist")
            continue
            
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Fix __init__ to accept **kwargs
        # Pattern 1: def __init__(self, start_date: str = ..., end_date: str = ...):
        pattern = r'(def __init__\(self,\s*start_date:\s*str\s*=\s*"[^"]+",\s*end_date:\s*str\s*=\s*"[^"]+"\):)'
        replacement = r'def __init__(self, start_date: str = "\g<1>"**kwargs):'
        
        # Simpler approach: just add **kwargs before the closing parenthesis
        old_pattern = r'(def __init__\(self[^)]+)(\):)'
        new_replacement = r'\1, **kwargs\2'
        
        content = re.sub(old_pattern, new_replacement, content)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"Fixed {file_path}")

def fix_disclosure_st_delist():
    """Fix disclosure get_st_delist_data to accept start_date and end_date."""
    file_path = 'src/akshare_one/modules/disclosure/__init__.py'
    
    if not Path(file_path).exists():
        return
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if function exists and needs fixing
    if 'def get_st_delist_data(' in content:
        print(f"Please check {file_path} manually for get_st_delist_data signature")

if __name__ == '__main__':
    print("Fixing valuation providers...")
    fix_valuation_providers()
    
    print("\nFixing disclosure functions...")
    fix_disclosure_st_delist()
    
    print("\nDone! Please verify the changes.")
