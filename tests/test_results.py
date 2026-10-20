"""Published numbers, pinned. If an intended change moves one of these, update
the test in the same commit and add the old figure to the report's corrections."""
import pytest

from conftest import result


def test_hebrew_forms():
    d = result("hebrew-forms")
    assert d["counting_rules"]["wayhi only (morphology)"] == 784
    assert d["by_morph"]["HC/Vqq3ms"] == 357
    assert d["counting_rules"]["unpointed ויהי + unpointed והיה"] == 1224
    assert d["buckets"]["past"] == {"time": 421, "verb": 363}


def test_published_claims():
    m = result("published-claims")["measured"]
    assert (m["kjv_ot_came_to_pass"], m["kjv_nt_came_to_pass"], m["bom_it_came_to_pass"]) == (391, 66, 1353)


def test_bom_frame_counts():
    d = result("bom-buckets")
    c = d["current|revised"]["narrative frame"]["counts"]
    assert (c["past_time"], c["past_event"]) == (335, 775)
    assert d["removed_by_bucket"] == {"past_event": 30, "past_time": 12}


def test_genre_ladder_matched_ratio():
    x = result("genre-ladder")["ladder"][-1]
    assert x["ratio_hebrew"] == pytest.approx(2.66, abs=0.02)
    assert x["ratio_hebrew_ci"][0] > 2.2


def test_kjv_rendering():
    d = result("kjv-rendering")
    assert d["rendering"]["past|time"]["rendered"] == 334 and d["rendering"]["past|time"]["verses"] == 396
    assert d["rule_agreement_on_settings"]["revised"]["past"] == [331, 334]


def test_rule_audit():
    d = result("english-rule-audit")
    assert d["revised"]["agree"] == 119 and d["revised"]["disagreements"] == ["Alma 49:28"]


def test_greek():
    d = result("greek-egeneto")
    assert d["totals"] == {"setting": 56, "event": 8, "sub": 3, "verb": 135}
    assert d["calibration"]["setting"]["rule_agrees"] == 52


def test_egyptian():
    d = result("egyptian")
    assert d["named"]["texts"]["Piye Victory Stela"]["per1k_translated"] == pytest.approx(8.26, abs=0.005)
    p = d["rylands"]["unquoted (narrative frame)"]
    assert (p["openings"], p["words"], p["time_first"]) == (12, 5602, 1)
    assert [round(x) for x in d["matched_range"]] == [0, 22]


def test_event_shares():
    t = result("event-shares")["texts"]
    assert (t["KJV Old Testament | revised"]["event"], t["KJV Old Testament | revised"]["time"]) == (14, 374)
    assert t["The Late War (1819) | revised"]["event"] == 22
    assert t["Snowden, American Revolution (1793) | revised"]["event"] == 49


def test_registered_verdicts():
    assert result("prereg-event-share")["verdict"]["overall"].startswith("MISS")
    j = result("prereg-jst-then")
    assert j["verdict"].startswith("R1")
    a = j["panels"]["primary (OT narrative)"]["added"]
    assert (a["n"], a["event"]) == (52, 39)
    c = j["amendment2_boundary_corrected"]["primary (OT narrative)"]["added"]
    assert (c["n"], c["event"]) == (47, 38)


def test_exclusions_flag_known_frame_parallels():
    refs = {x["bom"] for x in result("exclusions")["in_frame"]}
    assert "Mormon 9:22–9:24" in refs


def test_record_comparison():
    """The Requiem bridge's change line: equal at recorded precision is no change;
    only a move outside a recorded interval is called substantive."""
    from bomstylo.analysis import Headline
    from bomstylo.requiem_bridge import _fmt, _parse, compare
    new = [Headline("rate", 7.763112, 7.2, 8.3), Headline("n", 42)]
    old = _parse("Recorded values: " + "; ".join(_fmt(h) for h in new))
    assert compare(old, new).endswith("none (same values, new inputs).")
    assert "OUTSIDE" in compare(old, [Headline("rate", 9.0, 8.5, 9.5), Headline("n", 42)])
    moved = compare(old, [Headline("rate", 7.5, 7.0, 8.0), Headline("n", 43)])
    assert "OUTSIDE" not in moved and "rate" in moved and "n 42→43" in moved
