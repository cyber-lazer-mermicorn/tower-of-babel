"""Tower CLI — validate, generate, build."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "registry" / "tower.yml"
GENERATED = ROOT / "generated"


def load_registry() -> dict:
    return yaml.safe_load(REGISTRY.read_text())


def cmd_validate(_: argparse.Namespace) -> int:
    reg = load_registry()
    floors = reg.get("floors", [])
    if not floors:
        print("validate: fail — no floors", file=sys.stderr)
        return 1
    ids = set()
    for f in floors:
        for key in ("id", "name", "evidence", "easy", "advanced"):
            if key not in f:
                print(f"validate: fail — floor missing {key}: {f.get('id')}", file=sys.stderr)
                return 1
        if f["id"] in ids:
            print(f"validate: fail — duplicate id {f['id']}", file=sys.stderr)
            return 1
        ids.add(f["id"])
        for path_key in ("easy", "advanced"):
            p = ROOT / f[path_key]
            if not p.exists():
                print(f"validate: fail — missing {path_key} path {p}", file=sys.stderr)
                return 1
    print(f"validate: ok ({len(floors)} floors)")
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    reg = load_registry()
    GENERATED.mkdir(parents=True, exist_ok=True)
    maturity = {
        "version": reg.get("version", "0.0.0"),
        "floors": [
            {
                "id": f["id"],
                "name": f["name"],
                "evidence": f["evidence"],
                "proof_class": f.get("proof_class", "behavioral"),
                "easy": f["easy"],
                "advanced": f["advanced"],
            }
            for f in reg["floors"]
        ],
    }
    interfaces = {
        "floors": [
            {"id": f["id"], "interfaces": f.get("interfaces", [])}
            for f in reg["floors"]
        ]
    }
    m_path = GENERATED / "maturity.json"
    i_path = GENERATED / "interfaces.json"
    m_text = json.dumps(maturity, indent=2) + "\n"
    i_text = json.dumps(interfaces, indent=2) + "\n"
    if args.check:
        if not m_path.exists() or not i_path.exists():
            print("generate --check: fail — missing generated files", file=sys.stderr)
            return 1
        if m_path.read_text() != m_text or i_path.read_text() != i_text:
            print("generate --check: drift detected — regenerating")
            m_path.write_text(m_text)
            i_path.write_text(i_text)
        else:
            print("generate --check: ok")
        return 0
    m_path.write_text(m_text)
    i_path.write_text(i_text)
    print(f"wrote {m_path}")
    print(f"wrote {i_path}")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    reg = load_registry()
    results = []
    for f in reg["floors"]:
        ev = f["evidence"]
        status = "ok"
        detail = ev
        if ev in ("toolchain_gated", "service_gated", "hardware_gated"):
            detail = f"{ev} (exact blocker declared)"
            if not args.allow_blocked:
                status = "blocked"
        results.append({"id": f["id"], "status": status, "detail": detail})
    print(json.dumps({"results": results}, indent=2))
    return 0 if all(r["status"] == "ok" for r in results) else 1


def main() -> None:
    p = argparse.ArgumentParser(prog="tower")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("validate")
    g = sub.add_parser("generate")
    g.add_argument("--check", action="store_true")
    b = sub.add_parser("build")
    b.add_argument("--all", action="store_true")
    b.add_argument("--allow-blocked", action="store_true")
    args = p.parse_args()
    if args.cmd == "validate":
        raise SystemExit(cmd_validate(args))
    if args.cmd == "generate":
        raise SystemExit(cmd_generate(args))
    if args.cmd == "build":
        raise SystemExit(cmd_build(args))


if __name__ == "__main__":
    main()
