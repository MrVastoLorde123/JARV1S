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

The authoritative backend count remains the current repository regression baseline established through CS5: **3294 core tests**.

The focused CS6 additions are:

- historical interface focused checks;
- current AI local-model policy + provider-model-observation checks.

The UI gate remains \`npm ci\` + \`npm run build\`.

## Merge policy

CS6 remains open/draft/unmerged. No merge is performed as part of this closure stage.
