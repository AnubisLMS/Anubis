import hashlib


def sha256(s: str) -> str:
    """
    Get hex digest of hashed string
    """
    return hashlib.sha256(s.encode()).hexdigest()