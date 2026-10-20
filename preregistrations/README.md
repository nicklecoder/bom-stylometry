# Pre-registrations

These are copied byte for byte from the original project, `Stylometry/`, where
they were written and hashed. Constitution III applies: they are never edited.
A later change is an amendment, appended inside the document with a date, and
its hash is added below.

Each test was written down, with its decision rule, before the measurement it
decides was made. The hash taken at the time is in the original project's
`out/prereg.sha256`. That project was not under version control, so the
earlier versions survive only as these hashes. Each amendment was appended to
the end of the document, so the earlier text is still present unchanged inside
the current file.

| file | sha256 | recorded | state |
|---|---|---|---|
| PREREGISTRATION_2.md | `ac5c3e6b9f576512a42914004e3fb10ae8d071ba0599b075c4e88c1f0e850cbb` | 2026-10-12T05:36:52Z | as registered, before the run |
| PREREGISTRATION_2.md | `f10ac5de8dd56ff8c18a9965092b8d1d2b96945396c7c61c029ce1a125c605ce` | 2026-10-12T05:38:11Z | Amendment 1 and the result |
| PREREGISTRATION_2.md | `641515663c886b41d6d3804c89c8c595b16913cd9bb15485c679039af61b29ee` | 2026-10-12T05:41:41Z | Amendment 2 (current file) |
| PREREGISTRATION_30.md | `7daf18e9a21d7852c27b0ef2d588bcae860e716daad92cce80d12025a41c4bbc` | 2026-10-14 | as registered, before the run |
| PREREGISTRATION_30.md | `d4d1884df87381e2ffccaf0a5e49d621341a66bd62fe0dbc3fb7519843eb8bdb` | 2026-10-14 | Amendment 1 and the result |
| PREREGISTRATION_30.md | `c7c972c2740d93cc117909d4ad64679d14e800db97fb60f4fd4c5dd61a0aa766` | 2026-10-14 | Amendment 2 |
| PREREGISTRATION_30.md | `9aad7ad1e4d01cb06429fa91dcab2e5d435a4e3df5f2db6d24076b4ac5322a9f` | 2026-10-14 | Amendment 3 |
| PREREGISTRATION_30.md | `1e5036484d42165939a5f3514869f56d3f50f87ad1e90700833eae6745ad56fd` | 2026-10-14 | robustness note (current file) |

The registered re-runs are `analyses/wayhi/prereg_event_share.py` (PREREG 2)
and `analyses/wayhi/prereg_jst_then.py` (PREREG 30). Both use the registered
English rule unchanged. The revised rule's figures are reported beside the
registered ones, but they don't replace them.

`tests/test_preregistrations.py` checks that each file still has its current
hash.
