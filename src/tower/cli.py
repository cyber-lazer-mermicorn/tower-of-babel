"""Minimal Tower CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .registry import load_registry, validate_registry
from .generate import generate_surfaces

ROOT = Path(__file__).resolve().parents[2]


def cmd_validate(_: argparse.Namespace) -> int:
    reg = load_registry(ROOT / "registry" / "tower.yml")
    errors = validate_registry(reg, ROOT)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print(f"validate: ok ({len(reg.get('floors', []))} floors)")
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    reg = load_registry(ROOT / "registry" / "tower.yml")
    errors = validate_registry(reg, ROOT)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    written = generate_surfaces(reg, ROOT, check=args.check)
    if args.check:
        print("generate --check: ok (no drift)")
    else:
        for p in written:
            print(f"wrote {p}")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    reg = load_registry(ROOT / "registry" / "tower.yml")
    results = []
    for floor in reg.get("floors", []):
        evidence = floor.get("evidence", "illustrative")
        status = "ok"
        detail = evidence
        if evidence in {"service_gated", "hardware_gated", "toolchain_gated"}:
            if not args.allow_blocked:
                status = "blocked"
            detail = f"{evidence} (exact blocker declared)"
        results.append({"id": floor["id"], "status": status, "detail": detail})
    print(json.dumps({"results": results}, indent=2))
    blocked = [r for r in results if r["status"] == "blocked"]
    return 1 if blocked and not args.allow_blocked else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tower")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_val = sub.add_parser("validate")
    p_val.set_defaults(func=cmd_validate)

    p_gen = sub.add_parser("generate")
    p_gen.add_argument("--check", action="store_true")
    p_gen.set_defaults(func=cmd_generate)

    p_build = sub.add_parser("build")
    p_build.add_argument("--all", action="store_true")
    p_build.add_argument("--allow-blocked", action="store_true")
    p_build.set_defaults(func=cmd_build)

    args = parser.parse_args(argv)
    return args.func(args)
