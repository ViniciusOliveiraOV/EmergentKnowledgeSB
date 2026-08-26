---
schema_version: 1
type: doc
track: core
id: doc-20260826-provenance
created: 2026-08-26
title: Provenance
---

# Provenance

Every durable claim traces to where it came from. Provenance beats
compression: a beautifully condensed note with no origin is worth less than
a rough one you can audit.

## Normalized, not duplicated

Full metadata lives **once**, in the L0 source note. Knowledge notes carry
only the source `id`. No copying of dates, models, or paths into L1.

    _sources/2026-08-26-chatgpt-attention.md      ← full metadata here
    concepts/Deliberate Practice.md                ← sources: [src-2026...]

## Source note frontmatter

```yaml
schema_version: 1
type: source
id: src-20260826-chatgpt-attention
title: "ChatGPT — attention economy and time sovereignty"
created: 2026-08-26

source_type: chatgpt | claude | codex | paper | book | web | personal_note | voice
source_ref: "conv_68ab12cd"      # native id in origin system, if any
source_path: "_sources/2026-08-26-chatgpt-attention.md"
source_url: "https://..."        # only if publicly resolvable
source_date: 2026-08-24          # when the material was created
authors: [user, gpt-5]           # who produced it
content_hash: "sha256:9f2a..."   # of the raw body, set at ingest, immutable

ingested_at: 2026-08-26T14:03:00-03:00
ingested_by: claude-opus-5
pipeline_version: 0
```

`source_date` is knowledge time (when the material was produced);
`ingested_at` is system time (when it entered the vault). Same distinction
as `asserted_at` vs. `created` — see [[ONTOLOGY]] § Temporal semantics.

`content_hash` is what makes L0 append-only *checkable*. The validator
recomputes it; a mismatch means someone edited raw history, which is a
[[AGENT_RULES]] violation.

## Citing from a knowledge note

Frontmatter lists sources. Individual claims cite inline when it matters:

```markdown
- Attention is the scarce resource, not time. #e/user_position ^claim-a1
  <!-- src: src-20260826-chatgpt-attention L142-L149 -->
```

The `^claim-a1` block ref makes the claim addressable from other notes. The
HTML comment carries the location without cluttering rendered output.

Excerpts: quote sparingly, always with the source id. A quote longer than a
paragraph belongs in L0, linked, not copied into L1.

## Rules

1. Provenance is **recorded at extraction time or never**. Reconstructing it
   later is guessing, and guessed provenance is worse than none.
2. **Never fabricate** a source id, hash, date, line range or URL. If unknown,
   omit the field — or record the imprecision honestly (`asserted_at:
   2026-03` when the transcript says "back in March"). Never sharpen a
   vague date into a precise one to satisfy a parser. An absent field is honest; an invented one is corruption
   that survives decades.
3. A claim with no source and no `#e/user_position` tag is unattributed and
   the validator flags it.
4. Deleting an L0 source orphans every claim derived from it. L0 deletion is
   human-only and should essentially never happen.
