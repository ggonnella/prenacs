import pytest
import pyplugins

def test_bash(examples, testdata, script_runner):
  script_fn = examples("batch_compute.py")
  plugin_fn = examples("fas_stats_sh.sh")
  input_fn = testdata("example.fas")
  ret = script_runner.run(script_fn, plugin_fn, input_fn)
  assert ret.returncode == 0
  assert ret.stdout.rstrip() == "\t".join([input_fn,
    "['800', '.41000000000000000000']"])

def test_py(examples, testdata, script_runner):
  script_fn = examples("batch_compute.py")
  plugin_fn = examples("fas_stats_py.py")
  input_fn = testdata("example.fas")
  ret = script_runner.run(script_fn, plugin_fn, input_fn)
  assert ret.returncode == 0
  assert ret.stdout.rstrip() == "\t".join([input_fn,
    "([800, 0.41], [])"])

def test_rs(examples, testdata, script_runner):
  script_fn = examples("batch_compute.py")
  plugin_fn = examples("fas_stats_rs.rs")
  input_fn = testdata("example.fas")
  ret = script_runner.run(script_fn, plugin_fn, input_fn)
  assert ret.returncode == 0
  assert ret.stdout.rstrip() == "\t".join([input_fn,
    "((800, 0.41), [])"])

def test_nim(examples, testdata, script_runner):
  script_fn = examples("batch_compute.py")
  plugin_fn = examples("fas_stats_nim.nim")
  input_fn = testdata("example.fas")
  ret = script_runner.run(script_fn, plugin_fn, input_fn)
  assert ret.returncode == 0
  assert ret.stdout.rstrip() == "\t".join([input_fn,
    "(['800', '0.41'], [])"])

def test_with_state_py(examples, testdata, script_runner):
  script_fn = examples("batch_compute.py")
  plugin_fn = testdata("echo_plugin.py")
  input_fn = testdata("example.fas")
  ret = script_runner.run(script_fn, plugin_fn, input_fn)
  assert ret.returncode == 0
  assert ret.stdout.rstrip() == "\t".join([input_fn,
    f"(['{input_fn}'], None)"])
  assert ret.stderr.rstrip() == "\n".join([
    "initialized echo state: 0","echo state: 1","finalized echo state: 2"])

def test_bash_retval_types(examples, testdata, script_runner):
  script_fn = examples("batch_compute.py")
  input_fn = testdata("example.fas")
  expected_out = {
      "nested":       input_fn,
      "string":       "-".join([input_fn,""]),
      "list_tab":     str([input_fn,""]),
      "list_newline": str([input_fn,""]),
    }
  for rt in ["nested", "string", "list_tab", "list_newline"]:
    plugin_fn = testdata(f"sh_return_{rt}.sh")
    ret = script_runner.run(script_fn, plugin_fn, input_fn)
    assert ret.returncode == 0
    assert ret.stdout.rstrip() == f"{input_fn}\t{expected_out[rt]}"
    assert ret.stderr.rstrip() == ""

