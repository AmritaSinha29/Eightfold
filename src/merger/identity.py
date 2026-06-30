"""Identity matching — groups RawRecords that belong to the same candidate.

Matching priority:
  1. Exact email overlap (case-insensitive)
  2. Exact E.164 phone overlap
  3. Fuzzy name similarity >= threshold AND same country
"""
from __future__ import annotations

from rapidfuzz import fuzz

from src.models.raw_record import RawRecord

NAME_SIMILARITY_THRESHOLD: int = 88


class _UnionFind:
    def __init__(self, n: int) -> None:
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: int, y: int) -> None:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1


def group_records(records: list[RawRecord]) -> list[list[RawRecord]]:
    """Partition RawRecords into per-candidate groups using union-find."""
    n = len(records)
    if n == 0:
        return []

    uf = _UnionFind(n)
    for i in range(n):
        for j in range(i + 1, n):
            r_i, r_j = records[i], records[j]
            if _emails_overlap(r_i, r_j):
                uf.union(i, j)
            elif _phones_overlap(r_i, r_j):
                uf.union(i, j)
            elif _names_similar(r_i, r_j) and _same_country(r_i, r_j):
                uf.union(i, j)

    groups: dict[int, list[RawRecord]] = {}
    for i, rec in enumerate(records):
        root = uf.find(i)
        groups.setdefault(root, []).append(rec)

    return list(groups.values())


def _emails_overlap(a: RawRecord, b: RawRecord) -> bool:
    return bool(
        {e.lower() for e in a.emails} & {e.lower() for e in b.emails}
    )


def _phones_overlap(a: RawRecord, b: RawRecord) -> bool:
    return bool(set(a.phones) & set(b.phones))


def _names_similar(a: RawRecord, b: RawRecord) -> bool:
    if not a.full_name or not b.full_name:
        return False
    return fuzz.token_set_ratio(a.full_name, b.full_name) >= NAME_SIMILARITY_THRESHOLD


def _same_country(a: RawRecord, b: RawRecord) -> bool:
    return bool(
        a.location_country
        and b.location_country
        and a.location_country == b.location_country
    )
