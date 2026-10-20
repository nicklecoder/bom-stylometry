---
id: genre-control
namespace: methods/wayhi
kind: design
status: active
tags:
    - wayhi
provenance:
    type: code-derived
    file: annotations/embedded.tsv
    line_range:
        start: 1
        end: 1
    hash: 63ef54c32112d3ba52cb150aeedd646bfa43b6fdcbe57e4168b391cd3a92678f
created_at: 2026-10-19T14:34:13.00768749Z
relationships:
    - to: principles/like-for-like
      type: refines
      via: link
---

Genre is controlled in steps shown one at a time: whole text; KJV block quotations out (the Isaiah chapters and Malachi 3–4); embedded speech, letters, prophecies and records out, which also removes KJV parallels inside speech such as the Sermon at the Temple (annotations/embedded.tsv); leaving the narrative frame. The Hebrew side uses 17 narrative units with speech removed. Zeniff's first-person record (Mosiah 9–10) counts as speech by default, with frame-counting reported as sensitivity.
