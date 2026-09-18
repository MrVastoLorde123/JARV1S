# CS6 — Verification & CI Closure

## Status

CS6 establishes the repository's canonical automated verification boundary for the Deployment Closure program.

It replaces the historical M28-only workflow with one closure workflow that verifies the backend, current AI-routing contract, authoritative core regression, and reproducible UI build.

## Canonical workflow

\`.github/workflows/deployment-closure-verification.yml\`

Triggers:

- pushes to \`main\`;
- pushes to \`feature/deployment-closure-cs*\`;
- pull requests targeting \`main\`;
- pull requests targeting \`feature/deployment-closure-cs*\`;
- manual \`workflow_dispatch\`.

The workflow uses:

- Python **3.12**;
- Node **22**;
- committed \`ui/package-lock.json\` with \`npm ci\`.

## Backend verification boundary

The backend job verifies in this order:

1. repository checkout;
2. Python 3.12 setup;
3. database bootstrap with \`python -m src.database_bootstrap\`;
4. preserved historical interface focused tests;
5. current AI model-policy and provider-model-observation tests;
6. full authoritative core regression:
   \`python -m unittest discover -s src.core.tests -p "test_*.py"\`.

Database bootstrap intentionally precedes the core regression because a clean repository does not contain a generated SQLite schema.

## UI verification boundary

The UI job verifies:

1. Node 22 setup;
2. lockfile-backed dependency installation with \`npm ci\`;
3. production build with \`npm run build\`.

No mutable \`npm install\` step remains in the canonical closure workflow.

## Scope boundary

CS6 verifies repository-level reproducibility and regression coverage.

It does not:

- merge any pull request;
- modify \`main\` directly;
- introduce new runtime architecture;
- create execution authority;
- authorize capabilities;
- replace deterministic authority boundaries;
- require a locally installed model server in CI.

The local model provider remains a deployment input and is covered by provider/routing unit tests rather than live model inference in CI.

## Historical workflow retirement

The historical \`.github/workflows/m28-verification.yml\` was scoped exclusively to \`feature/m28-jarvis-os-prototype\`, used \`npm install\`, and omitted the database bootstrap and authoritative core regression.

It is retired in CS6 so the repository has one canonical closure verification workflow rather than overlapping historical and current CI definitions.

## Verification receipt

The CS6 branch must be accepted only after GitHub Actions executes the new workflow successfully on this branch/PR.

The CS6 receipt records the then-current baseline of **3294 core tests**. The authoritative regression count has since advanced to **3304** through CS8 adversarial coverage.

The focused CS6 additions are:

- historical interface focused checks;
- current AI local-model policy + provider-model-observation checks.

The UI gate remains \`npm ci\` + \`npm run build\`.

## Merge policy

CS6 remains open/draft/unmerged. No merge is performed as part of this closure stage.


## GitHub Actions verification receipt

Final successful run:

- Workflow: **Deployment Closure Verification**
- Run: **#7**
- Backend runtime: **Python 3.12.14**
- Historical interface checks: **18/18 OK**
- Current AI provider/routing checks: **7/7 OK**
- Authoritative core regression: **3294/3294 OK**
- UI runtime: **Node 22.23.2 / npm 10.9.8**
- UI dependency installation: **npm ci PASS** — 24 packages added, 0 vulnerabilities
- UI production build: **PASS** — Vite 8.3.0, 17 modules transformed
- Both CI jobs: **SUCCESS**

The first CS6 run correctly exposed a Python 3.12 portability defect in the regression command: dotted discovery of the namespace-style `src.core.tests` path failed because the imported namespace package had no `__file__`. The workflow was corrected to discover the filesystem path `src/core/tests`; the subsequent run passed the complete 3294-test regression.

GitHub Actions also emitted Node 20 deprecation warnings from the current action wrapper versions. These warnings did not affect the successful verification and are not a CS6 gate failure.

## CS6 status

The canonical verification workflow is implemented and has a successful GitHub Actions receipt on the CS6 branch/PR.
