---
id: results-in-requiem
namespace: principles
kind: principle
modality: must
abstract: true
status: active
tags:
    - constitution
provenance:
    type: dialogue
created_at: 2026-10-19T14:34:11.35983374Z
---

Every analysis's headline is recorded in Requiem as kind result under results/<family>/<analysis>/headline, anchored to line 1 of its fingerprint file so `requiem get` shows stale: true when an input changes. Agents check Requiem before rerunning an analysis and should not rerun one that isn't stale. Method decisions and rejected alternatives are recorded as statements and rejections. Constitution V.
