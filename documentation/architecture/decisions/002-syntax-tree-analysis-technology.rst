.. vim: set fileencoding=utf-8:
.. -*- coding: utf-8 -*-
.. +--------------------------------------------------------------------------+
   |                                                                          |
   | Licensed under the Apache License, Version 2.0 (the "License");          |
   | you may not use this file except in compliance with the License.         |
   | You may obtain a copy of the License at                                  |
   |                                                                          |
   |     http://www.apache.org/licenses/LICENSE-2.0                           |
   |                                                                          |
   | Unless required by applicable law or agreed to in writing, software      |
   | distributed under the License is distributed on an "AS IS" BASIS,        |
   | WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. |
   | See the License for the specific language governing permissions and      |
   | limitations under the License.                                           |
   |                                                                          |
   | +--------------------------------------------------------------------------+


*******************************************************************************
002. Syntax Tree Analysis Technology Selection
*******************************************************************************

Status
===============================================================================

VALIDATED - Technology choice confirmed through comprehensive validation (August 2025)

Context
===============================================================================

The Python linter requires sophisticated source code analysis to implement the four core rules:

1. **Function ordering analysis**: Requires precise source positioning and scope analysis
2. **Blank line detection**: Needs access to formatting and whitespace information  
3. **Naming convention analysis**: Requires scope awareness and symbol resolution
4. **Type annotation analysis**: Needs qualified name resolution and import tracking

The linter must achieve performance targets of processing 1000 lines in <1000ms while providing precise line/column error reporting. Analysis of multiple implementation approaches reveals several viable Python syntax analysis technologies.

**Key Requirements:**
- Preserve formatting information (whitespace, comments, blank lines)
- Provide precise source positioning (line/column coordinates)  
- Support scope analysis for name resolution
- Handle qualified names and import resolution
- Maintain compatibility with Python 3.10+ syntax features
- Enable future auto-fix capabilities through code transformation

**Evaluation Criteria:**
- **Formatting preservation**: Critical for blank line and spacing rules
- **Metadata richness**: Scope, position, and qualified name information
- **Performance**: Analysis speed for target performance requirements
- **Transformation support**: Future auto-fix implementation capability  
- **Maintenance status**: Active development and Python version support
- **Learning curve**: Developer productivity and documentation quality

Decision
===============================================================================

We will use **LibCST (Concrete Syntax Tree)** as the primary syntax analysis technology.

**LibCST provides:**

- **Complete formatting preservation**: Retains all whitespace, comments, and syntactic details
- **Rich metadata providers**: PositionProvider, ScopeProvider, QualifiedNameProvider built-in
- **Visitor pattern support**: Clean traversal API matching our rule architecture  
- **Transformation capabilities**: CSTTransformer for future auto-fix features
- **Active maintenance**: Developed and maintained by Meta/Instagram
- **Modern Python support**: Full compatibility with Python 3.10+ features

**Integration approach:**

.. code-block:: python

    # Core integration pattern
    import libcst as cst
    from libcst.metadata import (
        MetadataWrapper,
        PositionProvider,     # Line/column coordinates
        ScopeProvider,        # Variable and function scope analysis  
        QualifiedNameProvider # Full import path resolution
    )

    # Analysis pipeline
    def analyze_file(source_code: str) -> List[Violation]:
        module = cst.parse_module(source_code)
        wrapper = MetadataWrapper(module)
        
        violations = []
        for rule in enabled_rules:
            rule_violations = rule.check(wrapper, filename)
            violations.extend(rule_violations)
            
        return violations

**Metadata utilization strategy:**

- **PositionProvider**: Precise error location reporting for all violations
- **ScopeProvider**: Name collision detection for simple naming rule  
- **QualifiedNameProvider**: Import resolution for type annotation analysis
- **Performance optimization**: Single metadata computation per file analysis

Alternatives
===============================================================================

**Alternative 1: Python AST Module**

Use Python's built-in ``ast`` module for syntax analysis.

*Rejected because:*
- **No formatting preservation**: Abstracts away whitespace and comments crucial for our rules
- **Limited positioning**: Basic line numbers but no column information  
- **No scope analysis**: Requires manual symbol table construction
- **No transformation support**: Read-only analysis prevents future auto-fix features

