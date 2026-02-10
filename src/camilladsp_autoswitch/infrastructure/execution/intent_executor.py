"""
Intent Executor.

Responsibilities:
- Execute a SwitchIntent safely
- Enforce idempotency
- Never apply invalid YAML
- Own execution state

This is the execution boundary of the system.
"""

from pathlib import Path


class IntentExecutor:
    """
    Executes intents in an idempotent and fail-safe way.
    """

    def __init__(self, *, validate_fn, apply_fn):
        self._validate_fn = validate_fn
        self._apply_fn = apply_fn
        self.reset()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """Reset execution state (used by tests and daemon startup)."""
        self._last_yaml: Path | None = None
        self._last_validation_ok: bool | None = None

    def configure(self, *, validate_fn=None, apply_fn=None) -> None:
        """
        Rebind dependencies.

        This is REQUIRED so unittest.mock.patch works correctly.
        """
        if validate_fn is not None:
            self._validate_fn = validate_fn
        if apply_fn is not None:
            self._apply_fn = apply_fn

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute(self, intent, yaml_path: Path) -> None:
        """
        Execute an intent.

        Args:
            intent: SwitchIntent
            yaml_path: concrete YAML path

        Guarantees:
        - Invalid YAML is never applied
        - Same YAML is applied only once
        """
        result = self._validate_fn(yaml_path)

        if not result.valid:
            self._last_yaml = yaml_path
            self._last_validation_ok = False
            return

        yaml_changed = yaml_path != self._last_yaml

        if self._last_yaml is None or yaml_changed:
            self._apply_fn(yaml_path)

        self._last_yaml = yaml_path
        self._last_validation_ok = True
