# CS7 — Deployment Acceptance

## Status

CS7 defines the acceptance gate for the reproducible local JARVIS deployment established by CS5 and the automated verification boundary established by CS6.

**Acceptance state: VERIFIED / CLOSED.**

## Acceptance boundary

A deployment is accepted only when the following surfaces agree:

1. **Runtime entrypoint**
   - `scripts/run_jarvis.ps1` is present.
   - The launcher performs repository checks, database bootstrap, model-server readiness, model resolution, regression checks, and JARVIS launch.
   - The launcher supports an explicit persistent `-DataDir`.
   - The launcher supports explicit `-LlamaServerPath` and `-ModelPath`.
   - A server started by the launcher is normally stopped when the session ends.

2. **Canonical runtime**
   - `src/run_local_jarvis.py` establishes the configured data root.
   - The local provider inventory is observed before role routing.
   - The resolved local model identity is supplied to the runtime.
   - The durable database, learning service, control-plane stores, authorization evidence store, and session identity use the configured data root.

3. **Dependency reproducibility**
   - `ui/package-lock.json` is committed.
   - UI dependencies install with `npm ci`.
   - The production UI builds successfully with Node 22.

4. **Verification**
   - CS6 canonical CI remains green.
   - The authoritative core regression remains **3304/3304**.
   - The current AI provider/routing checks remain part of the CI boundary.

5. **Operator documentation**
   - CS5 reproducible deployment documentation exists.
   - CS6 verification/CI documentation exists.
   - The local runtime operator guide documents the actual launcher contract.

## Acceptance workflow

Canonical workflow:

`.github/workflows/deployment-acceptance.yml`

The workflow verifies:

- required deployment files are present;
- launcher/runtime configuration contracts are present;
- UI lockfile installation and production build succeed under Node 22;
- CS5/CS6/operator documentation exists and contains the corresponding acceptance evidence.

This is an acceptance-surface gate, not a substitute for CS6 regression CI and not a live model-inference test.

## Real deployment evidence

CS5 already established the strongest available local deployment receipt:

- clean checkout;
- database bootstrap;
- real `llama-server`;
- `qwen3-4b-local` model exposure;
- AI provider regression **11/11**;
- core regression **3294/3294**;
- real interactive JARVIS response;
- `:quit` clean shutdown;
- final clean working tree.

CS6 independently established the reproducible automated verification boundary with Python 3.12 and Node 22.

CS7 combines those receipts into an explicit acceptance contract; it does not replace either receipt.

## Non-goals

CS7 does not:

- merge PRs;
- modify `main`;
- introduce runtime architecture;
- create or expand execution authority;
- perform live model inference inside GitHub Actions;
- treat an LLM response as deployment authority or truth.

## Final acceptance

CS7 may be marked **VERIFIED / CLOSED** only after the acceptance workflow succeeds on the actual CS7 branch/PR head.


## Final acceptance receipt

The actual CS7 branch head was verified by GitHub Actions.

- Deployment Acceptance workflow on the acceptance branch: **SUCCESS**
- Deployment Closure Verification workflow on the same branch head: **SUCCESS**
- Deployment surface contract: **PASS**
- Node 22 setup: **PASS**
- UI `npm ci`: **PASS**
- UI production build: **PASS**
- Deployment documentation contract: **PASS**
- Acceptance result: **PASS**

The inherited CS6 verification workflow also passed on the same CS7 head, preserving the previously established:

- historical interface checks: **18/18 OK**
- AI provider/routing checks: **7/7 OK**
- authoritative core regression: **3294/3294 OK**

Together with the CS5 real clean-checkout deployment receipt, this establishes the current deployment candidate as accepted across local runtime, automated verification, and acceptance-surface checks.

## CS7 closure

**VERIFIED / CLOSED.**

No merge was performed. The PR remains open/draft/unmerged pending the later closure stages.
