# CS5 — Reproducible Deployment

## Status

CS5 is **verified / closed** on the Deployment Closure stack.

The reproducibility work is bounded around runtime data paths, committed UI dependencies, the Python runtime contract, and a successful clean-checkout deployment rehearsal.

## Canonical data directory

The production runtime establishes \`JARVIS_DATA_DIR\` before database bootstrap.

The canonical local database path is:

\`<JARVIS_DATA_DIR>/processed/jarvis.db\`

The legacy default remains \`data/processed/jarvis.db\` when no deployment data directory is supplied.

The launcher exposes the same configuration explicitly:

\`.\scripts\run_jarvis.ps1 -DataDir "C:\JARVIS\data"\`

The script also preserves/restores a pre-existing \`JARVIS_DATA_DIR\` environment value.

## Model-provider boundary

The local model remains an external capability provider. \`scripts/run_jarvis.ps1\` requires an explicit or discoverable \`llama-server.exe\` and GGUF model, and the runtime receives only the resolved OpenAI-compatible endpoint/model identity.

Machine-specific executable/model locations are not committed to the repository.

## UI dependency graph

The UI declares exact direct dependency versions and commits \`ui/package-lock.json\`.

Verified deployment commands:

\`cd ui\`
\`npm ci\`
\`npm run build\`

Both commands passed; the production build completed successfully.

## Python runtime contract

The backend has no third-party Python package manifest because the inspected runtime surface is standard-library-only.

The reproducible interpreter contract remains:

- Python **3.12**
- Python standard library only for the backend/runtime
- no Python dependency manifest is required by the current runtime

The clean-checkout rehearsal used Python **3.14.7** because Python 3.12 was not installed on that workstation. It therefore proves the deployment path on the available interpreter but is not a separate Python 3.12 execution receipt.

## Clean-checkout deployment proof — COMPLETE

Final rehearsal checkout:

\`C:\Users\jeoop\JARV1S-CS5-CLEAN\`

Branch:

\`feature/deployment-closure-cs5-reproducible-deployment\`

Verified:

- focused provider-routing verification: **7/7 OK**
- database bootstrap: **PASS**
- real \`llama-server\`: **READY**
- exposed model: \`qwen3-4b-local\`
- AI provider regression during deployment: **11/11 OK**
- core regression during deployment: **3294/3294 OK**
- real interactive JARVIS request: **PASS**
- interactive \`:quit\`: **PASS**
- final \`git status --short\`: **CLEAN**

The real clean-checkout runtime accepted an interactive request and returned:

\`Hello, Master. How can I assist you today?\`

The launcher then exited through \`:quit\` and returned the checkout to a clean working tree.

## CS6 handoff

The historical M28-only CI workflow is retired by CS6.

Canonical CI coverage is now owned by:

\`.github/workflows/deployment-closure-verification.yml\`

CS5 deployment responsibilities are complete. CI verification and closure evidence continue in **CS6 Verification & CI Closure**.
