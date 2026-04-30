# Testing

Tests are run with [pytest](https://docs.pytest.org/) from the repository root:

```bash
pytest testing/
```

## Large-integer store

Some tests require very large integers (e.g. `101**5001`, million-digit randoms) that are slow to compute from scratch on every run.  
`bigints.py` and `conftest.py` together handle this via a compact binary store under `testing/store/`.

### How it works

| Component | Role |
|-----------|------|
| `bigints.py` | Generates, saves, and loads large integers; also provides on-the-fly generation helpers. |
| `conftest.py` | `big_int_store` session fixture — rebuilds the store automatically when `_PRECOMPUTED` changes, then exposes the loaded dict to tests. |
| `testing/store/*.dat` | Binary files (`int.to_bytes` layout) — fast to load, much faster than re-parsing decimal strings. |
| `testing/store/bigints.hash` | SHA-256 fingerprint of the store files; used to skip rebuilds when nothing has changed. |

### Adding pre-computed integers

Edit the `_PRECOMPUTED` dict in `conftest.py`:

```python
_PRECOMPUTED: dict[str, dict] = {
    None: {                              # → store/bigints.dat
        "my_value": {"expr": lambda: 10**10000},
    },
    "my_store": {                        # → store/my_store.dat
        "another": {"expr": lambda: 2**65537 - 1},
    },
}
```

`None` maps to the default `bigints.dat` file; any other string becomes the filename (`.dat` extension added automatically).  
The store is regenerated once the next time `pytest` runs and the hash no longer matches.

### On-the-fly generation (no store)

```python
from testing.bigints import make_int, make_neg_int, make_ints

a = make_int(bits=33000, seed=0)        # exact bit-length
b = make_int(digits=10000, seed=1)      # ~10 000 decimal digits
c = make_neg_int(digits=5000, seed=2)
many = make_ints(8, digits=10000)       # list of 8 values, seeds 0–7
```

Same seed → same integer, always.

### Using the store in a test

```python
def test_something(big_int_store):
    n = big_int_store["big_101"]   # 101**5001, loaded from disk
    ...
```

The `big_int_store` fixture is `autouse=True` so the store is always populated before any test body runs, even without declaring the fixture parameter.
