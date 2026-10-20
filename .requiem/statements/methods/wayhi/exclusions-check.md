---
id: exclusions-check
namespace: methods/wayhi
kind: design
status: active
tags:
    - wayhi
provenance:
    type: code-derived
    file: analyses/wayhi/exclusions.py
    line_range:
        start: 1
        end: 1
    hash: 5335e2f6396821d29961a0bd3663ef6698a00c26069604139e886ce1af418fe5
created_at: 2026-10-19T14:34:13.244297152Z
relationships:
    - to: methods/wayhi/genre-control
      type: refines
      via: link
---

The exclusions analysis finds every Book of Mormon passage sharing 8-word runs with the KJV and reports the step at which it leaves. 40 passages; 3 keep verses in the frame (1 Nephi 22:20, 3 Nephi 10:4–6, Mormon 9:22–24) and are reported, not removed. It found the Isaiah span bug: 2 Nephi 12:1–24:23 corrected to 24:32 (frame 143,216 → 142,980 words; rate 7.75 → 7.76).
