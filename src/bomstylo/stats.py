"""Exact intervals used throughout. All are 95%, two-sided."""
from __future__ import annotations

from scipy.stats import beta, chi2


def rate(k: float, n: float, per: float = 1000.0) -> float:
    """k per `per` units of n (per 1,000 words by default)."""
    return per * k / n if n else 0.0


def poisson_ci(k: int) -> tuple[float, float]:
    """Exact (Garwood) interval for a Poisson count."""
    lo = chi2.ppf(0.025, 2 * k) / 2 if k else 0.0
    return lo, chi2.ppf(0.975, 2 * k + 2) / 2


def rate_ci(k: int, n: float, per: float = 1000.0) -> list[float]:
    """[rate, low, high] per `per` units, from the exact Poisson interval."""
    lo, hi = poisson_ci(k)
    return [per * k / n, per * lo / n, per * hi / n]


def ratio_ci(k1: int, e1: float, k2: int, e2: float) -> tuple[float, float] | None:
    """Exact interval for (k1/e1) / (k2/e2), conditional on k1 + k2.

    Given the total, k1 is binomial with p = r1 e1 / (r1 e1 + r2 e2); the
    Clopper–Pearson interval for p converts to one for the rate ratio."""
    if not k2:
        return None
    lo = beta.ppf(0.025, k1, k2 + 1) if k1 else 0.0
    hi = beta.ppf(0.975, k1 + 1, k2)
    f = e2 / e1
    return lo / (1 - lo) * f, hi / (1 - hi) * f


def share_ci(k: int, n: int) -> list[float | None]:
    """[k/n, low, high], Clopper–Pearson."""
    if not n:
        return [None, None, None]
    lo = beta.ppf(0.025, k, n - k + 1) if k else 0.0
    hi = beta.ppf(0.975, k + 1, n - k) if k < n else 1.0
    return [k / n, lo, hi]
