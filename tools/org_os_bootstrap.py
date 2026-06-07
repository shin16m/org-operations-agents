"""Put products/org-os on sys.path before tools/org_os.py can shadow the package."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORG_OS_SRC = ROOT / "products/org-os/src"


def ensure_org_os_package() -> None:
    """Call before ``import org_os`` from any tool entry under tools/."""
    stale = sys.modules.get("org_os")
    if stale is not None and not hasattr(stale, "__path__"):
        del sys.modules["org_os"]
    src = str(ORG_OS_SRC)
    if src not in sys.path:
        sys.path.insert(0, src)
