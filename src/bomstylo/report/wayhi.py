"""Tables and values for reports/wayhi.md. Each fragment reads only result files
(and the manifest / registry for the sources and questions sections)."""
from __future__ import annotations

from .. import genre, results


# --- formatting ------------------------------------------------------------------------
def table(head: list[str], rows: list[list]) -> str:
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"]
    out += ["| " + " | ".join("" if c is None else str(c) for c in r) + " |" for r in rows]
    return "\n".join(out) + "\n"


def f(x, d=2):
    return "—" if x is None else f"{x:,.{d}f}"


def pct(x, d=0):
    return "—" if x is None else f"{100 * x:.{d}f}%"


def ci(lo, hi, d=2, as_pct=False):
    if lo is None or hi is None:
        return ""
    return f"({pct(lo, d - 2 if d > 2 else 0)}–{pct(hi, d - 2 if d > 2 else 0)})" if as_pct else f"({lo:.{d}f}–{hi:.{d}f})"


def share(s) -> str:
    """[k, n, share, lo, hi] or [share, lo, hi] → '70% (67–73%), 775/1,110'."""
    if len(s) == 5:
        k, n, p, lo, hi = s
        return "—" if p is None else f"{pct(p)} {ci(lo, hi, as_pct=True)}, {k:,}/{n:,}"
    p, lo, hi = s
    return "—" if p is None else f"{pct(p)} {ci(lo, hi, as_pct=True)}"


def D(data, aid):
    return data[aid]["data"]


# --- front matter ------------------------------------------------------------------------
def headlines(data, reg):
    out = []
    for aid, a in reg.items():
        hs = data[aid]["headline"]
        out.append(f"- **{a.title}** ([`{aid}`](#{aid}), {a.label})." + ("" if len(hs) > 1 else f" {hs[0]['text']}"))
        if len(hs) > 1:
            out += [f"  - {h['text']}" for h in hs]
    return "\n".join(out) + "\n"


def questions(data, reg):
    return table(["analysis", "label", "question", "why it was asked"],
                 [[f"[`{a.id}`](#{a.id})", a.label, a.question, a.why] for a in reg.values()])


def sources(data, reg):
    out = []
    for s in results.manifest()["sources"]:
        users = [a.id for a in reg.values() if s["id"] in a.corpora]
        if not users:
            continue
        out += [f"**`{s['id']}`: {s['title']}.**", "",
                f"- Edition: {s.get('edition', '—')}", f"- Cite as: {s.get('citation', '—')}",
                f"- Licence: {s.get('licence', '—')}"]
        for r in s.get("raw", []):
            if "url_template" in r:
                out.append(f"- Files: {len(r['files'])} from `{r['url_template']}`")
            else:
                urls = r.get("urls") or [r["url"]]
                pin = f" (sha256 `{r['sha256'][:16]}…`)" if "sha256" in r else ""
                out.append(f"- Download: <{urls[0]}>{pin}" + (f"; fallback <{urls[1]}>" if len(urls) > 1 else ""))
                if "citation" in r:
                    out.append(f"  - Also used: {r['citation']} Licence: {r.get('licence', '—')}")
        out.append(f"- Preparation: step `{s['prepare']}` in `src/bomstylo/prepare.py`; prepared files pinned in "
                   f"`corpora/checksums/{s['id']}.sha256`.")
        if s.get("notes"):
            out.append(f"- Notes: {s['notes']}")
        out += [f"- Read by: {', '.join(f'`{u}`' for u in users)}", ""]
    return "\n".join(out)


# --- methods ----------------------------------------------------------------------------------
def quotation_spans(data, reg):
    d = D(data, "exclusions")
    k = d["span_kinds"]
    rows = [[s, "step 2 onward"] for s in d["quotation_spans"]]
    return (table(["KJV block quotation (layer `quotation`)", "out of the comparison"], rows) +
            f"\nThe annotation has {d['n_spans']} spans: {k.get('quotation', 0)} KJV block quotations and "
            f"{d['n_spans'] - k.get('quotation', 0)} embedded speeches, letters, prophecies and records "
            f"({', '.join(f'{v} {n}' for n, v in sorted(k.items()) if n != 'quotation')}).\n")


