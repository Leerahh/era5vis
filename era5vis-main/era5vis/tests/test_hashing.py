from era5vis.utils.hashing import request_hash

def test_request_hash_is_deterministic():
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

    assert request_hash(req1) == request_hash(req2)
