"""Require one explicit resource coverage entry for each canonical page."""

def validate_coverage(coverage, canonical):
    assert set(coverage) == set(canonical), 'Every canonical page needs explicit coverage'
