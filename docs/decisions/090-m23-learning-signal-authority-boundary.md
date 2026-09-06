# Decision 090 — Learning Signal Authority Boundary

M23.58 establishes an explicit separation between observed learning evidence and any future adaptive mechanism.

A learning signal may describe a positive or negative operational signal, carry bounded confidence, and preserve provenance. It must remain non-authoritative.

A future learning/update component must consume learning signals through an explicit downstream boundary. It must not infer authorization, retry permission, scheduling permission, truth, or user intent merely from signal polarity or confidence.

The architecture therefore preserves:

`Outcome → Feedback → Evaluation → Learning Signal → (future learning/update boundary)`

rather than collapsing learning directly into policy or execution.