def parallels(data, reg):
    rows = []
    for p in D(data, "exclusions")["passages"]:
        n = len(p["frame_verses"])
        flag = f"**{'all' if n == p['verses'] else n} verse{'s' * (n != 1)} in frame, {p['frame_words']} words**" if n else ""
        rows.append([p["bom"], p["kjv"], p["verses"], p["leaves_at"], flag])
    return table(["Book of Mormon", "KJV (best match)", "verses", "leaves the comparison at", "note"], rows)


def hebrew_units(data, reg):
    u = D(data, "genre-ladder")["units"]
    rows = []
    for lab, book, a, z in genre.HEBREW_UNITS:
        x = u[lab]
        c = x["counts"]
        rows.append([lab, f"{book} {a}–{z}" if a != z else f"{book} {a}", f(x["frame_words"], 0),
                     c.get("past_time", 0), c.get("past_verb", 0), f(x["setting_per1k"])])
    return table(["unit", "chapters", "frame words (KJV scale)", "setting-first wayhi", "ordinary-verb wayhi",
                  "setting-first per 1,000"], rows)


def calibration(data, reg):
    k = D(data, "kjv-rendering")["rule_agreement_on_settings"]
    a = D(data, "english-rule-audit")
    g = D(data, "greek-egeneto")["calibration"]
    rows = []
    for rule in ("revised", "registered"):
        ok, n = k[rule]["past"]
        fo, fn = k[rule]["future"]
        rows.append([rule, f"{ok}/{n} ({pct(ok / n)})", f"{fo}/{fn} ({pct(fo / fn)})",
                     f"{a[rule]['agree']}/{a['n']} {ci(a[rule]['share'][1], a[rule]['share'][2], as_pct=True)}"])
    gs = g["setting"]
    return (table(["English rule", "KJV past settings (Hebrew known)", "KJV future settings",
                   "Book of Mormon hand audit (120)"], rows) +
            f"\nOn the Greek: the revised rule agrees on {gs.get('rule_agrees', 0)} of {gs.get('rendered', 0)} "
            f"setting-first ἐγένετο the KJV renders with the phrase.\n")


# --- results ----------------------------------------------------------------------------------
def res_published_claims(data, reg):
    d = D(data, "published-claims")
    t1 = table(["published figure", "published", "measured", "note"],
               [[c["claim"], f"{c['published']:,}", "—" if c["measured"] is None else f"{c['measured']:,}", c["note"]]
                for c in d["checks"]])
    t2 = table(["passage", "words", "'it came to pass'", "per 1,000"],
               [[k, f"{v['words']:,}", v["phrase"], f(v["per1k"])] for k, v in d["named_passages"].items()])
    return t1 + "\nThe phrase in passages the same literature names:\n\n" + t2


def res_hebrew_forms(data, reg):
    d = D(data, "hebrew-forms")
    t1 = table(["counting rule", "count"], [[k, f"{v:,}"] for k, v in d["counting_rules"].items()])
    named = [[f"`{m}`", d["form_names"][m], n] for m, n in d["by_morph"].items() if m in d["form_names"]]
    rest = {m: n for m, n in d["by_morph"].items() if m not in d["form_names"]}
    t2 = table(["form (morphology)", "meaning", "count"],
               named + [[f"{len(rest)} other forms", "plain (non-consecutive) perfects, participles, imperatives, "
                         "infinitives and other persons; counted only by the every-form rule", sum(rest.values())]])
    b = d["buckets"]
    t3 = table(["", "setting-first", "straight to event", "ordinary verb"],
               [[t, b[t].get("time", 0), b[t].get("event", 0), b[t].get("verb", 0)] for t in ("past", "future")])
    return t1 + "\n" + t2 + "\nBy bucket (Hebrew rule), past = *wayhi*, future = *wehayah*:\n\n" + t3


def res_kjv_rendering(data, reg):
    d = D(data, "kjv-rendering")
    names = {"past|time": "wayhi, setting-first", "past|verb": "wayhi, ordinary verb",
             "past|event": "wayhi, straight to event", "future|time": "wehayah, setting-first",
             "future|verb": "wehayah, ordinary verb", "future|event": "wehayah, straight to event"}
    rows = [[names.get(k, k), v["verses"], v["rendered"], pct(v["share"], 1)]
            for k, v in sorted(d["rendering"].items(), key=lambda kv: list(names).index(kv[0]) if kv[0] in names else 99)]
    t = table(["Hebrew form and bucket", "single-form verses", "KJV says 'came / shall come to pass'", "share"], rows)
    o, tot = d["kjv_orphans"].get("past", 0), d["kjv_totals"]["past"]
    return (t + f"\nKJV past 'it came to pass' with no *wayhi* in the verse: {o} of {tot} ({pct(o / tot)}). "
            f"Verses whose Hebrew and English numbering differ: {d['unmatched_verses']} (left out).\n")


