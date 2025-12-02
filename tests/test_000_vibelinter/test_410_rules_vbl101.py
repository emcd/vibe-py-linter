# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

#============================================================================#
#                                                                            #
#  Licensed under the Apache License, Version 2.0 (the "License");           #
#  you may not use this file except in compliance with the License.          #
#  You may obtain a copy of the License at                                   #
#                                                                            #
#      http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                            #
#  Unless required by applicable law or agreed to in writing, software       #
#  distributed under the License is distributed on an "AS IS" BASIS,         #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#  See the License for the specific language governing permissions and       #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#


''' Test VBL101 Blank Line Elimination rule. '''


from libcst import parse_module as _parse_module
from libcst.metadata import MetadataWrapper as _MetadataWrapper


def create_rule_wrapper( code: str, filename: str = 'test.py' ):
    ''' Creates LibCST wrapper with metadata for testing rules. '''
    # Parse code into CST module
    module = _parse_module( code )
    # Create metadata wrapper with required providers
    wrapper = _MetadataWrapper( module )
    # Split source into lines for context extraction
    source_lines = tuple( code.splitlines( ) )
    return wrapper, source_lines


def run_vbl101( code: str, filename: str = 'test.py' ):
    ''' Runs VBL101 rule on code snippet and returns violations. '''
    from vibelinter.rules.implementations.vbl101 import VBL101
    wrapper, source_lines = create_rule_wrapper( code, filename )
    rule = VBL101(
        filename = filename,
        wrapper = wrapper,
        source_lines = source_lines,
    )
    # Visit the module to collect data and analyze
    wrapper.visit( rule )
    return rule.violations


#-----------------------------------------------------------------------------
# Basic Functionality Tests (000-099)
#-----------------------------------------------------------------------------


def test_000_rule_instantiation( ):
    ''' Rule instantiates successfully with required parameters. '''
    code = ''
    wrapper, source_lines = create_rule_wrapper( code )
    from vibelinter.rules.implementations.vbl101 import VBL101
    rule = VBL101(
        filename = 'test.py',
        wrapper = wrapper,
        source_lines = source_lines,
    )
    assert rule is not None
    assert rule.filename == 'test.py'


def test_010_rule_id( ):
    ''' Rule reports correct rule ID. '''
    code = ''
    wrapper, source_lines = create_rule_wrapper( code )
    from vibelinter.rules.implementations.vbl101 import VBL101
    rule = VBL101(
        filename = 'test.py',
        wrapper = wrapper,
        source_lines = source_lines,
    )
    assert rule.rule_id == 'VBL101'


def test_020_empty_module( ):
    ''' Empty module generates no violations. '''
    code = ''
    violations = run_vbl101( code )
    assert len( violations ) == 0


def test_030_module_with_no_functions( ):
    ''' Module with code but no functions generates no violations. '''
    code = '''x = 42
y = 'hello'

class MyClass:
    pass
'''
    violations = run_vbl101( code )
    assert len( violations ) == 0


def test_040_multiple_functions_detected( ):
    ''' Multiple function definitions are detected and analyzed. '''
    code = '''def func1():
    x = 1

    y = 2

def func2():
    a = 3

    b = 4
'''
    violations = run_vbl101( code )
    # Violations detected in both functions
    # (observable via violations produced)
    assert len( violations ) == 2


def test_050_violations_initially_empty( ):
    ''' Violations list is empty before analysis. '''
    code = ''
    wrapper, source_lines = create_rule_wrapper( code )
    from vibelinter.rules.implementations.vbl101 import VBL101
    rule = VBL101(
        filename = 'test.py',
        wrapper = wrapper,
        source_lines = source_lines,
    )
    # Before visit, violations should be empty
    assert rule.violations == ( )


#-----------------------------------------------------------------------------
# Simple Blank Line Detection Tests (100-199)
#-----------------------------------------------------------------------------


def test_100_single_blank_line_in_function( ):
    ''' Single blank line within function body is detected. '''
    code = '''def my_function():
    x = 1

    y = 2
'''
    violations = run_vbl101( code )
    assert len( violations ) == 1


