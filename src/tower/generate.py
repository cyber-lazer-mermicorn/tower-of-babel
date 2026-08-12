"""Generate derived surfaces from the registry."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def generate_surfaces(reg: dict[str, Any], root: Path, check: bool = False) -> list[Path]:
    out_dir = root / "generated"
    out_dir.mkdir(exist_ok=True)

    maturity = {
        "version": reg.get("version"),
        "floors": [
            {
                "id": f["id"],
                "name": f.get("name"),
                "evidence": f.get("evidence"),
                "proof_class": f.get("proof_class"),
                "easy": f.get("easy"),
                "advanced": f.get("advanced"),
            }
            for f in reg.get("floors", [])
        ],
    }

    interfaces = {
        "floors": [
            {"id": f["id"], "interfaces": f.get("interfaces", [])}
            for f in reg.get("floors", [])
        ]
    }

    targets = {
        out_dir / "maturity.json": json.dumps(maturity, indent=2) + "\n",
        out_dir / "interfaces.json": json.dumps(interfaces, indent=2) + "\n",
    }

    written: list[Path] = []
    for path, content in targets.items():
        if check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                raise SystemExit(f"drift detected: {path}")
        else:
            path.write_text(content, encoding="utf-8")
            written.append(path)
    return written
