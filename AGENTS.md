# Tower Agent Doctrine

## Authority

`registry/tower.yml` (and its declared fragments) is the only authority for:

- technology admission
- W4H placement
- easy and advanced exhibit paths
- evidence state and proof class
- toolchain / build commands
- hardware, service, and toolchain blockers
- cross-language interfaces

Do not add a language or format by editing the README, generated files, or agent maps directly.

## Required workflow

1. Edit the canonical registry (or a declared fragment).
2. Add or update both exhibits.
3. Strengthen the proof gate if needed.
4. Run `python -m tower validate`.
5. Run `python -m tower generate`.
6. Run tests.
7. Run `python -m tower build --all --allow-blocked`.
8. Emit / verify integrity and receipt.
9. Review generated drift before commit.

## Truth classes

A file name containing `advanced` does not establish production maturity.  
Use only the declared evidence state.

Never promote a floor without corresponding evidence.

## Language diversification rule

New technology is admitted only when its What, Where, When, Why, How, interoperability boundary, and proof gate are explicit.  
Existing working components are preserved. No refactor is permitted merely to introduce another language.

## Generated files

Generated surfaces must not be hand-edited. They are overwritten by the generate step.
