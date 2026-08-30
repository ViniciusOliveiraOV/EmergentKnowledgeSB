---
id: adr-0006-human-cognitive-utility
track: core
status: accepted
date: 2026-08-26
---

# Human Cognitive Utility as a success criterion

## Context

`v0.0.1-prealpha` is almost entirely epistemic machinery: provenance,
canonicalization, temporal semantics, ontology, validation, permissions, and
the CORE/INSTANCE boundary. That machinery is correct and load-bearing, and
it is also **the control plane, not the product**.

Nothing built so far measures whether the system makes a person's knowledge
easier to think with. A vault can be schema-perfect and still be a worse
place to look for an answer than the raw conversation it was extracted from.
Nothing in the current validator can detect that, because the validator only
knows about structural integrity.

There is a specific failure mode this project is exposed to: rigour is
measurable and legible, usefulness is neither, so effort drifts toward what
can be checked. The result is a system that is provably consistent and
quietly useless — heavy to maintain, unpleasant to consult, and abandoned.

## Decision

Adopt **Human Cognitive Utility** as a product-level success criterion,
independent of and equal in standing to epistemic integrity.

> A system may report `0 validation errors` and still have failed.

Preserve this architectural distinction:

    CORE                = boring, conservative, auditable, predictable
    INSTANCE EXPERIENCE = intuitive, alive, navigable, cognitively useful

The epistemic mechanisms exist to protect knowledge **invisibly**. In normal
use a person should not have to think about YAML, hashes, provenance
mechanics or ontology. Encountering the machinery during ordinary use is a
design defect, not user error.

The interaction model converges toward five natural operations:

| Operation | The human says |
|---|---|
| **Capture** | "remember this" |
| **Integrate** | "integrate this conversation / source" |
| **Consult** | "what do I currently think about X?" |
| **Navigate** | "how does X connect to Y?" |
| **Review** | "what requires my attention?" |

Maintaining the epistemic machinery is not among them. Anything that forces
the human to hand-maintain schema, provenance or ontology is a cost to be
removed, not a feature.

From Phase 1 onward, every real ingestion is evaluated on **two independent
dimensions**:

    Epistemic Integrity  +  Human Cognitive Utility

**Never optimize the second by weakening the first.** Dropping provenance,
collapsing epistemic states, or overwriting history would all make the system
feel lighter and would destroy what it is for. Humane experience is to be
built *on top of* a rigorous core, not traded against it.

### Evaluation questions

Asked after real ingestions, answered honestly rather than favourably:

- Did the system make the project easier to understand?
- Did it reveal useful connections?
- Did retrieval become easier?
- Is the resulting synthesis more useful than the raw conversation?
- Were important nuances preserved?
- Did the system introduce too much maintenance bureaucracy?
- Did the operator discover something they had not explicitly organized?
- Does the operator actually want to return to the vault?

The last question is the honest summary of the others. Sustained reluctance
to open the vault is a failure signal regardless of how clean validation is.

## Rationale

Stating this now, before the first real corpus, is deliberate. After
ingestion there will be a working system and a natural pull to declare it
successful because it is consistent. A criterion recorded in advance is
harder to quietly redefine to match whatever was built.

Keeping the two dimensions **independent** matters as much as naming the
second. Collapsing them into one score would let a strong result on either
side conceal a failure on the other — and the two failure modes need
different fixes: broken integrity is a bug, low utility is a design problem.

This ADR deliberately specifies **no** UI, dashboard system or automation.
The right shape for those is not knowable before observing where the friction
actually falls during real ingestions. Building an experience layer now would
mean designing against imagined friction.

## Consequences

- Phase 1 and subsequent ingestions produce two assessments, not one. The
  utility assessment is qualitative and written down even when unflattering.
- Maintenance burden becomes a tracked cost. Ceremony that produces no
  cognitive value is a defect, even when it is schema-valid.
- Future features are judged against the five operations. A capability that
  serves none of them needs an explicit reason to exist.
- The public README's ordering is provisional. It currently opens with
  machinery; from `v0.1.0-alpha` it should likely open with the human problem
  and outcome, then explain the machinery underneath. Not changed now —
  rewriting the framing before there is evidence about what the system
  actually does for a person would just be marketing.
- No UI, dashboard system or automation is authorized by this ADR.

## Revisit when

Three to five real ingestions have been evaluated on both dimensions — at
which point the observed friction, not speculation, determines what the
experience layer should be, and the README framing can be rewritten against
evidence.