def res_english_rule_audit(data, reg):
    d = D(data, "english-rule-audit")
    rows = [[r, f"{d[r]['agree']}/{d['n']}", share(d[r]["share"]), ", ".join(d[r]["disagreements"]) or "none"]
            for r in ("revised", "registered")]
    return table(["rule", "agrees", "share (95% CI)", "disagreements"], rows) + \
        f"\nHand labels: {d['hand'].get('time', 0)} setting-first, {d['hand'].get('event', 0)} straight to the event.\n"


def _lvl_rows(lv):
    rows = []
    for name in genre.BOM_LEVELS:
        x = lv[name]
        c, w = x["counts"], x["words"]
        p = c.get("past_time", 0) + c.get("past_event", 0)
        rows.append([name, f"{w:,}", c.get("past_time", 0), c.get("past_event", 0),
                     c.get("future_time", 0) + c.get("future_event", 0), f(1000 * p / w)])
    return rows


def res_bom_buckets(data, reg):
    d = D(data, "bom-buckets")
    h = ["genre level", "words", "past, setting-first", "past, straight to event", "future (all)", "past per 1,000"]
    out = "Current text, revised rule:\n\n" + table(h, _lvl_rows(d["current|revised"]))
    out += "\n1830 text (current + uses removed after 1830), revised rule:\n\n" + table(h, _lvl_rows(d["1830|revised"]))
    es = d["event_share"]
    out += "\n" + table(["straight-to-event share", "value"], [[k, share(v)] for k, v in es.items()])
    rows = []
    for n, x in d["narrators"].items():
        s = x["revised"]["event_share"]
        if s[1]:
            rows.append([n, s[1], share(s), share(x["registered"]["event_share"])])
    out += "\nBy narrator (narrative frame, current text):\n\n" + table(
        ["narrator", "past uses", "straight to event (revised)", "(registered)"], rows)
    e = d["e1830"]
    rb = d["removed_by_bucket"]
    out += (f"\n1830 alignment: of {e['old_total']:,} past uses in the 1830 OCR, {e['status']['present']:,} are in "
            f"the current text, {e['status']['removed']} were removed after 1830 ({rb.get('past_time', 0)} "
            f"setting-first, {rb.get('past_event', 0)} straight to the event), and "
            f"{e['status']['unmatched (OCR)']} could not be aligned because of OCR damage (treated as present). "
            f"Reverse direction: {e['reverse']['absent from 1830']} current-text uses were not found in the 1830 "
            f"OCR by the aligner ({e['reverse']['unmatched']} more unalignable).\n")
    z = d["sensitivity_zeniff_as_frame"]
    zc = z["current"]
    out += (f"\nSensitivity, Zeniff's first-person record (Mosiah 9–10) counted as frame: {zc['words']:,} words, "
            f"{zc['counts'].get('past_time', 0)} setting-first, {zc['counts'].get('past_event', 0)} straight to "
            f"the event ({f(1000 * (zc['counts'].get('past_time', 0) + zc['counts'].get('past_event', 0)) / zc['words'])} "
            f"per 1,000).\n")
    return out


