"""
utils/hashing.py
----------------
Generates a deterministic SHA-256 content hash over one or more image
byte payloads.  Used as the cache key for scan results so identical
images are never re-processed by the AI.
"""

import hashlib
from typing import Sequence


def compute_content_hash(*image_bytes_list: bytes) -> str:
    """
    Return a hex SHA-256 digest computed over all supplied byte strings
    concatenated in order.  For a scan this is always:
        compute_content_hash(front_image_bytes, back_image_bytes)

    The hash is stable: same bytes → same hash, always.
    """
    h = hashlib.sha256()
    for data in image_bytes_list:
        h.update(data)
    return h.hexdigest()
