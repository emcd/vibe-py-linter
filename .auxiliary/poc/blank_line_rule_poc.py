#!/usr/bin/env python3
"""
Proof-of-Concept: No Blank Lines in Function Bodies Rule

This script implements REQ-002 from the PRD: "Prohibit blank lines within 
function bodies, so that function implementations remain compact and focused."

Usage:
    python blank_line_rule_poc.py <python_file>

Example:
    python blank_line_rule_poc.py example.py
"""

import sys
import argparse
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass, field

import libcst as cst
from libcst.metadata import MetadataWrapper, PositionProvider


@dataclass
class ViolationContext:
    """Context information for a violation."""
    before_lines: List[str] = field(default_factory=list)
    violation_line: str = ""
    after_lines: List[str] = field(default_factory=list)
    start_line_number: int = 0


@dataclass
class Violation:
    """Represents a linting rule violation."""
    rule_id: str
    filename: str
    line: int
    column: int
    message: str
    severity: str = "error"
    context: Optional[ViolationContext] = None

    def __str__(self) -> str:
        return (f"{self.filename}:{self.line}:{self.column}: "
                f"{self.severity}: {self.message} ({self.rule_id})")
    
    def format_with_context(self) -> str:
        """Format violation with context lines."""
        base_message = str(self)
        
        if not self.context:
            return base_message
        
        lines = [base_message, ""]  # Add blank line after main message
        
        # Show context with line numbers
        current_line = self.context.start_line_number
        
        # Before lines
        for line in self.context.before_lines:
            lines.append(f"  {current_line:3d} | {line}")
            current_line += 1
        
        # Violation line (blank line)
        lines.append(f"> {current_line:3d} | {self.context.violation_line}")
        current_line += 1
        
        # After lines
        for line in self.context.after_lines:
            lines.append(f"  {current_line:3d} | {line}")
            current_line += 1
        
        return "\n".join(lines)


class BlankLineInFunctionVisitor(cst.CSTVisitor):
    """
    Visitor that detects blank lines within function bodies.
    
    Implementation approach:
    1. Track when we enter/exit function bodies
    2. Examine all SimpleStatementLine nodes within functions
    3. Check for empty lines using PositionProvider coordinates
    4. Report violations with precise line numbers
    5. Extract context lines around violations
    """
    
    METADATA_DEPENDENCIES = (PositionProvider,)
    
    def __init__(self, filename: str, source_lines: List[str]):
        self.filename = filename
        self.source_lines = source_lines  # Original source code split by lines
        self.violations: List[Violation] = []
        self.function_stack: List[str] = []  # Track nested functions
        self.function_body_lines: List[int] = []  # Lines within function body
        
    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
        """Enter a function definition."""
        function_name = node.name.value
        is_async = node.asynchronous is not None
        full_name = f"{'async ' if is_async else ''}function {function_name}"
        
        self.function_stack.append(full_name)
        self.function_body_lines = []  # Reset for new function
        
        # Get function start position for context
        try:
            position = self.get_metadata(PositionProvider, node)
            function_start_line = position.start.line
        except KeyError:
            function_start_line = -1
        
        # Store function info for potential violation reporting
        self._current_function_start = function_start_line

    def _extract_context(self, violation_line: int, context_lines: int = 2) -> ViolationContext:
        """Extract context lines around a violation."""
        # Convert to 0-based indexing
        violation_idx = violation_line - 1
        
        # Calculate context bounds
        start_idx = max(0, violation_idx - context_lines)
        end_idx = min(len(self.source_lines), violation_idx + context_lines + 1)
        
        # Extract lines
        before_lines = []
        violation_text = ""
        after_lines = []
        
        for i in range(start_idx, end_idx):
            if i < violation_idx:
                before_lines.append(self.source_lines[i] if i < len(self.source_lines) else "")
            elif i == violation_idx:
                violation_text = self.source_lines[i] if i < len(self.source_lines) else ""
            else:
                after_lines.append(self.source_lines[i] if i < len(self.source_lines) else "")
        
        return ViolationContext(
            before_lines=before_lines,
            violation_line=violation_text,
            after_lines=after_lines,
            start_line_number=start_idx + 1  # Convert back to 1-based
        )

    def _create_violation_with_context(self, line: int, message: str) -> Violation:
        """Create a violation with context information."""
        context = self._extract_context(line)
        
        return Violation(
            rule_id="VBL101",
            filename=self.filename,
            line=line,
            column=1,
            message=message,
            severity="error",
            context=context
        )

    def leave_FunctionDef(self, node: cst.FunctionDef) -> None:
        """Exit a function definition and analyze collected lines."""
        if self.function_stack:
            self.function_stack.pop()
        
        # Analyze collected lines for blank lines
        self._check_for_blank_lines_in_function()
        self.function_body_lines = []

    def visit_SimpleStatementLine(self, node: cst.SimpleStatementLine) -> None:
        """
        Track statement lines within function bodies.
        
        We examine SimpleStatementLine nodes because they represent individual
        statements and can help us detect blank lines between them.
        """
        if not self.function_stack:
            return  # Not inside a function
        
        try:
            position = self.get_metadata(PositionProvider, node)
            start_line = position.start.line
            end_line = position.end.line
            
            # Record lines occupied by this statement
            for line_num in range(start_line, end_line + 1):
                self.function_body_lines.append(line_num)
                
        except KeyError:
            # No position metadata available
            pass

    def visit_SimpleStatementSuite(
        self, node: cst.SimpleStatementSuite
    ) -> None:
        """Handle simple statement suites (like single-line function bodies)."""
        if not self.function_stack:
            return
            
        try:
            position = self.get_metadata(PositionProvider, node)
            start_line = position.start.line
            end_line = position.end.line
            
            for line_num in range(start_line, end_line + 1):
                self.function_body_lines.append(line_num)
                
        except KeyError:
            pass

    def visit_IndentedBlock(self, node: cst.IndentedBlock) -> None:
        """
        Handle indented function bodies.
        
        This is where we can detect blank lines by examining the structure
        of the indented block and looking for EmptyLine nodes.
        """
        if not self.function_stack:
            return
        
        # Check for empty lines within the indented block
        for stmt in node.body:
            if hasattr(stmt, 'leading_lines'):
                for leading_line in stmt.leading_lines:
                    if isinstance(leading_line, cst.EmptyLine):
                        # Found a blank line - this is a violation
                        try:
                            position = self.get_metadata(PositionProvider, stmt)
                            # The empty line is before this statement
                            violation_line = position.start.line - 1
                            
                            message = (f"Blank line found within {self.function_stack[-1]} body. "
                                     f"Function implementations should remain compact and focused.")
                            
                            violation = self._create_violation_with_context(violation_line, message)
                            self.violations.append(violation)
                            
                        except KeyError:
                            # Fallback: report violation without precise line
                            fallback_line = getattr(self, '_current_function_start', 1)
                            message = (f"Blank line found within {self.function_stack[-1]} body. "
                                     f"Function implementations should remain compact and focused.")
                            
                            violation = self._create_violation_with_context(fallback_line, message)
                            self.violations.append(violation)

    def _check_for_blank_lines_in_function(self) -> None:
        """
        Additional check for blank lines using line number analysis.
        
        This method looks for gaps in the line numbers to detect blank lines
        that might not be caught by the EmptyLine approach.
        """
        if len(self.function_body_lines) < 2:
            return  # Not enough lines to have gaps
        
        # Sort and deduplicate line numbers
        sorted_lines = sorted(set(self.function_body_lines))
        
        # Look for gaps that indicate blank lines
        for i in range(len(sorted_lines) - 1):
            current_line = sorted_lines[i]
            next_line = sorted_lines[i + 1]
            
            # If there's a gap > 1, there might be blank lines
            if next_line - current_line > 1:
                # This could indicate blank lines, but we need to be careful
                # not to flag legitimate multi-line statements
                gap_size = next_line - current_line - 1
                
                if gap_size > 0:
                    # Report the first blank line in the gap
                    blank_line = current_line + 1
                    
                    message = (f"Blank line found within {self.function_stack[-1] if self.function_stack else 'function'} body. "
                             f"Function implementations should remain compact and focused.")
                    
                    # Avoid duplicate violations
                    if not any(v.line == blank_line for v in self.violations):
                        violation = self._create_violation_with_context(blank_line, message)
                        self.violations.append(violation)