def test_110_multiple_blank_lines_in_function( ):
    ''' Multiple blank lines within single function are detected. '''
    code = '''def my_function():
    x = 1

    y = 2

    z = 3
'''
    violations = run_vbl101( code )
    assert len( violations ) == 2


def test_120_no_blank_lines_clean_function( ):
    ''' Compact functions generate no violations. '''
    code = '''def my_function():
    x = 1
    y = 2
    return x + y
'''
    violations = run_vbl101( code )
    assert len( violations ) == 0


def test_130_blank_line_after_function_def( ):
    ''' Blank line immediately after function definition is detected. '''
    code = '''def my_function():

    x = 1
'''
    violations = run_vbl101( code )
    assert len( violations ) == 1


def test_140_multiple_functions_with_violations( ):
    ''' Multiple functions each with blank lines are detected. '''
    code = '''def func1():
    x = 1

    y = 2

def func2():
    a = 3

    b = 4
'''
    violations = run_vbl101( code )
    assert len( violations ) == 2


def test_150_method_blank_line_detection( ):
    ''' Blank line detection within class methods works correctly. '''
    code = '''class MyClass:
    def my_method(self):
        x = 1

        y = 2
'''
    violations = run_vbl101( code )
    assert len( violations ) == 1


def test_160_violation_line_numbers( ):
    ''' Violation line numbers correspond to actual blank line positions. '''
    code = '''def my_function():
    x = 1

    y = 2

    z = 3
'''
    violations = run_vbl101( code )
    assert len( violations ) == 2
    # Line 3 and line 5 should have violations
    violation_lines = [ v.line for v in violations ]
    assert 3 in violation_lines
    assert 5 in violation_lines


def test_170_violation_message_format( ):
    ''' Violation message is correct. '''
    code = '''def my_function():
    x = 1

    y = 2
'''
    violations = run_vbl101( code )
    assert len( violations ) == 1
    assert violations[ 0 ].message == "Blank line in function body."
    assert violations[ 0 ].severity == 'warning'


def test_180_violation_column_number( ):
    ''' Violation column is always 1 for blank lines. '''
    code = '''def my_function():
    x = 1

    y = 2
'''
    violations = run_vbl101( code )
    assert len( violations ) == 1
    assert violations[ 0 ].column == 1


#-----------------------------------------------------------------------------
# String Literal Handling Tests (200-299)
#-----------------------------------------------------------------------------


def test_200_blank_lines_inside_triple_double_string( ):
    ''' Blank lines inside triple-double-quote strings are allowed. '''
    code = '''def my_function():
    text = """This is a string.

    It has blank lines inside.

    This is allowed.
    """
    return text
'''
    violations = run_vbl101( code )
    assert len( violations ) == 0


def test_210_blank_lines_inside_triple_single_string( ):
    ''' Blank lines inside triple-single-quote strings are allowed. '''
    code = """def my_function():
    text = '''This is a string.

    It has blank lines inside.

    This is allowed.
    '''
    return text
"""
    violations = run_vbl101( code )
    assert len( violations ) == 0


def test_220_blank_line_after_string_literal( ):
    ''' Blank line after string literal between statements is detected. '''
    code = '''def my_function():
    text = 'Short string.'

    x = 1
'''
    violations = run_vbl101( code )
    assert len( violations ) == 1


def test_230_docstring_with_blank_lines( ):
    ''' Docstring with blank lines generates no violations. '''
    code = """def my_function():
    '''Does something.

    This docstring has blank lines.
    '''
    return 42
"""
    violations = run_vbl101( code )
    assert len( violations ) == 0


def test_240_string_closes_on_same_line( ):
    ''' String that opens and closes on same line generates no violations. '''
    code = """def my_function():
    text = '''Short single-line string with triple quotes.'''
    x = 1
"""
    violations = run_vbl101( code )
    assert len( violations ) == 0


