#!/usr/bin/env python3
"""Fix invalid source tests to use correct exception type."""

import re
from pathlib import Path

TEST_FILES = [
    'tests/test_insider.py',
    'tests/test_bond.py',
    'tests/test_stock.py',
    'tests/test_etf.py',
    'tests/test_index.py',
    'tests/test_fundflow.py',
    'tests/test_lhb.py',
    'tests/test_limitup.py',
    'tests/test_macro.py',
    'tests/test_margin.py',
    'tests/test_pledge.py',
    'tests/test_restricted.py',
    'tests/test_goodwill.py',
    'tests/test_blockdeal.py',
    'tests/test_northbound.py',
    'tests/test_options.py',
]

def fix_invalid_source_test(file_path):
    """Fix invalid source test in a file."""
    if not Path(file_path).exists():
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Pattern 1: with pytest.raises((ValueError, KeyError)):
    old_pattern1 = r'with pytest\.raises\(\(ValueError, KeyError\)\):\s*(get_\w+\([^)]+\)|\w+Factory\.get_provider\([^)]+\))'
    
    def replacement(match):
        call = match.group(2)
        return f'''from akshare_one.modules.exceptions import InvalidParameterError
        
        with pytest.raises(InvalidParameterError):
            {call}'''
    
    content = re.sub(old_pattern1, replacement, content)
    
    # Write back
    with open(file_path, 'w') as f:
        f.write(content)
    
    return True

if __name__ == '__main__':
    fixed_count = 0
    for file_path in TEST_FILES:
        if fix_invalid_source_test(file_path):
            fixed_count += 1
            print(f"Fixed {file_path}")
    
    print(f"\nTotal fixed: {fixed_count} files")
