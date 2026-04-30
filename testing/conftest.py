"""Pytest configuration for the catena test suite.

The ``big_int_store`` fixture is session-scoped and runs automatically before
any test.  It guarantees the binary store (bigints.dat) is populated with the
expensive pre-computed values before tests that need them execute.

Tests can depend on the fixture explicitly to receive the dict:

    def test_something(big_int_store):
        n = big_int_store["big_101"]
        ...

Or they can just call ``load()`` directly, knowing the store is already on
disk by the time any test body runs.
"""

import pytest
import pickle
import hashlib
from pathlib import Path


from testing.bigints import _STORE_DIR, load, make_int, make_neg_int, build_store_path, save

from typing import Callable, Any


# Integers that are expensive to compute and worth caching.
# Add entries here as needed; update_or_save only rewrites keys that are
# missing or changed, so re-runs are cheap once the file exists.
_HASH_FILE = build_store_path().with_suffix(".hash")
_PRECOMPUTED: dict[str, dict[str, Callable[[], int]]] = {
    None: { # default store file (bigints.dat)
        "big_101": {"expr": lambda: 101**5001},
        "mersenne_127": {"expr": lambda: 2**127 - 1},
    },

    "random_strings": {
        "random_33000b": {"expr": lambda: make_int(bits=33000, seed=1)},
        "random_10000d": {"expr": lambda: make_int(digits=10000, seed=2)},
    },

    "random_math_metric_product_digit_count": {
        f"random_1000000_digits{i}": {"expr": lambda: make_int(digits=1000000, seed=i)} for i in range(1, 4)
    },
}


@pytest.fixture(scope="session", autouse=True)
def big_int_store() -> dict[str, int]:
    """Populate the binary store once per session and return the full dict.

    ``autouse=True`` guarantees this runs before every test, even those that
    do not request it.  Tests that need the integers can declare
    ``big_int_store`` as a parameter and receive the loaded dict directly.
    """
    if _store_needs_update():
        _main()  # generates the store file and saves the new hash
    return load(build_store_path())


def _hash_salted_object(obj: Any, salt: str) -> str:
    """
    Hashes a picklable object in memory with a given salt using SHA-256.

    :param obj: Any picklable Python object.
    :param salt: A string used to salt the hash.
    :return: SHA-256 hash of the salted object's bytes.
    :raises TypeError: If the object is not picklable or the salt is invalid.
    :raises ValueError: If the salt is None or cannot be encoded in UTF-8.
    """
    if salt is None:
        raise ValueError("Salt cannot be None.")
    
    try:
        salt_bytes = salt.encode("utf-8")
    except (AttributeError, UnicodeEncodeError) as e:
        raise ValueError(f"Salt must be a UTF-8 encodable string. Error: {e}")

    try:
        obj_bytes = pickle.dumps(obj)
    except pickle.PicklingError:
        raise TypeError(f"Object of type {type(obj).__name__} is not picklable: {obj}")

    salted_bytes = salt_bytes + obj_bytes
    return hashlib.sha256(salted_bytes).hexdigest()


def _file_hash(filepath: str) -> str:
    """
    Computes the SHA-256 hash of a file.
    
    :param filepath: The path to the file.
    :return: The SHA-256 hash of the file as a hexadecimal string.
    """
    if not Path(filepath).exists():
        return ''
    
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(4096): 
            hasher.update(chunk)
    return hasher.hexdigest()


def _store_hash() -> str:
    """
    Computes a combined hash of all precomputed store files, including the structure of _PRECOMPUTED 
    and the contents of each file.

    This function iterates over all precomputed store files, computes their individual hashes,
    and combines them into a single hash value. This allows us to detect changes in any of the
    store files by comparing the combined hash against a known good hash.

    :return: A combined hash string representing the current state of all precomputed store files.
    """
    combined_hash = _precomputed_signature()  # Start with a hash of the _PRECOMPUTED structure itself
    for file_name in _PRECOMPUTED.keys():
        path = build_store_path(file_name)
        combined_hash = _hash_salted_object(combined_hash, _file_hash(path))
    
    return combined_hash


def _store_needs_update() -> bool:
    """
    Determines if the store file needs to be updated based on the current integers.

    :param path: The path to the store file.
    :param integers: A dictionary of integer configurations to compare against the store.
    :return: True if the store needs to be updated, False otherwise.
    """
    last_known_good_hash = _HASH_FILE.read_text().strip() if _HASH_FILE.exists() else ''

    return _store_hash() != last_known_good_hash


def _generate_and_save_store():
    """Generate the store file with the precomputed integers and save it."""
    for file_name, integers in _PRECOMPUTED.items():
        path = build_store_path(file_name)
        save({k: cfg["expr"]() for k, cfg in integers.items()}, path)


def _clear_store_directory():
    """Utility function to clear all store files. Use with caution."""
    for file in _STORE_DIR.glob("*.dat"):
        file.unlink()
    if _HASH_FILE.exists():
        _HASH_FILE.unlink()


def _precomputed_signature() -> str:
    """Compute a stable hash of _PRECOMPUTED's structure and lambda bytecodes.

    Lambdas are not picklable, so _hash_salted_object cannot be used on
    _PRECOMPUTED directly.  Instead, hash the dict's key structure together
    with each lambda's compiled code object (bytecode + constants), which are
    both deterministic and stable across interpreter restarts.
    """
    hasher = hashlib.sha256()
    for file_name, entries in _PRECOMPUTED.items():
        hasher.update(str(file_name).encode())
        for key, cfg in entries.items():
            hasher.update(key.encode())
            code = cfg["expr"].__code__
            hasher.update(bytes(code.co_code))
            hasher.update(pickle.dumps(code.co_consts))
    return hasher.hexdigest()


def _main():
    """Main function to generate the store files and save the hash."""

    _clear_store_directory()  

    _generate_and_save_store()

    # After rebuilding the store, compute and save the new hash
    new_hash = _store_hash()

    _HASH_FILE.write_text(new_hash)


if __name__ == "__main__":
    _main()