def check_blank_lines_in_file(file_path: Path) -> List[Violation]:
    """
    Check a Python file for blank lines within function bodies.
    
    Args:
        file_path: Path to the Python file to check
        
    Returns:
        List of violations found
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        UnicodeDecodeError: If the file can't be decoded as text
        libcst.ParserSyntaxError: If the file has syntax errors
    """
    try:
        # Read the file
        content = file_path.read_text(encoding='utf-8')
        source_lines = content.splitlines()
        
        # Parse with LibCST
        module = cst.parse_module(content)
        
        # Create metadata wrapper for position information
        wrapper = MetadataWrapper(module)
        
        # Create and run the visitor with source lines for context
        visitor = BlankLineInFunctionVisitor(str(file_path), source_lines)
        wrapper.visit(visitor)
        
        return visitor.violations
        
    except cst.ParserSyntaxError as e:
        # Handle syntax errors gracefully
        return [Violation(
            rule_id="VBL101",
            filename=str(file_path),
            line=1,
            column=1,
            message=f"Syntax error in file, cannot check for blank lines: {e}",
            severity="warning"
        )]
    except Exception as e:
        # Handle other errors
        return [Violation(
            rule_id="VBL101", 
            filename=str(file_path),
            line=1,
            column=1,
            message=f"Error processing file: {e}",
            severity="warning"
        )]


def main() -> int:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Check Python files for blank lines within function bodies (VBL101)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python blank_line_rule_poc.py example.py
  python blank_line_rule_poc.py src/module.py --context
  python blank_line_rule_poc.py test.py -c -v
  
Rule VBL101: Prohibit blank lines within function bodies so that function 
implementations remain compact and focused.

Use --context to see the lines before and after each violation for better
understanding of the code structure.
        """
    )
    
    parser.add_argument(
        'file',
        type=Path,
        help='Python file to check'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show additional information'
    )
    
    parser.add_argument(
        '--context', '-c',
        action='store_true',
        help='Show context lines around violations'
    )
    
    args = parser.parse_args()
    
    # Validate file exists
    if not args.file.exists():
        print(f"Error: File {args.file} does not exist", file=sys.stderr)
        return 1
    
    if not args.file.is_file():
        print(f"Error: {args.file} is not a file", file=sys.stderr)
        return 1
    
    # Check file extension
    if args.file.suffix != '.py':
        print(f"Warning: {args.file} does not have .py extension", file=sys.stderr)
    
    if args.verbose:
        print(f"Checking {args.file} for blank lines in function bodies...")
    
    # Run the check
    try:
        violations = check_blank_lines_in_file(args.file)
        
        # Report results
        if violations:
            print(f"Found {len(violations)} violation(s):")
            for violation in violations:
                if args.context:
                    print(violation.format_with_context())
                    print()  # Add blank line between violations for readability
                else:
                    print(violation)
            return 1  # Exit with error code for CI/CD integration
        if args.verbose:
            print("✓ No blank lines found in function bodies")
        return 0
            
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())