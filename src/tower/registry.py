"""Registry load + validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore


def load_registry(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if yaml is None:
        raise RuntimeError("PyYAML is required: pip install pyyaml")
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError("registry must be a mapping")
    return data


def validate_registry(reg: dict[str, Any], root: Path) -> list[str]:
    errors: list[str] = []
    floors = reg.get("floors")
    if not isinstance(floors, list) or not floors:
        errors.append("floors must be a non-empty list")
        return errors
    seen: set[str] = set()
    for i, floor in enumerate(floors):
        if not isinstance(floor, dict):
            errors.append(f"floor[{i}] must be a mapping")
            continue
        fid = floor.get("id")
        if not fid or not isinstance(fid, str):
            errors.append(f"floor[{i}] missing id")
            continue
        if fid in seen:
            errors.append(f"duplicate floor id: {fid}")
        seen.add(fid)
        for key in ("what", "where", "when", "why", "how", "evidence", "easy", "advanced"):
            if key not in floor:
                errors.append(f"floor {fid}: missing {key}")
        for path_key in ("easy", "advanced"):
            rel = floor.get(path_key)
            if isinstance(rel, str):
                p = root / rel
                if not p.is_file():
                    errors.append(f"floor {fid}: {path_key} path missing: {rel}")
    return errors
