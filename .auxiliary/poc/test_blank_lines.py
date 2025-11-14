#!/usr/bin/env python3
"""
Test file for demonstrating the blank line rule.

This file contains both good and bad examples of function implementations
to test the VBL101 rule (no blank lines in function bodies).
"""

def good_function():
    """This function has no blank lines - should pass."""
    x = 1
    y = 2
    return x + y

def bad_function():
    """This function has blank lines - should fail."""
    x = 1
    
    y = 2
    
    return x + y

async def good_async_function():
    """Async function with no blank lines - should pass."""
    result = await some_async_operation()
    processed = process_result(result)
    return processed

async def bad_async_function():
    """Async function with blank lines - should fail."""
    result = await some_async_operation()
    
    processed = process_result(result)
    
    return processed

class ExampleClass:
    """Class with methods to test."""
    
    def good_method(self):
        """Method with no blank lines - should pass."""
        self.value = 42
        return self.value
    
    def bad_method(self):
        """Method with blank lines - should fail."""
        self.value = 42
        
        return self.value

def nested_functions_good():
    """Function with nested function, no blank lines - should pass."""
    def inner():
        return "inner"
    
    result = inner()
    return result

def nested_functions_bad():
    """Function with nested function, has blank lines - should fail."""
    def inner():
        return "inner"
    
    result = inner()
    
    return result

def single_line_function(): return "ok"

def multiline_statement_function():
    """Function with multi-line statements - should pass."""
    data = {
        'key1': 'value1',
        'key2': 'value2',
        'key3': 'value3'
    }
    result = process_data(data)
    return result

def comment_lines_function():
    """Function with comments - should pass if no blank lines."""
    x = 1  # Initialize x
    # Process x
    y = x * 2
    # Return result
    return y

def comment_with_blank_lines_function():
    """Function with comments and blank lines - should fail."""
    x = 1  # Initialize x
    
    # Process x with blank line above
    y = x * 2
    
    # Return result with blank line above
    return y

# Module-level code (not in functions)
module_var = "This is fine"

print("Module-level code can have blank lines")

# Global functions for testing
def some_async_operation():
    return "async result"

def process_result(result):
    return f"processed: {result}"

def process_data(data):
    return str(data)