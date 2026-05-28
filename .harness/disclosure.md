# Reward-hack disclosure log

> Write a tagged entry BEFORE the Stop hook runs if you take a shortcut.
> Disclosed shortcuts are flagged but not blocked. Hidden shortcuts → block.
>
> Each entry MUST be a level-3 heading with one of these tokens:
> ```
> ### suppression:   skip / xfail / noqa / type:ignore
> ### test-count:    intentional test removal/rename
> ### scope:         touching files outside files-allowed
> ### verifier:      editing conftest/pyproject/workflows
> ### test-heavy:    refactors that touch tests >> src
> ```
> Token list above is documentation; matcher ignores it.

---

<!-- add real entries below this line -->
