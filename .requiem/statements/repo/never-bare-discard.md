---
id: never-bare-discard
namespace: repo
kind: rule
modality: must_not
abstract: true
status: active
tags:
    - repo
provenance:
    type: dialogue
created_at: 2026-10-19T14:34:12.120312903Z
---

Never run a bare `requiem discard`: during setup it deleted the uncommitted .requiem/config.yaml and .gitignore (restored by re-running `requiem init`). Discard specific statements only. `requiem commit` is the human approval step; agents and the record bridge never run it.