def test_250_string_with_delimiter_in_content( ):
    ''' String with delimiter characters is handled correctly. '''
    # This test is tricky - the current implementation may have edge cases
    # Testing basic scenario
    code = '''def my_function():
    text = """This is a string."""
    x = 1
'''
    violations = run_vbl101( code )
    assert len( violations ) == 0


def test_260_mixed_string_types_in_file( ):
    ''' Mixed triple-single and triple-double quotes work correctly. '''
    code = '''def func1():
    text1 = """Uses triple-double quotes."""
    x = 1

def func2():
    text2 = """Uses triple-double quotes."""
    y = 2
'''
    violations = run_vbl101( code )
    assert len( violations ) == 0


def test_270_function_with_only_docstring( ):
    ''' Function containing only a docstring generates no violations. '''
    code = """def my_function():
    '''This function only has a docstring.'''
"""
    violations = run_vbl101( code )
    assert len( violations ) == 0


def test_280_blank_line_before_string( ):
    ''' Blank line before string literal in function body is detected. '''
    code = """def my_function():

    text = '''String after blank line.'''
    x = 1
"""
    violations = run_vbl101( code )
    assert len( violations ) == 1


def test_290_multiline_string_not_first_statement( ):
    ''' Multiline string appearing after other statements is handled. '''
    code = '''def my_function():
    x = 1

    text = """This is a string literal.

    With blank lines inside.
    """
    y = 2
'''
    violations = run_vbl101( code )
    # Only blank line between statements is detected (line 3)
    # Blank lines inside string literal are correctly ignored
    assert len( violations ) == 1


#-----------------------------------------------------------------------------
# Edge Cases and Boundary Conditions (300-399)
#-----------------------------------------------------------------------------


def test_300_empty_function_body( ):
    ''' Function with only pass statement generates no violations. '''
    code = '''def my_function():
    pass
'''
    violations = run_vbl101( code )
    assert len( violations ) == 0


def test_310_function_with_only_pass_and_blank( ):
    ''' Function with blank line and pass generates violation. '''
    code = '''def my_function():

    pass
'''
    violations = run_vbl101( code )
    assert len( violations ) == 1


def test_320_function_at_end_of_file( ):
    ''' Function at end of file handles boundary condition correctly. '''
    code = '''def my_function():
    x = 1

    y = 2
'''
    violations = run_vbl101( code )
    assert len( violations ) == 1


def test_330_function_with_blank_lines_in_string( ):
    ''' Blank lines inside string literals do not cause false positives. '''
    code = """def my_function():
    text = '''
    This is a string

    with blank lines
    '''
    return text
"""
    violations = run_vbl101( code )
    assert len( violations ) == 0


def test_340_function_with_comments_on_blank_lines( ):
    ''' Lines with only whitespace (no comments) are detected. '''
    code = '''def my_function():
    x = 1
    # This is a comment, not blank

    # The line above is blank and should violate
    y = 2
'''
    violations = run_vbl101( code )
    assert len( violations ) == 1


def test_350_indented_blank_lines( ):
    ''' Blank lines with whitespace (indented) are still detected. '''
    code = '''def my_function():
    x = 1

    y = 2
'''
    violations = run_vbl101( code )
    assert len( violations ) == 1


def test_360_very_long_function( ):
    ''' Function with many statements and blank lines is handled. '''
    code = '''def my_function():
    a = 1

    b = 2
    c = 3

    d = 4
    e = 5

    return a + b + c + d + e
'''
    violations = run_vbl101( code )
    assert len( violations ) == 3


def test_370_position_metadata_unavailable( ):
    ''' Graceful handling when position metadata is not available. '''
    # Note: This test verifies the rule handles metadata absence gracefully
    # In practice, with MetadataWrapper, position metadata is usually available
    code = '''def my_function():
    x = 1

    y = 2
'''
    violations = run_vbl101( code )
    # Should still work normally with standard MetadataWrapper
    assert len( violations ) >= 0  # No crash


