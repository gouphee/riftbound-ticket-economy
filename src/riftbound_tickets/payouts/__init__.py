"""Versioned historical published payouts, independent of collection code."""

from .rules import saturday_placement, saturday_top8_split, win_record_payout

__all__ = ["saturday_placement", "saturday_top8_split", "win_record_payout"]
