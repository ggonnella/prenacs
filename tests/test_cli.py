import pytest
import pyplugins

def test_bash(examples, testdata, script_runner):
  script_fn = examples("batch_compute.py")
  plugin_fn = examples("fas_stats_sh.sh")
  input_fn = testdata("example.fas")
  ret = script_runner.run(script_fn, plugin_fn, input_fn)
  assert ret.returncode == 0
  assert ret.stdout.rstrip() == "\t".join([input_fn,
    '800', '.410000000000000000'])

def test_py(examples, testdata, script_runner):
  script_fn = examples("batch_compute.py")
  plugin_fn = examples("fas_stats_py.py")
  input_fn = testdata("example.fas")
  ret = script_runner.run(script_fn, plugin_fn, input_fn)
  assert ret.returncode == 0
  assert ret.stdout.rstrip() == "\t".join([input_fn,
    "[800, 0.41]", "[]"])

def test_rs(examples, testdata, script_runner):
  script_fn = examples("batch_compute.py")
  plugin_fn = examples("fas_stats_rs.rs")
  input_fn = testdata("example.fas")
  ret = script_runner.run(script_fn, plugin_fn, input_fn)
  assert ret.returncode == 0
  assert ret.stdout.rstrip() == "\t".join([input_fn,
    "(800, 0.41)", "[]"])

def test_nim(examples, testdata, script_runner):
  script_fn = examples("batch_compute.py")
  plugin_fn = examples("fas_stats_nim.nim")
  input_fn = testdata("example.fas")
  ret = script_runner.run(script_fn, plugin_fn, input_fn)
  assert ret.returncode == 0
  assert ret.stdout.rstrip() == "\t".join([input_fn,
    "['800', '0.41']", "[]"])
