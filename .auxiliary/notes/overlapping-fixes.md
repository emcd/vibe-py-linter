# Analysis of Overlapping Fixes and Conflict Detection

## Context
During the implementation of style rules (specifically VBL103: bracket spacing), we encountered an issue where multiple valid fixes on the same line were being blocked. For example, `assert (a) <= (b)` required adding spaces after both `(` characters. The first fix was applied, but the second was rejected as a "conflict" because the line had already been modified.

## Removed Logic
The original `FixEngine` implementation in `fixer.py` contained strict line-blocking logic:

```python
        modified_lines: set[ int ] = set( )
        for fix in sorted_fixes:
            violation = fix.violation
            # Check for overlap with already-applied fixes
            if violation.line in modified_lines:
                # Find the conflicting fix
                conflicting_fixes = [
                    f for f in applied if f.violation.line == violation.line ]
                conflicting = (
                    conflicting_fixes[ 0 ] if conflicting_fixes
                    else applied[ -1 ] if applied else fix )
                conflicts.append( FixConflict(
                    skipped_fix = fix,
                    conflicting_fix = conflicting,
                    reason = f"Line {violation.line} already modified.",
                ) )
                continue
            try:
                module = fix.transformer_factory( module )
                applied.append( fix )
                modified_lines.add( violation.line )
```

## Pros and Cons Analysis

| Approach | Pros | Cons |
| :--- | :--- | :--- |
| **Strict Line Blocking** (Old) | • **Safety:** Guarantees no two fixes interact on the same line.<br>• **Simplicity:** Easy to implement and understand. | • **False Positives:** Blocks valid, non-overlapping fixes (e.g., spacing adjustments at start AND end of line).<br>• **UX:** Requires user to run "fix" multiple times to converge. |
| **No Blocking** (Current Fix) | • **Completeness:** Allows all formatting rules (spacing, quotes, commas) to apply in one pass.<br>• **Efficiency:** Reduces "fix loop" cycles. | • **Collision Risk:** Two rules trying to modify the exact same token might overwrite each other (Last Writer Wins).<br>• **Complexity:** Relies heavily on Transformers to verify their targets still exist. |

## Edge Case Analysis

1.  **Same Rule, Multiple Fixes (The VBL103 Case):**
    *   *Scenario:* `func( a,b )`. Fix 1: Space after `(`. Fix 2: Space before `)`.
    *   *Logic:* These target distinct column positions. By applying them in **reverse position order** (right-to-left), the first fix (rightmost) expands the line but does not shift the coordinates of the second fix (leftmost).
    *   *Verdict:* **Safe.** Removing line blocking is required for this to work.

2.  **Different Rules, Same Node (Parent/Child):**
    *   *Scenario:* Rule A renames `my_func` (Name node). Rule B wraps `my_func()` call in `try...except` (Call node).
    *   *Logic:* Both start at the same position. `FixEngine` applies them sequentially.
        *   Pass 1: Rename `my_func` -> `new_func`.
        *   Pass 2: Transformer looks for `Call` at the starting position. Since the name changed but the structure didn't, it finds the (now modified) node and wraps it.
    *   *Verdict:* **Safe.** Strict conflict detection (like blocking identical start positions) would actually break this valid composition.

3.  **True Collisions (Same Token):**
    *   *Scenario:* Rule A renames `x` to `y`. Rule B renames `x` to `z`.
    *   *Logic:* Pass 1 changes `x` to `y`. Pass 2 looks for `x` at that position but finds `y`.
    *   *Outcome:* The Transformer for Rule B should check `if node.value == 'x':`. Upon seeing `y`, it should return the node unchanged (skipping the fix).
    *   *Verdict:* **Safe (Fail-safe).** As long as Transformers verify their targets (which they do via `METADATA_DEPENDENCIES` and internal checks), the second fix will simply be skipped.

## Conclusion
The "No Blocking" approach is superior because the **Reverse Position Sort** combined with **Transformer Target Verification** provides a natural, robust conflict resolution mechanism.

*   **Right-to-Left application** ensures that modifications don't invalidate pending fixes to the left.
*   **Re-parsing/Re-wrapping** between steps ensures each fix operates on the current state of the tree.
*   **Transformer checks** ensure that if a target node was destroyed or fundamentally altered by a previous fix, the subsequent fix aborts gracefully.