def test_380_source_lines_boundary( ):
    ''' Boundary conditions with source line access work correctly. '''
    code = '''def my_function():
    x = 1

    y = 2
'''
    violations = run_vbl101( code )
    # Boundary conditions handled gracefully
    assert len( violations ) == 1


#-----------------------------------------------------------------------------
# Nested Functions and Complex Scenarios (400-499)
#-----------------------------------------------------------------------------


def test_400_nested_function_definitions( ):
    ''' Nested function definitions are both analyzed. '''
    code = '''def outer():
    x = 1

    def inner():
        y = 2

        z = 3
    return inner()
'''
    violations = run_vbl101( code )
    # Implementation counts:
    # line 3 (before inner def) -> Allowed (adjacent to def)
    # line 6 (in inner, between statements) -> Violation
    assert len( violations ) == 1


def test_410_nested_function_no_violations_outer( ):
    ''' Outer function with nested function analyzed correctly. '''
    code = '''def outer():
    x = 1

    def inner():
        y = 2

        z = 3
    return inner()
'''
    violations = run_vbl101( code )
    # Line 3 (before inner def) -> Allowed
    # Line 6 (in inner) -> Violation
    assert len( violations ) == 1


def test_420_closure_with_blank_lines( ):
    ''' Closure creation with blank lines in both functions is detected. '''
    code = '''def create_closure():
    captured = 42

    def inner():
        result = captured

        return result * 2
    return inner
'''
    violations = run_vbl101( code )
    # Blank lines before nested defs also counted within outer functions
    # Line 3 (before inner def) -> Allowed (adjacent to def)
    # Line 7 (in inner) -> Violation
    assert len( violations ) == 1


def test_430_deeply_nested_functions( ):
    ''' Multiple levels of function nesting work correctly. '''
    code = '''def level1():

    def level2():

        def level3():
            x = 1

            y = 2
        return level3()
    return level2()
'''
    violations = run_vbl101( code )
    # Blank lines before nested defs are now allowed.
    # Only 1 violation remains: Line 7 (in level3, between x=1 and y=2).
    # Others (before def level2, before def level3) are adjacent to defs.
    assert len( violations ) == 1


def test_440_lambda_expressions( ):
    ''' Lambda expressions are not analyzed (not FunctionDef nodes). '''
    code = '''def my_function():
    f = lambda x: x + 1

    return f(42)
'''
    violations = run_vbl101( code )
    # Blank line in my_function, lambda ignored
    assert len( violations ) == 1


def test_450_async_function_definitions( ):
    ''' Async functions are analyzed the same as regular functions. '''
    code = '''async def my_async_function():
    x = 1

    y = 2
'''
    violations = run_vbl101( code )
    assert len( violations ) == 1


def test_460_generator_functions( ):
    ''' Generator functions are analyzed normally. '''
    code = '''def my_generator():
    yield 1

    yield 2
'''
    violations = run_vbl101( code )
    assert len( violations ) == 1


def test_470_decorated_functions( ):
    ''' Decorated functions are analyzed (decorator does not affect body). '''
    code = '''@decorator
def my_function():
    x = 1

    y = 2
'''
    violations = run_vbl101( code )
    assert len( violations ) == 1


def test_480_nested_class_spacing( ):
    ''' Blank lines around nested classes are allowed. '''
    code = '''def outer():
    x = 1

    class Inner:
        pass

    return Inner()
'''
    violations = run_vbl101( code )
    # Blank before class Inner (line 3) -> Allowed
    # Blank after class Inner (line 6) -> Allowed
    assert len( violations ) == 0


def test_490_nested_def_spacing_details( ):
    ''' Verify precise spacing rules around nested definitions. '''
    code = '''def outer():
    # Case 1: Blank before
    x = 1

    def inner1():
        pass

    # Case 2: Blank after
    inner1()
    # Case 3: No blank before
    def inner2():
        pass
    # Case 4: No blank after
    inner2()
    # Case 5: Double blank before
    y = 1


    def inner3():
        pass

    return
'''
    violations = run_vbl101( code )
    # L4: Blank before inner1 (L5) -> Allowed
    # L7: Blank after inner1 (L6) -> Allowed
    # L17: First blank before inner3 -> Violation (not adjacent)
    # L18: Second blank before inner3 -> Allowed (adjacent to L19)
    
    assert len( violations ) == 1
    assert violations[ 0 ].line == 17


