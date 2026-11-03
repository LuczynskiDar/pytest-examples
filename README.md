# pytest-examples
Exercisemyself with pytest

## Pre-commit

Every `git commit` runs `ruff check --fix`, `ruff format` and `mypy` (see `.pre-commit-config.yaml`).
Install the git hook once per clone:

```
uv run pre-commit install
```

Run it manually:

```
uv run pre-commit run --all-files
```

| Command                                           | What it does                                      |
|---------------------------------------------------|---------------------------------------------------|
| `pre-commit run`                                  | only files added to the commit (`git add`)        |
| `pre-commit run --all-files`                      | all files                                         |
| `pre-commit run ruff-check --all-files`           | one hook by `id` (`ruff-check`, `ruff-format`, `mypy`) |
| `pre-commit run --files tests/unit/test_payment.py` | specific files                                  |
| `git commit --no-verify`                          | commit without running the hooks                  |

If a hook modifies files (`Failed (files were modified by this hook)`), run `git add` and commit again.
