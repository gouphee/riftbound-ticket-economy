"""Pure ticket functions. None means unknown, never zero-filled missing evidence.

These functions calculate published entitlements, not confirmed physical claims.
Draws are not promoted to wins. Recorded wins include any officially awarded bye
wins; no second payout is added for a bye.
"""

from __future__ import annotations

SATURDAY_TIERS = ((1, 1, 432), (2, 2, 288), (3, 4, 216), (5, 8, 144),
                  (9, 16, 72), (17, 32, 48), (33, 64, 24), (65, 128, 18))


def _integer(value, name: str, minimum: int = 0):
    if value is not None and (type(value) is not int or value < minimum):
        raise ValueError(f"{name} must be an integer >= {minimum} or None")


def win_record_payout(wins: int | None, losses: int | None, draws: int | None,
                      *, rounds: int, table: dict[int, int]) -> int | None:
    """Apply one event's published win table; unlisted valid wins pay zero.

    Unknown record components and records beyond the published round limit
    cannot be evaluated. Early drops retain their recorded results; eligibility
    is a separate determination and is not inferred by this function.
    """
    _integer(rounds, "rounds", 1)
    for name, value in (("wins", wins), ("losses", losses), ("draws", draws)):
        _integer(value, name)
    for win, award in table.items():
        _integer(win, "table wins")
        _integer(award, "table tickets")
        if win > rounds:
            raise ValueError("Published win table exceeds round limit")
    if None in (wins, losses, draws):
        return None
    if wins + losses + draws > rounds:
        return None
    return table.get(wins, 0)


def saturday_placement(final_placement: int | None) -> int | None:
    """Use final placement, never an unresolved Swiss seed for the Top 8."""
    _integer(final_placement, "final_placement", 1)
    if final_placement is None:
        return None
    return next((award for lo, hi, award in SATURDAY_TIERS if lo <= final_placement <= hi), 0)


def saturday_top8_split(placement_or_seed: int | None) -> int | None:
    """Explicit equal-split scenario: the 1,728-ticket Top 8 pool / 8 = 216.

    This is a redistribution, never an additional payout. Event-specific proof
    of an agreement is required to call this an observed event payout.
    """
    _integer(placement_or_seed, "placement_or_seed", 1)
    if placement_or_seed is None:
        return None
    return 216 if placement_or_seed <= 8 else saturday_placement(placement_or_seed)
