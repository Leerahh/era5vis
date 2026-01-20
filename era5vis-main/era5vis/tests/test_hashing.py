"""
Tests for the request_hash function in era5vis.utils.hashing.
Author: Leah Herrfurth
"""

from era5vis.utils.hashing import request_hash

def test_request_hash_is_deterministic():
    """
    Verify that request_hash produces the same hash for dictionaries
    with the same content but different key orders.
    """

    # Two request dictionaries with identical content but different key order
    req1 = {
        "variable": ["t"],
        "pressure_level": ["850"],
        "year": ["2022"],
    }
    req2 = {
        "year": ["2022"],
        "pressure_level": ["850"],
        "variable": ["t"],
    }

    # The hashes must be identical
    assert request_hash(req1) == request_hash(req2)
