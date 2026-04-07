#!/usr/bin/env python3
"""Mark network-dependent tests as integration tests."""

import re
from pathlib import Path

# Files that need integration marking
TEST_FILES = {
    'tests/test_stock.py': [
        'test_basic_hist_data',
        'test_hist_data_with_adjust',
        'test_hist_data_eastmoney_direct',
        'test_basic_realtime_data',
        'test_eastmoney_direct_source',
    ],
    'tests/test_options.py': [
        'test_basic_options_chain',
        'test_options_chain_columns',
        'test_options_chain_types',
        'test_options_realtime_for_underlying',
        'test_options_realtime_columns',
        'test_get_options_expirations',
        'test_expirations_sorted',
        'test_expirations_in_chain',
    ],
    'tests/test_api_contract.py': [
        'test_hist_data_golden_sample',
        'test_hist_data_field_types',
        'test_hist_data_required_fields',
        'test_hist_data_value_ranges',
        'test_northbound_flow_value_types',
        'test_options_required_fields',
    ],
    'tests/test_financial.py': [
        'test_basic_balance_sheet',
        'test_basic_income_statement',
        'test_multiple_periods',
        'test_basic_cash_flow',
    ],
}

def add_integration_marker(file_path, test_names):
    """Add @pytest.mark.integration decorator to tests."""
    if not Path(file_path).exists():
        print(f"Skip {file_path} - not found")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ensure pytest is imported
    if 'import pytest' not in content:
        # Find first import line and add after it
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                lines.insert(i, 'import pytest\n')
                break
        content = '\n'.join(lines)
    
    # Add decorators
    modified = False
    for test_name in test_names:
        pattern = rf'(    def {test_name}\(self[^\)]*\):)'
        replacement = r'    @pytest.mark.integration\n    \1'
        
        if pattern in content:
            content = re.sub(pattern, replacement, content)
            modified = True
            print(f"  ✓ Marked {test_name}")
        else:
            print(f"  ✗ Not found: {test_name}")
    
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

if __name__ == '__main__':
    total_fixed = 0
    
    for file_path, tests in TEST_FILES.items():
        print(f"\nProcessing {file_path}...")
        if add_integration_marker(file_path, tests):
            total_fixed += 1
            print(f"✓ Fixed {file_path}")
        else:
            print(f"✗ No changes needed for {file_path}")
    
    print(f"\n{'='*60}")
    print(f"Total files modified: {total_fixed}")
    print(f"Total tests marked: {sum(len(tests) for tests in TEST_FILES.values())}")
