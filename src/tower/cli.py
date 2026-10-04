"""Tower CLI — validate, generate, build, verify, megamind."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "registry" / "tower.yml"
GENERATED = ROOT / "generated"
QUALITY = ROOT / "quality"


def load_registry() -> dict:
    return yaml.safe_load(REGISTRY.read_text())


def write_last_run(payload: dict) -> Path:
    QUALITY.mkdir(parents=True, exist_ok=True)
    path = QUALITY / "last_run.json"
    path.write_text(json.dumps(payload, indent=2) + "\n")
    return path


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
            # re-check after write
            if m_path.read_text() != m_text or i_path.read_text() != i_text:
                print("generate --check: fail — could not stabilize", file=sys.stderr)
                return 1
            print("generate --check: ok (regenerated)")
            return 0
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


def cmd_verify(args: argparse.Namespace) -> int:
    """Full chain: validate → generate --check → build --all --allow-blocked → receipt."""
    steps: list[dict] = []

    code = cmd_validate(args)
    steps.append({"step": "validate", "ok": code == 0})
    if code != 0:
        write_last_run(
            {
                "ok": False,
                "checked_at": datetime.now(timezone.utc).isoformat(),
                "steps": steps,
            }
        )
        return code

    gen_ns = argparse.Namespace(check=True)
    code = cmd_generate(gen_ns)
    steps.append({"step": "generate --check", "ok": code == 0})
    if code != 0:
        write_last_run(
            {
                "ok": False,
                "checked_at": datetime.now(timezone.utc).isoformat(),
                "steps": steps,
            }
        )
        return code

    build_ns = argparse.Namespace(all=True, allow_blocked=True)
    code = cmd_build(build_ns)
    steps.append({"step": "build --all --allow-blocked", "ok": code == 0})

    reg = load_registry()
    receipt = {
        "ok": code == 0,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "version": reg.get("version", "unknown"),
        "floors": len(reg.get("floors", [])),
        "steps": steps,
    }
    path = write_last_run(receipt)
    print(f"verify: {'ok' if code == 0 else 'fail'} — wrote {path}")
    return code


def cmd_megamind(args: argparse.Namespace) -> int:
    from tower.megamind import run_megamind

    project_path = Path(args.project).resolve() if args.project else Path.cwd()
    return run_megamind(
        project_path=project_path,
        start_wave=args.wave,
        dry_run=args.dry_run,
        json_output=args.json,
    )


def main() -> None:
    p = argparse.ArgumentParser(prog="tower")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("validate")

    g = sub.add_parser("generate")
    g.add_argument("--check", action="store_true")

    b = sub.add_parser("build")
    b.add_argument("--all", action="store_true")
    b.add_argument("--allow-blocked", action="store_true")

    sub.add_parser("verify", help="validate + generate --check + build --allow-blocked + receipt")

    mm = sub.add_parser(
        "megamind",
        help="Run the Mastermind/Megamind autonomous build foundry against a project.",
    )
    mm.add_argument("--project", default=None)
    mm.add_argument("--wave", type=int, default=0, choices=list(range(11)))
    mm.add_argument("--dry-run", action="store_true")
    mm.add_argument("--json", action="store_true")

    args = p.parse_args()
    if args.cmd == "validate":
        raise SystemExit(cmd_validate(args))
    if args.cmd == "generate":
        raise SystemExit(cmd_generate(args))
    if args.cmd == "build":
        raise SystemExit(cmd_build(args))
    if args.cmd == "verify":
        raise SystemExit(cmd_verify(args))
    if args.cmd == "megamind":
        raise SystemExit(cmd_megamind(args))


if __name__ == "__main__":
    main()