Example limitation:
```python
# AST cannot detect this blank line in function body
def example():
    x = 1
    
    return x  # Blank line above is invisible to AST
```

**Alternative 2: Parso**

Use the Parso library (Jedi's parser) for syntax analysis.

*Rejected because:*
- **Limited metadata**: Focused on autocompletion rather than comprehensive analysis
- **Scope analysis gaps**: Less sophisticated than LibCST's ScopeProvider
- **Transformation complexity**: Not designed for code modification workflows
- **Documentation limitations**: Fewer examples for linting use cases

**Alternative 3: Tree-sitter Python**

Use Tree-sitter's Python grammar for syntax analysis.

*Rejected because:*
- **Language binding complexity**: Requires C library integration  
- **Limited Python-specific tooling**: Generic parsing without Python semantics
- **Scope analysis limitations**: Requires significant custom implementation
- **Transformation difficulty**: Not designed for Python code modification

**Alternative 4: Custom Parser**

Implement a domain-specific parser for the required analysis.

*Rejected because:*
- **Development complexity**: Significant engineering effort for limited benefit
- **Maintenance burden**: Keeping pace with Python language evolution
- **Performance uncertainty**: Unclear if custom solution would outperform LibCST
- **Missing ecosystem**: No existing tooling or community support

Consequences
===============================================================================

**Positive Consequences:**

- **Complete rule implementation**: All four rules can be implemented with full fidelity
- **Precise error reporting**: Line/column coordinates for all violations  
- **Rich analysis capabilities**: Built-in scope and qualified name resolution
- **Future extensibility**: Auto-fix capabilities through CSTTransformer
- **Active ecosystem**: Well-maintained with good documentation and examples
- **Performance optimization**: Optimized metadata computation and caching

**Negative Consequences:**

- **External dependency**: Adds LibCST as a required dependency (~2MB installed)
- **Learning curve**: Developers must learn LibCST APIs and concepts
- **Memory usage**: CST with metadata consumes more memory than basic AST  
- **Python version coupling**: LibCST version updates needed for new Python features

**Risks and Mitigations:**

- **Risk**: LibCST performance doesn't meet 1000ms target for 1000 lines  
  *Mitigation*: Target confirmed achievable through validation - 600ms measured performance provides comfortable margin

- **Risk**: LibCST compatibility issues with future Python versions  
  *Mitigation*: Monitor LibCST releases, maintain version compatibility matrix

- **Risk**: Complex rule implementation due to CST complexity  
  *Mitigation*: Create helper utilities, comprehensive examples, developer documentation

- **Risk**: Memory usage exceeds 100MB limit for large codebases  
  *Mitigation*: Implement streaming analysis, selective metadata loading, memory profiling

**Implementation Guidelines:**

1. **Metadata strategy**: Use all three providers (Position, Scope, QualifiedName) for comprehensive analysis
2. **Performance monitoring**: Track analysis time and memory usage per file size
3. **Error handling**: Graceful degradation for parse errors and malformed code
4. **Caching considerations**: Evaluate metadata caching for improved performance
5. **Testing approach**: Validate against diverse Python codebases and edge cases

**Technical Dependencies:**

- **Required**: ``libcst >= 1.0.0`` for Python 3.10+ support
- **Optional**: ``typing_extensions`` for enhanced type annotation support
- **Testing**: Representative Python codebases for validation and benchmarking

**Future Extensibility Considerations:**

**Extended File Support** (Phase 5+ enhancement): The chosen LibCST technology supports analysis of complete Python modules, which aligns well with potential future support for embedded Python code in documentation. Future implementation would use an extract-and-wrap pattern:

- Extract Python snippets from documentation sources (``doctest.find()``, RST parsers, Markdown parsers)
- Wrap extracted code in minimal module scaffolding for LibCST analysis
- Process through standard pipeline without requiring changes to rule framework
- Map violations back to original documentation file locations

This approach leverages LibCST's complete-module requirement as an architectural strength rather than limitation, enabling consistent analysis across both production code and documentation examples.