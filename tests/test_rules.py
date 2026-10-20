"""The bucket rules on hand-picked sentences, and the statistics helpers."""
import pytest

from bomstylo import english, stats


@pytest.mark.parametrize("text,rule,bucket", [
    ("And it came to pass that they did march forth", "registered", "past_event"),
    ("And it came to pass, when they had eaten, that", "registered", "past_time"),
    ("and it came to pass the same day, that the lord", "registered", "past_event"),   # registered miss
    ("and it came to pass the same day, that the lord", "revised", "past_time"),
    ("and when the feast was ended, it came to pass, the fragments", "revised", "past_time"),
    ("and when the feast was ended, it came to pass, the fragments", "registered", "past_event"),
    ("and it came to pass on the day that", "revised", "past_time"),                 # the "the day" fix
    ("and it shall come to pass, whosoever doeth this", "revised", "future_time"),
    ("and it came to pass on a certain day, that", "revised", "past_time"),
])
def test_english_rule(text, rule, bucket):
    c = english.counts(text, rule)
    assert dict(c) == {bucket: 1}


def test_registered_counter_is_after_text_only():
    assert english.registered_counts("And when they came, it came to pass that he") == {"event": 1}


def test_revised_pattern_keeps_the_day():
    assert english.EN_TIME_REV.match("the day")


def test_intervals():
    assert stats.poisson_ci(0) == (0.0, pytest.approx(3.6889, abs=1e-4))
    p, lo, hi = stats.share_ci(14, 388)
    assert (round(lo, 4), round(hi, 4)) == (0.0199, 0.0598)
    lo, hi = stats.ratio_ci(1110, 143216, 249, 85348.0857)
    assert lo < 1110 / 143216 / (249 / 85348.0857) < hi