def res_genre_ladder(data, reg):
    d = D(data, "genre-ladder")
    rows = []
    for x in d["ladder"]:
        lo, hi = x["ratio_hebrew_ci"]
        lo2, hi2 = x["ratio_hebrew_1830_ci"]
        rows.append([x["hebrew_level"], x["bom_level"], f(x["kjv"]), f(x["hebrew_setting"]), f(x["bom"]),
                     f(x["bom_1830"]), f"{x['ratio_hebrew']:.1f}× {ci(lo, hi, 1)}",
                     f"{x['ratio_hebrew_1830']:.1f}× {ci(lo2, hi2, 1)}"])
    out = table(["Hebrew side", "Book of Mormon side", "KJV English per 1,000", "Hebrew setting-first per 1,000",
                 "BoM per 1,000", "BoM 1830", "ratio (current)", "ratio (1830)"], rows)
    b = d["buckets"]
    names = {"past_time": "past, setting-first", "past_event": "past, straight to event",
             "past_verb": "past, ordinary verb", "future_time": "future, setting-first",
             "future_event": "future, straight to event", "future_verb": "future, ordinary verb"}
    rows = []
    for k, n in names.items():
        x = b[k]
        h = x["hebrew"]
        r = x["ratio_ci"]
        rows.append([n, f"{h[0]} = {f(h[1])} {ci(h[2], h[3])}", f"{x['bom'][0]} = {f(x['bom'][1])}",
                     f"{x['bom_1830'][0]} = {f(x['bom_1830'][1])}",
                     "—" if r is None else f"{(x['bom'][1] / h[1]) if h[1] else 0:.2f}× {ci(r[0], r[1])}"])
    out += "\nNarrative frame by bucket (17 Hebrew units vs the Book of Mormon frame), per 1,000 words:\n\n"
    out += table(["bucket", "Hebrew", "Book of Mormon", "BoM 1830", "BoM ÷ Hebrew"], rows)
    k = d["kjv_ot_event_share"]
    out += (f"\nHebrew instances whose verse the WEB numbers differently (counted as frame): {d['hebrew_unaligned']}. "
            f"KJV Old Testament English, straight-to-the-event share: {share(k)}.\n")
    return out


def res_per_verb(data, reg):
    d = D(data, "per-verb")
    rows = []
    for k, r in d["per_100_verbs"].items():
        rows.append([k] + [f"{f(r[x][0])} {ci(r[x][1], r[x][2])}" for x in ("setting", "event", "total")])
    out = table(["per 100 verbs, past, narrative frame", "setting-first", "straight to event", "total"], rows)
    v = d["validation"]
    out += (f"\nCheck: in the same 17 units the KJV has {v['kjv_verbs_per_hebrew_verb']:.3f} verbs per Hebrew verb "
            f"but {v['kjv_words_per_hebrew_word']:.2f} words per Hebrew word. Words per verb: "
            + "; ".join(f"{k} {x:.2f}" for k, x in v["words_per_verb"].items()) + ".\n")
    out += "\nPer 1,000 words, by which words are counted:\n\n" + table(
        ["rate", "per 1,000"], [[k, f(x)] for k, x in d["per_1k"].items()])
    return out


def res_greek(data, reg):
    d = D(data, "greek-egeneto")
    rows = [[b] + [c.get(k, 0) for k in ("setting", "event", "sub", "verb")] for b, c in d["by_book"].items() if c]
    out = table(["book", "setting-first", "straight to event", "subordinate", "ordinary verb"], rows)
    c = d["calibration"]
    out += "\nKJV rendering, verses with one ἐγένετο: " + "; ".join(
        f"{k} {c[k].get('rendered', 0)}/{c[k].get('verses', 0)}" for k in ("setting", "event", "sub", "verb")) + ".\n\n"
    rows = []
    for lab, r in d["rows"].items():
        lo, hi = r["bom_ratio_1k"] or (None, None)
        lo2, hi2 = r["bom_ratio_verbs"] or (None, None)
        rows.append([lab, f"{r['setting']} + {r['event']}", f(r["per_1k"][2]), f(r["per_100_verbs"]),
                     share(r["event_share_ci"]), f"{r['bom_ratio']:.1f}× {ci(lo, hi, 1)}",
                     f"{r['bom_ratio_per_verb']:.1f}× {ci(lo2, hi2, 1)}"])
    b = d["bom_1830"]
    rows.append(["Book of Mormon 1830 frame", "", f(b["per_1k"]), f(b["per_100_verbs"]), pct(b["event_share"]), "", ""])
    out += table(["narrative frame", "setting + event", "per 1,000 KJV words", "per 100 Greek verbs",
                  "straight to event", "BoM ÷ this, per word", "per verb"], rows)
    return out


