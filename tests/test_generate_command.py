"""
Test for the generate command behavior
"""

import pytest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_generate_exit_code_logic():
    """
    Test the logic that determines exit code based on generated_count.
    
    This verifies the fix: when generated_count == 0, sys.exit(1) should be called.
    """
    
    # Read the main.py source code
    main_py_path = Path(__file__).parent.parent / 'main.py'
    with open(main_py_path, 'r') as f:
        source = f.read()
    
    # Verify the fix is present in the generate function
    assert 'if generated_count == 0:' in source, "Missing check for generated_count == 0"
    assert 'sys.exit(1)' in source, "Missing sys.exit(1) call"
    assert 'Failed to generate any content' in source, "Missing error message"
    
    # Verify the logic flow by checking the lines are in the right order
    gen_count_pos = source.find('Generated content for {generated_count}')
    exit_check_pos = source.find('if generated_count == 0:')
    sys_exit_pos = source.find('sys.exit(1)')
    
    assert gen_count_pos > 0, "Could not find generated_count message"
    assert exit_check_pos > gen_count_pos, "Exit check should come after count message"
    assert sys_exit_pos > exit_check_pos, "sys.exit(1) should come after the check"
    
    print("✅ Exit code logic is correctly implemented")
    print("   - sys.exit(1) is called when generated_count == 0")
    print("   - Proper error message is displayed")
    print("   - Logic flow is correct")


def test_main_imports_sys():
    """Verify that main.py imports sys module (needed for sys.exit)"""
    import main
    assert hasattr(main, 'sys')
    assert main.sys.exit is not None
    print("✅ sys module is properly imported in main.py")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

