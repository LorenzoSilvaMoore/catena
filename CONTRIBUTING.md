# Contributing to catena

Thank you for your interest in contributing.  This document covers everything
you need to know to get started.

---

## How to contribute

You have two options:

1. **Open an issue or discussion first** — useful for new features, design
   questions, or anything that may need agreement before code is written.
2. **Fork and open a pull request** — fine for clear bug fixes or small
   improvements where the intent is unambiguous.

There is no rigid rule; use your judgement.  For anything non-trivial, opening
a discussion first tends to save everyone time.

You are also welcome to reach out directly to the maintainer at
[lorenzo.smb.rayo@gmail.com](mailto:lorenzo.smb.rayo@gmail.com) or
[lorenzosilvamoore@ciencias.unam.mx](mailto:lorenzosilvamoore@ciencias.unam.mx).

---

## Setting up the development environment

The project has **no third-party runtime dependencies**.  `requirements.txt`
exists only to pin the development tooling (pytest, etc.).

```bash
git clone https://github.com/<your-fork>/catena.git
cd catena
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e .
pip install -r requirements.txt
```

There are no environment variables or `.env` files to configure.

---

## Running the tests

```bash
pytest testing/
```

All tests must pass before a pull request can be merged.  If your change
intentionally breaks an existing test, document clearly why the old behaviour
was wrong and what the new contract is.  This should be the exception, not the
norm.

Some tests depend on very large pre-computed integers (million-digit values,
large powers, etc.) that are stored in a compact binary cache under
`testing/store/` to avoid recomputing them on every run.  The store is
rebuilt automatically when its contents change.  The `*.dat` and `*.hash`
files it produces are **not git-tracked** — they are generated locally on
first run and should not be committed.  See
[testing/README.md](testing/README.md) for a full explanation and instructions
on adding new pre-computed values.

---

## Testing philosophy

Tests are **a promise to the future**, not a development methodology.  The
suite cements the current observable behaviour of every public API so that
future changes cannot accidentally regress it.

Concretely:

- **New behaviour must come with new tests.**  A feature without tests is not
  finished.
- **Tests should be written after the implementation is understood**, not to
  drive the design.  TDD is not the workflow here.
- **Every expected value must be independently verifiable** — derive it by
  hand, from a reference, or from a separate computation.  Do not copy-paste
  values out of the code under test.
- **Test names should describe the contract**, not the implementation.  Prefer
  `test_convergent_0_returns_first_partial_quotient` over
  `test_convergent_branch_n_equals_0`.

---

## What is and isn't tracked by git

The `.gitignore` excludes the following; do not force-add them:

| Pattern | Reason |
|---------|--------|
| `.venv/` | Local virtual environment |
| `__pycache__/` | Python bytecode |
| `dist/` | Build artefacts |
| `testing/store/*.dat`, `testing/store/*.hash` | Locally generated large-integer cache |
| `docs/theory/` | LaTeX source for the theory document (not yet versioned; tracked from v1.0.0 of the document) |
| `*.aux`, `*.pdf`, `*.log`, etc. | LaTeX build outputs |
| `gitdiff.txt` | Scratch diff files |

---

## Code conventions

- **Python ≥ 3.12** with standard-library-only dependencies.
- **Type hints** on all public function signatures.
- **Docstrings** follow the existing NumPy/Sphinx style used throughout the
  codebase.
- **No global state.**  Side-effectful code belongs in `run.py`, not in the
  package.
- `run.py` is tracked in the repository but excluded from the package build.
  It is the designated place for exploratory examples and use-cases that print
  to the screen.  The README may also contain curated examples.

---

## Documentation

- **API documentation** lives in the docstrings.  Keep them accurate when you
  change behaviour.
- **Theoretical justification** (proofs, derivations, mathematical background)
  lives in `docs/theory/main.tex`.  This document is not yet git-tracked and
  will remain so until version 1.0.0 of the document.
- The **README** is the public-facing overview.  Update it if a public API
  changes or a new class is added.

---

## Versioning and changelog

The project uses **Semantic Versioning 2.0.0** (`MAJOR.MINOR.PATCH`).

- `PATCH` — backwards-compatible bug fixes.
- `MINOR` — backwards-compatible new functionality.
- `MAJOR` — breaking changes.

`CHANGELOG.md` must be updated with every release, at minimum for every
`PATCH` increment.  Add your entry under an `[Unreleased]` heading while work
is in progress; it will be dated and tagged at release time.

---

## Releases

Releases to PyPI are done **by hand** — there is no automated publish pipeline.
Do not bump the version or add a changelog entry as part of a feature PR; that
is done by the maintainer at release time.
