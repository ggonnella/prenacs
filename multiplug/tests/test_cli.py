#
# (c) 2022 Giorgio Gonnella, University of Goettingen, Germany
#
import pytest
import multiplug

def test_bash(examples, testplugins, testdata, script_runner):
  script_fn = examples("batch_compute.py")
  plugin_fn = examples("fas_stats_sh.sh")
  input_fn = testdata("example.fas")
  ret = script_runner.run(script_fn, plugin_fn, input_fn)
  assert ret.returncode == 0
  assert ret.stdout.rstrip() == "\t".join([input_fn,
    "['800', '.41000000000000000000']"])

def test_py(examples, testplugins, testdata, script_runner):
  script_fn = examples("batch_compute.py")
  plugin_fn = examples("fas_stats_py.py")
  input_fn = testdata("example.fas")
  ret = script_runner.run(script_fn, plugin_fn, input_fn)
  assert ret.returncode == 0
  assert ret.stdout.rstrip() == "\t".join([input_fn,
    "([800, 0.41], [])"])

@pytest.mark.script_launch_mode('subprocess')
def test_rs(examples, testplugins, testdata, script_runner):
  script_fn = examples("batch_compute.py")
  plugin_fn = examples("fas_stats_rs.rs")
  input_fn = testdata("example.fas")
  ret = script_runner.run(script_fn, plugin_fn, input_fn)
  assert ret.returncode == 0
  assert ret.stdout.rstrip() == "\t".join([input_fn,
    "((800, 0.41), [])"])

def test_nim(examples, testplugins, testdata, script_runner):
  script_fn = examples("batch_compute.py")
  plugin_fn = examples("fas_stats_nim.nim")
  input_fn = testdata("example.fas")
  ret = script_runner.run(script_fn, plugin_fn, input_fn)
  assert ret.returncode == 0
  assert ret.stdout.rstrip() == "\t".join([input_fn,
    "(['800', '0.41'], [])"])

def test_with_state_py(examples, testplugins, testdata, script_runner):
  script_fn = examples("batch_compute.py")
  plugin_fn = testplugins("py_w_state.py")
  input_fn = testdata("example.fas")
  ret = script_runner.run(script_fn, plugin_fn, input_fn)
  assert ret.returncode == 0
  assert ret.stdout.rstrip() == "\t".join([input_fn, input_fn])
  assert ret.stderr.rstrip() == "\n".join([
    "initialized state, count=0","count=1","finalized state, count=2"])

@pytest.mark.script_launch_mode('subprocess')
def test_with_state_nim(examples, testplugins, testdata, script_runner):
  script_fn = examples("batch_compute.py")
  plugin_fn = testplugins("nim_w_state.nim")
  input_fn = testdata("example.fas")
  ret = script_runner.run(script_fn, plugin_fn, input_fn)
  assert ret.returncode == 0
  assert ret.stdout.rstrip() == "\t".join([input_fn, input_fn])
  assert ret.stderr.rstrip() == "\n".join([
    "initialized state, count=0","count=1","finalized state, count=2"])

@pytest.mark.script_launch_mode('subprocess')
def test_with_state_rust(examples, testplugins, testdata, script_runner):
  script_fn = examples("batch_compute.py")
  plugin_fn = testplugins("rs_w_state.rs")
  input_fn = testdata("example.fas")
  ret = script_runner.run(script_fn, plugin_fn, input_fn)
  assert ret.returncode == 0
  assert ret.stdout.rstrip() == "\t".join([input_fn, input_fn])
  assert ret.stderr.rstrip() == "\n".join([
    "initialized state, count=0","count=1","finalized state, count=2"])

def test_with_state_sh(examples, testplugins, testdata, script_runner):
  script_fn = examples("batch_compute.py")
  plugin_fn = testplugins("sh_w_state.sh")
  input_fn = testdata("example.fas")
  ret = script_runner.run(script_fn, plugin_fn, input_fn)
  assert ret.returncode == 0
  assert ret.stdout.rstrip() == "\t".join([input_fn, input_fn])
  assert ret.stderr.rstrip() == "\n".join([
    "initialized state, count=0","count=1","finalized state, count=2"])

def test_bash_retval_types(examples, testplugins, testdata, script_runner):
  script_fn = examples("batch_compute.py")
  input_fn = testdata("example.fas")
  expected_out = {
      "nested":       str([input_fn, '']),
      "string":       "-".join([input_fn,""]),
      "list_tab":     str([input_fn,""]),
      "list_newline": str([input_fn,"",""]),
    }
  for rt in ["nested", "string", "list_tab", "list_newline"]:
    plugin_fn = testplugins(f"sh_return_{rt}.sh")
    ret = script_runner.run(script_fn, plugin_fn, input_fn)
    assert ret.returncode == 0
    assert ret.stdout.rstrip() == f"{input_fn}\t{expected_out[rt]}"
    assert ret.stderr.rstrip() == ""

