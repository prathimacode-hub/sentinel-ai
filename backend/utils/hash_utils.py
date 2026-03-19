import hashlib
import json
from config import settings


def generate_hash(data):
    """
    Generate SHA256 hash for given data
    """

    # Convert dict to sorted string for consistency
    if isinstance(data, dict):
        data_string = json.dumps(data, sort_keys=True)
    else:
        data_string = str(data)

    hash_object = hashlib.new(settings.HASH_ALGORITHM)
    hash_object.update(data_string.encode("utf-8"))

    return hash_object.hexdigest()


# -----------------------------
# OPTIONAL: CHAINED HASHING (BLOCKCHAIN STYLE)
# -----------------------------

def generate_chain_hash(current_data, previous_hash=""):
    """
    Create chained hash for tamper-proof logs
    """
    import json

    combined = json.dumps({
        "prev": previous_hash,
        "data": current_data
    }, sort_keys=True)

    return generate_hash(combined)


# -----------------------------
# VERIFY HASH INTEGRITY
# -----------------------------
def verify_hash(data, given_hash):
    """
    Verify if data matches hash
    """

    calculated_hash = generate_hash(data)
    return calculated_hash == given_hash
