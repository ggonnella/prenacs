import pytest
import pyplugins

from contextlib import contextmanager

@contextmanager
def assert_nothing_raised():
  try: yield
  except Exception as e: pytest.fail(f"Unexpected exception raised: {e}")

def test_bash_fas_plugin(testdata, examples):
  plugin = pyplugins.importer(examples("fas_stats_sh.sh"))
  assert plugin.compute(testdata("example.fas")) == \
           (['800', '.41000000000000000000'], [''])

def test_rs_fas_plugin(testdata, examples):
  plugin = pyplugins.importer(examples("fas_stats_rs.rs"))
  assert plugin.compute(testdata("example.fas")) == \
           ((800, 0.41), [])

def test_py_fas_plugin(testdata, examples):
  plugin = pyplugins.importer(examples("fas_stats_py.py"))
  assert plugin.compute(testdata("example.fas")) == \
           ([800, 0.41], [])

def test_nim_fas_plugin(testdata, examples):
  plugin = pyplugins.importer(examples("fas_stats_nim.nim"))
  assert plugin.compute(testdata("example.fas")) == \
           (["800", "0.41"], [])

