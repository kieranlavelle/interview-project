"""Module used to hold utility functions for the application."""

from typing import Iterator
from datetime import date


def list_pairs(sequence: list) -> Iterator[tuple[date, date]]:
    """Create a list of pairs from a sequence.

    This function is used to split a flat list of dates
    into an iterable of pairs of dates. The pairs are
    representative of the start and end dates of a
    period of time.

    Args:
        sequence: A list of dates.

    Yields:
        A zip object of pairs of dates.
    """
    if not sequence:
        return []
    it = iter(sequence)
    return zip(it, it)
