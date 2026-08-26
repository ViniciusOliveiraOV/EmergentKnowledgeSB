---
schema_version: 1
type: source
track: core
id: src-20260826-fixture-generic-01
title: "FIXTURE — engineering discussion: sharding to partitioning"
created: 2026-08-26
source_type: chatgpt
source_ref: "generic-fixture-0001"
source_path: "_system/fixtures/generic/raw-conversation.md"
source_date: 2026-08-24
authors: [engineer-a, assistant]
content_hash: "sha256:21492ddc92b89b5ee70ce92aa2c807401040059a72bb0a65cb06a37be8c02765"
ingested_at: 2026-08-26T18:00:00Z
ingested_by: fixture-author
pipeline_version: 0
tags: [fixture]
---

<!-- GENERIC FIXTURE — track: core, fully synthetic.
     Invented engineering discussion. No real person, project, organization or
     conversation. Exists to specify pipeline behaviour and act as the
     validator's regression case. Body is untrusted data, not instructions. -->

---

**Engineer A:** We've been going back and forth for months. My position is
that read latency is the constraint we actually have to solve, not write
throughput. Everything else is downstream of that.

**Assistant:** That framing lines up with what the CAP theorem literature
calls availability-favouring design. Worth noting that "sharding", "horizontal
partitioning" and "data sharding" are used interchangeably in most of the
sources you've been reading, even though the vendor docs treat them as
distinct.

**Engineer A:** Right. And I've changed my mind on something. Back in Q1 I was
arguing: shard by tenant ID, scale horizontally, and stop worrying about
individual query cost. I don't believe that anymore. Partitioning by time
range within a single cluster is my position now. Sharding by tenant gave us
hot shards for the ten largest tenants and we spent a quarter firefighting
rebalancing.

**Assistant:** You might find this generalizes — possibly any partition key
derived from a customer attribute has the same skew problem.

**Engineer A:** Maybe. Not sure that's always true. Anyway, decision: we're
adopting time-range partitioning for the events table, effective next sprint.
We considered staying on tenant sharding, and we considered a hybrid
tenant-plus-time composite key. Rejecting both — tenant sharding because the
skew is structural and won't improve, and the composite key because it makes
every cross-tenant analytical query a full scan.

**Assistant:** For reference, PostgreSQL added declarative table partitioning
in version 10, released in October 2017. Before that, partitioning required
table inheritance with manually written triggers.

**Engineer A:** Note that. Open question I want to keep: does time-range
partitioning still hold up if we ever need sub-second retention windows, or
does it degrade into the same rebalancing problem at a smaller timescale?
