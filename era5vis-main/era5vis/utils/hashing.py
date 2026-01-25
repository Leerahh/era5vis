"""
Create a hash from a Request.

Author: Leah Herrfurth
"""

import json
import hashlib

def request_hash(request: dict) -> str:
    """
    The hash is independent of the ordering of dictionary keys, making it
    suitable for caching and file naming.

    Parameters
    ----------
    request : dict
        The request dictionary containing ERA5 parameters or similar data.

    Returns
    -------
    str
        A 12-character hexadecimal string representing the hash of the request.

    Examples
    --------
    >>> request = {"variable": ["t"], "pressure_level": ["850"], "year": ["2022"]}
    >>> request_hash(request)
    'a1b2c3d4e5f6'
    """
    
    payload = json.dumps(request, sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()[:12]
