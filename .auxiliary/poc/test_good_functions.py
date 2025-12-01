#!/usr/bin/env python3
"""
Test file with only good functions (no blank lines in function bodies).
"""

def simple_function():
    """A simple function with no blank lines."""
    x = 1
    y = 2
    return x + y

async def async_function():
    """An async function with no blank lines."""
    result = await some_operation()
    return result

class Calculator:
    """A class with methods that have no blank lines."""
    
    def __init__(self):
        """Initialize the calculator."""
        self.value = 0
    
    def add(self, x, y):
        """Add two numbers."""
        result = x + y
        self.value = result
        return result
    
    def multiply(self, x, y):
        """Multiply two numbers."""
        result = x * y
        self.value = result
        return result

def nested_function():
    """Function with nested function, no blank lines."""
    def inner(x):
        return x * 2
    result = inner(5)
    return result

def multiline_statement():
    """Function with multi-line statements."""
    data = {
        'name': 'test',
        'value': 42,
        'active': True
    }
    result = process(data)
    return result

# Module-level code can have blank lines

global_var = "test"

def some_operation():
    return "operation result"

def process(data):
    return f"processed: {data}"