## 1. Configuration Implementation
- [x] 1.1 Update `Configuration` data class in `sources/vibelinter/configuration.py` to include `per_file_ignores`.
- [x] 1.2 Implement parsing logic for `[tool.vibelinter.per-file-ignores]` in `_parse_configuration`.
- [x] 1.3 Add validation for per-file ignore patterns and rule codes.

## 2. Engine Implementation (Suppression)
- [x] 2.1 Update `Engine` to track `noqa` comments during CST traversal or tokenization.
- [x] 2.2 Implement `SuppressionFilter` to match violations against suppression comments.
- [x] 2.3 Update `lint_source` to apply suppression filtering before returning report.

## 3. Engine Implementation (Per-File Ignores)
- [x] 3.1 Update `Engine` to apply per-file configuration overrides.
- [x] 3.2 Implement logic to filter violations based on `per_file_ignores` map.

## 4. Testing
- [x] 4.1 Add unit tests for `per-file-ignores` configuration parsing.
- [x] 4.2 Add integration tests for inline `noqa` suppression.
- [x] 4.3 Add integration tests for per-file rule exclusion.