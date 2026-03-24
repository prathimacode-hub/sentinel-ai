# backend/utils/hash_utils.py

"""
Hash Utilities for SentinelAI Backend
-------------------------------------

This module provides functions for:
- Generating SHA256 (or other) hashes for any data
- Creating chained hashes for tamper-proof logs
- Verifying hash integrity

No external dependencies are required beyond standard Python libraries.

Author: SentinelAI Team
"""

import hashlib
import json
from datetime import datetime

# -----------------------------
# DEFAULT HASH ALGORITHM
# -----------------------------
HASH_ALGORITHM = "sha256"  # Change to "sha512" if needed

# -----------------------------
# GENERATE HASH
# -----------------------------
def generate_hash(data, algorithm=HASH_ALGORITHM):
    """
    Generate a hash for the given data.

    Args:
        data (dict, str, int, etc.): Data to hash
        algorithm (str): Hash algorithm (default sha256)

    Returns:
        str: Hexadecimal hash string
    """
    # Convert dict to sorted string for consistency
    if isinstance(data, dict):
        data_string = json.dumps(data, sort_keys=True)
    else:
        data_string = str(data)

    hash_obj = hashlib.new(algorithm)
    hash_obj.update(data_string.encode("utf-8"))
    return hash_obj.hexdigest()

# -----------------------------
# CHAINED HASHING (BLOCKCHAIN STYLE)
# -----------------------------
def generate_chain_hash(current_data, previous_hash="", algorithm=HASH_ALGORITHM):
    """
    Generate a chained hash using previous hash and current data.

    Args:
        current_data (dict, str, int): Current event data
        previous_hash (str): Previous hash in the chain
        algorithm (str): Hash algorithm

    Returns:
        str: Chained hash
    """
    combined = json.dumps({
        "prev": previous_hash,
        "data": current_data
    }, sort_keys=True)
    return generate_hash(combined, algorithm)

# -----------------------------
# VERIFY HASH INTEGRITY
# -----------------------------
def verify_hash(data, given_hash, algorithm=HASH_ALGORITHM):
    """
    Verify if the hash of the data matches the given hash.

    Args:
        data (dict, str, int): Data to verify
        given_hash (str): Expected hash
        algorithm (str): Hash algorithm

    Returns:
        bool: True if matches, False otherwise
    """
    calculated_hash = generate_hash(data, algorithm)
    return calculated_hash == given_hash

# -----------------------------
# OPTIONAL TESTING
# -----------------------------
if __name__ == "__main__":
    sample_data = {"event": "test_event", "score": 42}

    # Generate simple hash
    h = generate_hash(sample_data)
    print(f"[Test] Hash: {h}")

    # Generate chained hash
    chain_h = generate_chain_hash(sample_data, previous_hash="prev_hash_123")
    print(f"[Test] Chained Hash: {chain_h}")

    # Verify hash
    verified = verify_hash(sample_data, h)
    print(f"[Test] Verify Hash: {verified}")
