# CS5 — Reproducible Deployment

## Status

CS5 is an active closure stage. This PR contains the first bounded reproducibility slice; it is **not** a completion receipt.

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

## Remaining reproducibility gaps

### UI dependency lock

`ui/package.json` currently declares React, React DOM, Vite, TypeScript, and related packages as `latest`.

A reproducible clean checkout requires:

1. pinning direct dependency versions;
2. committing `ui/package-lock.json`;
3. changing CI/install behavior from `npm install` to `npm ci`;
4. proving `npm ci && npm run build` from the clean checkout.

The current environment could not reach the npm registry, so a real lockfile was not generated here. This remains an explicit CS5 gate rather than an assumed success.

### Python environment declaration

The backend currently has no committed Python dependency lock/manifest. The closure audit must verify whether the runtime is intentionally standard-library-only or define the required Python package set before CS5 can close.

### Clean-checkout launch proof

After dependency/runtime manifests are fixed, CS5 needs a clean-checkout launch rehearsal using only committed configuration plus explicitly supplied model-provider artifacts.

## Verification planned

```powershell
python -m unittest src.tests.test_database src.tests.test_database_bootstrap -v
python -m unittest discover -s src.core.tests -p "test_*.py"
```

After the UI manifest is pinned:

```powershell
cd ui
npm ci
npm run build
```

CS5 remains open/draft until the full reproducibility contract is satisfied.
