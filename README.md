# Piskvorky

Tests and tournament for a student assignment.

Note that names/comments/messages are in Czech.


## Test Installation & Usage

In a Python virtual environment, install:

    python -m pip install pytest pytest-level

Then, run:

    python -m pytest -v test_piskvorky.py --level 0

That will run 0 tests.
Increase the level to get more tests.


## Tournament Installation & Usage

Put strategies in `strategie/name.py` (replacing `name` with the attendee
name).

In a Python virtual environment, install:

    python -m pip install -r requirements.txt

Then, run:

    python turnaj.py --help

See the output for available options.