def res_event_shares(data, reg):
    t = D(data, "event-shares")["texts"]
    names = sorted({k.rsplit(" | ", 1)[0] for k in t}, key=lambda n: list(t).index(n + " | registered"))
    rows = []
    for n in names:
        r, g = t[n + " | revised"], t[n + " | registered"]
        rows.append([n, f"{r['words']:,}", f"{r['event'] + r['time']:,}", f(r["per_1k"]),
                     f"{r['event']}/{r['event'] + r['time']} = {share(r['share'])}", share(g["share"])])
    bb = D(data, "bom-buckets")["event_share"]
    rows.append(["*Book of Mormon, narrative frame (bom-buckets)*", "", f"{bb['current'][1]:,}", "", share(bb["current"]),
                 share(bb["current, registered rule"])])
    out = table(["text", "words", "past uses", "per 1,000", "straight to event (revised rule)", "(registered rule)"], rows)
    d = D(data, "event-shares")
    J = d["jst_revised"]
    out += "\nJST, revised rule:\n\n" + table(
        ["panel", "added", "kept from the KJV", "added (boundary-corrected)"],
        [[p, share([J["panels"][p]["added"]["event"], J["panels"][p]["added"]["n"], *J["panels"][p]["added"]["share"]]),
          share([J["panels"][p]["retained"]["event"], J["panels"][p]["retained"]["n"], *J["panels"][p]["retained"]["share"]]),
          share([J["boundary_corrected"][p]["added"]["event"], J["boundary_corrected"][p]["added"]["n"],
                 *J["boundary_corrected"][p]["added"]["share"]])] for p in J["panels"]])
    out += f"\nAbraham vs Moses (revised rule), Fisher's exact test: p = {d['abraham_vs_moses_fisher_p']:.2f}.\n"
    return out


def res_egyptian(data, reg):
    d = D(data, "egyptian")
    yn = lambda b: "yes" if b else "no"   # noqa: E731
    rows = []
    for title, x in d["named"]["texts"].items():
        rows.append([title, x["period"], x["genre"], x["composed"], f"{x['tokens']:,}", x["total"],
                     f(x["per1k_translated"]), yn(x["date_ok"]), yn(x["genre_ok"]),
                     "yes" if x["matched"] and not x["below_floor"] else ("under 500 tokens" if x["below_floor"] else "no")])
    out = table(["text", "stage", "genre", "composed", "tokens", "particles", "per 1,000 est. translation words",
                 "date ok", "genre ok", "matched"], rows)
    out += "\nPooled by stage (texts of 500 tokens or more):\n\n" + table(
        ["group", "texts", "tokens", "particles", "per 1,000 tokens", "per 1,000 est. translation words"],
        [[k, g["n_texts"], f"{g['tokens']:,}", g["total"], f(g["per1k_tokens"]), f(g["per1k_translated"])]
         for k, g in d["named"]["groups"].items()])
    out += "\nTranslation words per Egyptian token, measured in each TLA subset: " + "; ".join(
        f"{k} {v['expansion']:.2f}" for k, v in d["subsets"].items()) + ".\n\n"
    out += "25th–26th-dynasty hieroglyphic royal inscriptions (the Saite check):\n\n" + table(
        ["inscription", "tokens", "old particles", "ḫpr openings", "per 1,000 (×1.47 scale)", "note"],
        [[k, f"{v['tokens']:,}", v["old_particles"], v["hpr_initial"], f(v["per_1k"]),
          "under 500 tokens" if v["below_floor"] else ""] for k, v in d["hieroglyphic"].items()])
    out += "\nDemotic ḫpr openings, TLA narrative sentences (selected by rule; genre not matched):\n\n" + table(
        ["selection", "sentences", "German words", "ḫpr openings", "per 1,000", "setting-first", "straight to event",
         "date ok"],
        [[k, f"{v['sentences']:,}", f"{v['words']:,}", v["n"], f"{f(v['all_per_1k'][0])} {ci(*v['all_per_1k'][1:])}",
          v["time"], v["event"], yn(v["date_ok"])] for k, v in d["demotic"].items()])
    out += "\npRylands 9 (c. 513 BC; a petition; genre not matched):\n\n" + table(
        ["selection", "sentences", "German words", "openings", "per 1,000", "setting-first", "straight to event"],
        [[k, f"{v['sentences']:,}", f"{v['words']:,}", v["openings"], f"{f(v['per_1k'][0])} {ci(*v['per_1k'][1:])}",
          v["time_first"], v["event_first"]] for k, v in d["rylands"].items()])
    m = d["additive_model"]
    b = m["bom_1830"]
    rows = [[k, f(r["time"][0]), f"{f(r['event'][0])} {ci(*r['event'][1:])}" if r["event"][1] != r["event"][0] else f(r["event"][0]),
             f"{f(r['total'][0])} {ci(*r['total'][1:])}" if r["total"][1] != r["total"][0] else f(r["total"][0]),
             yn(r["matched"])] for k, r in m["rows"].items()]
    rows.append(["**Book of Mormon, 1830 frame**", f(b["time"]), f(b["event"]), f(b["total"]), ""])
    out += "\nAdditive model, per 1,000 words (Hebrew setting-first only; its straight-to-event bucket is empty):\n\n"
    out += table(["model", "setting-first", "straight to event", "total", "Egyptian side matched"], rows)
    lo, hi = d["matched_range"]
    out += f"\nMatched narratives, by text: {f(lo)}–{f(hi)} per 1,000 estimated translation words.\n"
    return out


