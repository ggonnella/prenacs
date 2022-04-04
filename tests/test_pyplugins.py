import pytest
import pyplugins

def test_bash_fas_plugin(testdata, examples, fas_api_config):
  plugin = pyplugins.importer(examples("fas_stats_sh.sh"), fas_api_config)
  assert plugin.compute(testdata("example.fas")) == \
           (['800', '.41000000000000000000'], [''])

def test_rs_fas_plugin(testdata, examples, fas_api_config):
  plugin = pyplugins.importer(examples("fas_stats_rs.rs"), fas_api_config)
  assert plugin.compute(testdata("example.fas")) == \
           ((800, 0.41), [])

def test_py_fas_plugin(testdata, examples, fas_api_config):
  plugin = pyplugins.importer(examples("fas_stats_py.py"), fas_api_config)
  assert plugin.compute(testdata("example.fas")) == \
           ([800, 0.41], [])

def test_nim_fas_plugin(testdata, examples, fas_api_config):
  plugin = pyplugins.importer(examples("fas_stats_nim.nim"), fas_api_config)
  assert plugin.compute(testdata("example.fas")) == \
           (["800", "0.41"], [])

