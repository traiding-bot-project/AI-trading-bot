"""Shared pytest fixtures and import-time stubs for the market_intel_lib tests.

``market_intel_lib.db.__init__`` fetches the database password from Infisical at
import time, so importing any ``market_intel_lib.db.*`` submodule would otherwise
require a live Infisical server. We register a lightweight stub for
``market_intel_lib.secrets`` before those imports happen, keeping the unit tests
hermetic.
"""

import sys
import types


class _StubSecretsManager:
    """Minimal secrets manager returning a dummy value for any secret."""

    def get_secret(self, secret_name: object) -> str:
        """Return a placeholder secret value regardless of the requested name."""
        return "test-secret"


_stub_module = types.ModuleType("market_intel_lib.secrets")
_stub_module.secrets_manager = _StubSecretsManager()
sys.modules.setdefault("market_intel_lib.secrets", _stub_module)
