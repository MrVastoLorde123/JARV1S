# CS5 — Reproducible Deployment

## Status

CS5 is an active closure stage. The reproducibility work is now bounded around runtime data paths, committed UI dependencies, and the Python runtime contract. It is **not** a completion receipt until the clean-checkout rehearsal is recorded.

## Implemented

### Canonical data directory

The production runtime now establishes `JARVIS_DATA_DIR` before database bootstrap.

The canonical local database path is:

```
<JARVIS_DATA_DIR>/processed/jarvis.db
```

The legacy default remains `data/processed/jarvis.db` when no deployment data directory is supplied.

The launcher exposes the same configuration explicitly:

```powershell
.\scripts\run_jarvis.ps1 -DataDir "C:\JARVIS\data"
```

The script also preserves/restores a pre-existing `JARVIS_DATA_DIR` environment value.

This removes the previous split where persistent learning used the configured data directory while legacy conversation/bootstrap persistence could still silently use the repository-relative database path.

### Model-provider boundary

The local model remains an external capability provider. `scripts/run_jarvis.ps1` requires an explicit or discoverable `llama-server.exe` and GGUF model, and the runtime receives only the resolved OpenAI-compatible endpoint/model identity.

Machine-specific executable/model locations are not committed to the repository.

### UI dependency graph

The UI now declares exact direct dependency versions and commits `ui/package-lock.json`:

- React `19.3.0`
- React DOM `19.3.0`
- Vite `8.3.0`
- @types/react `19.3.0`
- @types/react-dom `19.3.0`
- @vitejs/plugin-react `6.1.1`
- TypeScript `7.0.2`

The lockfile is npm lockfile version 3 and records the resolved dependency graph with integrity metadata.

Local verification on the deployment workstation:

```powershell
cd ui
npm ci
npm run build
```

Both commands passed; the production build completed successfully.

## Remaining reproducibility gaps

### Python runtime contract

The backend has no third-party Python package manifest because the inspected runtime surface is standard-library-only. Runtime code uses Python standard-library modules for persistence (`sqlite3`), HTTP transport (`http.server`, `urllib`), filesystem/process control, JSON, typing, and related services.

The reproducible interpreter contract is:

- Python **3.12**
- Python standard library only for the backend/runtime
- no `requirements.txt`, `pyproject.toml`, or Python package lockfile is required by the current runtime

The existing CI configuration targets Python 3.12. A clean-checkout rehearsal performed under another interpreter version does not substitute for a Python 3.12 verification.

This avoids introducing a dependency manifest that would claim packages the runtime does not actually require.

### Clean-checkout deployment proof

The final CS5 proof must start from a clean checkout of this branch and use only committed repository configuration plus explicitly supplied model-provider artifacts.

The rehearsal should prove:

1. the branch checks out cleanly;
2. `python -m src.database_bootstrap` creates the configured data-root database;
3. the backend regression suite is run **after bootstrap** against that initialized database;
4. `cd ui; npm ci; npm run build` succeeds from the committed lockfile;
5. `scripts/run_jarvis.ps1 -DataDir <explicit-data-dir> ...` reaches its normal startup gates;
6. no generated runtime artifacts are required to be committed.

The local model executable and GGUF remain deployment inputs rather than repository dependencies.

### CI boundary

The existing workflow at `.github/workflows/m28-verification.yml` is still scoped to the historical M28 branch. Changing its trigger topology and broadening CI coverage is a **CS6 Verification & CI Closure** concern rather than a CS5 deployment-manifest requirement.

Once CS6 owns that workflow, the UI install step should use `npm ci` because the lockfile is now committed.


## Verification evidence

Verified on the deployment workstation:

```
Database/data-directory tests: 5/5 OK
Core regression: 3294/3294 OK
npm ci: PASS
npm run build: PASS
```

CS5 remains open/draft until the clean-checkout deployment rehearsal is recorded.