def res_exclusions(data, reg):
    d = D(data, "exclusions")
    return (f"{len(d['passages'])} passages found (table in Methods). Passages that keep verses in the narrative "
            f"frame:\n\n" + table(["passage", "KJV", "frame verses", "words"],
                                  [[x["bom"], x["kjv"], ", ".join(x["frame_verses"]), x["frame_words"]]
                                   for x in d["in_frame"]]))


def res_prereg2(data, reg):
    d = D(data, "prereg-event-share")
    rows = [["Egyptian particles, pooled (E)", d["egyptian_pooled"].get("event", 0), d["egyptian_pooled"].get("time", 0), f(d["E"])],
            ["Hebrew wayhi, 17 units (H)", d["hebrew"]["17 narrative units"].get("event", 0),
             d["hebrew"]["17 narrative units"].get("time", 0), f(d["H"])],
            ["Book of Mormon frame (B)", d["bom_frame"].get("event", 0), d["bom_frame"].get("time", 0), f(d["B"])]]
    rows += [[k, v.get("event", 0), v.get("time", 0), f(v.get("event", 0) / max(1, v.get("event", 0) + v.get("time", 0)))]
             for k, v in d["controls"].items()]
    out = table(["text (registered rules)", "event", "time", "event share"], rows)
    v = d["verdict"]
    out += "\n" + table(["rule", "result"], [[k, v[k] if not isinstance(v[k], dict) else
                                               "; ".join(f"{a}: {b}" for a, b in v[k].items())]
                                              for k in v if k != "overall"])
    return out + f"\n**Registered verdict: {v['overall']}**\n"


def res_prereg30(data, reg):
    d = D(data, "prereg-jst-then")
    rows = []
    for b, r in d["books"].items():
        rows.append([b, f"{r['jst_words']:,}", f"{r['kjv_words']:,}", f(r["match_ratio"]), r["kjv_formulas"],
                     r["removed"]])
    out = table(["book", "JST words", "KJV words", "token match", "KJV formulas", "removed by Smith"], rows)
    rows = []
    for p, blk in d["panels"].items():
        for k in ("added", "retained"):
            x = blk[k]
            rows.append([p, k, x["n"], share([x["event"], x["n"], *x["share"]])])
    out += "\n" + table(["panel", "formulas", "n", "event-first share (registered rule)"], rows)
    C = d["amendment2_boundary_corrected"]["primary (OT narrative)"]["added"]
    out += (f"\n**Registered verdict: {d['verdict']}.** Without the five boundary spill-overs (Amendment 2): "
            f"{share([C['event'], C['n'], *C['share']])}; verdict {d['amendment2_verdict'][:2]}. Headnote-limit "
            "robustness: " + "; ".join(f"{k} lines → {v['added']} added, S = {v['S']:.3f} ({v['verdict']})"
                                        for k, v in d["robustness_headnote_lines"].items()) + ".\n")
    return out


FRAGMENTS = {
    "headlines": headlines, "questions": questions, "sources": sources,
    "quotation-spans": quotation_spans, "parallels": parallels, "hebrew-units": hebrew_units,
    "calibration": calibration,
    "res-published-claims": res_published_claims, "res-hebrew-forms": res_hebrew_forms,
    "res-kjv-rendering": res_kjv_rendering, "res-english-rule-audit": res_english_rule_audit,
    "res-bom-buckets": res_bom_buckets, "res-genre-ladder": res_genre_ladder, "res-per-verb": res_per_verb,
    "res-greek-egeneto": res_greek, "res-event-shares": res_event_shares, "res-egyptian": res_egyptian,
    "res-exclusions": res_exclusions, "res-prereg-event-share": res_prereg2, "res-prereg-jst-then": res_prereg30,
}


