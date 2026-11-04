"""Run every server test:  python -I Server/tests/run_all.py

Needs nothing but Python (tests that use the player database skip until
Server/gamedata/fifadb.rar is extracted). Exit code 0 = all passed.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.discover(HERE, pattern="test_*.py", top_level_dir=HERE)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
