#
# (c) 2022 Giorgio Gonnella, University of Goettingen, Germany
#
import pytest
import multiplug

def test_bash_fas_plugin(testdata, examples, fas_api_config):
  plugin = multiplug.bash(examples("fas_stats_sh.sh"), **fas_api_config)
  assert plugin.compute(testdata("example.fas")) == \
           ['800', '.41000000000000000000']

def test_rs_fas_plugin(testdata, examples, fas_api_config):
  plugin = multiplug.rust(examples("fas_stats_rs.rs"), **fas_api_config)
  assert plugin.compute(testdata("example.fas")) == \
           ((800, 0.41), [])

def test_py_fas_plugin(testdata, examples, fas_api_config):
  plugin = multiplug.py(examples("fas_stats_py.py"), **fas_api_config)
  assert plugin.compute(testdata("example.fas")) == \
           ([800, 0.41], [])

def test_nim_fas_plugin(testdata, examples, fas_api_config):
  plugin = multiplug.nim(examples("fas_stats_nim.nim"), **fas_api_config)
  assert plugin.compute(testdata("example.fas")) == \
           (["800", "0.41"], [])

def test_auto_bash_fas_plugin(testdata, examples, fas_api_config):
  plugin = multiplug.importer(examples("fas_stats_sh.sh"), **fas_api_config)
  assert plugin.compute(testdata("example.fas")) == \
           ['800', '.41000000000000000000']

def test_auto_rs_fas_plugin(testdata, examples, fas_api_config):
  plugin = multiplug.importer(examples("fas_stats_rs.rs"), **fas_api_config)
  assert plugin.compute(testdata("example.fas")) == \
           ((800, 0.41), [])

def test_auto_py_fas_plugin(testdata, examples, fas_api_config):
  plugin = multiplug.importer(examples("fas_stats_py.py"), **fas_api_config)
  assert plugin.compute(testdata("example.fas")) == \
           ([800, 0.41], [])

def test_auto_nim_fas_plugin(testdata, examples, fas_api_config):
  plugin = multiplug.importer(examples("fas_stats_nim.nim"), **fas_api_config)
  assert plugin.compute(testdata("example.fas")) == \
           (["800", "0.41"], [])