def _calibration_range(data) -> str:
    k = D(data, "kjv-rendering")["rule_agreement_on_settings"]["revised"]
    a = D(data, "english-rule-audit")["revised"]
    g = D(data, "greek-egeneto")["calibration"]["setting"]
    shares = [k["past"][0] / k["past"][1], k["future"][0] / k["future"][1], a["share"][0],
              g.get("rule_agrees", 0) / max(1, g.get("rendered", 0))]
    return f"{pct(min(shares))}–{pct(max(shares))}"


def values(data) -> dict[str, str]:
    """Single numbers the template's prose quotes."""
    bb, gl = D(data, "bom-buckets"), D(data, "genre-ladder")
    fr, fr30 = bb["current|revised"]["narrative frame"], bb["1830|revised"]["narrative frame"]
    rate = lambda x: 1000 * (x["counts"].get("past_time", 0) + x["counts"].get("past_event", 0)) / x["words"]  # noqa: E731
    matched = gl["ladder"][-1]
    es = D(data, "event-shares")["texts"]
    eg = D(data, "egyptian")
    pv = D(data, "per-verb")
    v = {
        "frame-words": f"{fr['words']:,}", "frame-rate": f(rate(fr)), "frame-rate-1830": f(rate(fr30)),
        "frame-setting": fr["counts"]["past_time"], "frame-event": fr["counts"]["past_event"],
        "event-share": share(bb["event_share"]["current"]),
        "ratio-matched": f"{matched['ratio_hebrew']:.1f}× {ci(*matched['ratio_hebrew_ci'], 1)}",
        "ratio-matched-1830": f"{matched['ratio_hebrew_1830']:.1f}× {ci(*matched['ratio_hebrew_1830_ci'], 1)}",
        "ratio-whole": f"{gl['ladder'][0]['ratio_hebrew']:.1f}×",
        "setting-ratio": (lambda x: f"{x['bom'][1] / x['hebrew'][1]:.2f}× {ci(*x['ratio_ci'])}")(gl["buckets"]["past_time"]),
        "hebrew-setting-rate": f(gl["buckets"]["past_time"]["hebrew"][1]),
        "ratio-per-verb": f"{pv['ratio']['current']:.2f}× {ci(*pv['ratio']['current_ci'], 1)}",
        "kjv-ot-share": share(es["KJV Old Testament | revised"]["share"]),
        "kjv-nt-share": share(es["KJV New Testament | revised"]["share"]),
        "late-war-share": share(es["The Late War (1819) | revised"]["share"]),
        "snowden-share": share(es["Snowden, American Revolution (1793) | revised"]["share"]),
        "napoleon-share": share(es["First Book of Napoleon (1809) | revised"]["share"]),
        "nullification-share": share(es["Book of Nullification (1830) | revised"]["share"]),
        "jst-kept-share": share(D(data, "event-shares")["jst_revised"]["panels"]["primary (OT narrative)"]["retained"]["share"]),
        "moses": (lambda m: f"{m['event']}/{m['event'] + m['time']} at {f(m['per_1k'])} per 1,000")(es["Moses (all) | revised"]),
        "abraham": (lambda m: f"{m['event']}/{m['event'] + m['time']} at {f(m['per_1k'])} per 1,000")(es["Abraham | revised"]),
        "abraham-p": f"{D(data, 'event-shares')['abraham_vs_moses_fisher_p']:.2f}",
        "matched-range": f"{f(eg['matched_range'][0], 0)}–{f(eg['matched_range'][1], 0)}",
        "piye": f(eg["named"]["texts"]["Piye Victory Stela"]["per1k_translated"]),
        "additive-demotic": (lambda r: f"{min(r):.1f}–{max(r):.1f}")(
            [x["total"][0] for k, x in eg["additive_model"]["rows"].items() if "demotic" in k]),
        "wehayah": D(data, "hebrew-forms")["by_morph"]["HC/Vqq3ms"],
        "pooled": f"{D(data, 'hebrew-forms')['counting_rules']['wayhi + wehayah (morphology)']:,}",
        "reverse-absent": bb["e1830"]["reverse"]["absent from 1830"],
        "prereg2-verdict": D(data, "prereg-event-share")["verdict"]["overall"],
        "prereg30-verdict": D(data, "prereg-jst-then")["verdict"],
        "n-analyses": len(data),
        "calibration-range": _calibration_range(data),
    }
    return {k: str(x) for k, x in v.items()}
