import json
import hashlib

def request_hash(request: dict) -> str:
    payload = json.dumps(request, sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()[:12]