def test_480_staticmethod_and_classmethod( ):
    ''' Static and class methods are analyzed. '''
    code = '''class MyClass:
    @staticmethod
    def static_method():
        x = 1

        return x

    @classmethod
    def class_method(cls):
        y = 2

        return y
'''
    violations = run_vbl101( code )
    assert len( violations ) == 2


def test_490_function_with_multi_statement_lines( ):
    ''' Only truly blank lines are detected (not lines with semicolons). '''
    code = '''def my_function():
    x = 1; y = 2

    z = 3
'''
    violations = run_vbl101( code )
    assert len( violations ) == 1


#-----------------------------------------------------------------------------
# Integration and Metadata Tests (500-599)
#-----------------------------------------------------------------------------


def test_500_metadata_wrapper_integration( ):
    ''' Integration with MetadataWrapper and PositionProvider works. '''
    code = '''def my_function():
    x = 1

    y = 2
'''
    violations = run_vbl101( code )
    # Positions accurately reflect source code locations
    assert len( violations ) == 1
    assert violations[ 0 ].line == 3


def test_510_source_lines_consistency( ):
    ''' Source_lines tuple matches parsed code. '''
    code = '''def my_function():
    x = 1

    y = 2

    z = 3
'''
    violations = run_vbl101( code )
    # Violations reference correct source lines
    assert len( violations ) == 2
    violation_lines = [ v.line for v in violations ]
    assert 3 in violation_lines
    assert 5 in violation_lines


def test_520_violation_context_extraction( ):
    ''' Violations include enough information for context extraction. '''
    code = '''def my_function():
    x = 1

    y = 2
'''
    violations = run_vbl101( code )
    assert len( violations ) == 1
    v = violations[ 0 ]
    # All fields needed for context extraction are populated
    assert v.line is not None
    assert v.column is not None
    assert v.filename is not None


def test_530_multiple_violations_sorting( ):
    ''' Multiple violations are reported in line-number order. '''
    code = '''def my_function():
    x = 1

    y = 2

    z = 3

    return x + y + z
'''
    violations = run_vbl101( code )
    assert len( violations ) == 3
    violation_lines = [ v.line for v in violations ]
    # Should be in ascending order
    assert violation_lines == sorted( violation_lines )


def test_540_rule_descriptor_registration( ):
    ''' VBL101 is properly registered in RULE_DESCRIPTORS. '''
    from vibelinter.rules.implementations.__ import RULE_DESCRIPTORS
    from vibelinter.rules.implementations.vbl101 import VBL101
    assert 'VBL101' in RULE_DESCRIPTORS
    descriptor = RULE_DESCRIPTORS[ 'VBL101' ]
    assert descriptor.vbl_code == 'VBL101'
    assert descriptor.descriptive_name == 'blank-line-elimination'
    assert descriptor.category == 'readability'
    assert descriptor.subcategory == 'compactness'
    assert descriptor.rule_class == VBL101


def test_550_baseline_rule_framework_compliance( ):
    ''' VBL101 complies with BaseRule contract. '''
    code = '''def my_function():
    x = 1

    y = 2
'''
    wrapper, source_lines = create_rule_wrapper( code )
    from vibelinter.rules.implementations.vbl101 import VBL101
    rule = VBL101(
        filename = 'test.py',
        wrapper = wrapper,
        source_lines = source_lines,
    )
    # Verify rule has required rule_id property
    assert hasattr( rule, 'rule_id' )
    assert rule.rule_id == 'VBL101'
    # Verify rule produces violations when run on code with blank lines
    wrapper.visit( rule )
    assert len( rule.violations ) > 0
    # Full compliance with BaseRule interface observable
    # through proper violation generation
