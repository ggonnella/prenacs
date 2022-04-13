#
# (c) 2022 Giorgio Gonnella, University of Goettingen, Germany
#
import pytest
import snacli

@pytest.mark.script_launch_mode('subprocess')
def test_reuse(script_runner, cases, casesdir):
  script1_fn = cases("reuse1.py")
  script2_fn = cases("reuse2.py")
  snake_fn = cases("reuse.snake")
  arguments = ["testdata/input1",
               "test_out/output1",
               "--common1-input", "testdata/input2",
               "--common2-input", "testdata/input3",
               "--common1-output", "test_out/output2",
               "--common2-output", "test_out/output3",
               "--common1-param",
               "--common2-param",
               "-x",
               "-y"]
  arguments1 = arguments + ["--param_sp1"]
  arguments2 = arguments + ["--param_sp2"]
  stdout_expected = ["testdata/input1",
                     "testdata/input2",
                     "testdata/input3",
                     "test_out/output1",
                     "test_out/output2",
                     "test_out/output3",
                     "True", "True", "True", "True", "True"]
  ret_cli1 = script_runner.run(script1_fn, *arguments1)
  assert ret_cli1.returncode == 0
  stdout_cli1 = ret_cli1.stdout.rstrip().split("\n")
  assert stdout_cli1 == stdout_expected

  ret_cli2 = script_runner.run(script2_fn, *arguments2)
  assert ret_cli2.returncode == 0
  stdout_cli2 = ret_cli2.stdout.rstrip().split("\n")
  assert stdout_cli2 == stdout_expected

  ret_sna1 = script_runner.run("snakemake",
       "-d", casesdir, "-j", "1", "-s", snake_fn, "reuse1")
  assert ret_sna1.returncode == 0
  stdout_sna1 = ret_sna1.stdout.rstrip().split("\n")
  assert stdout_sna1 == stdout_expected

  ret_sna2 = script_runner.run("snakemake",
       "-d", casesdir, "-j", "1", "-s", snake_fn, "reuse2")
  assert ret_sna2.returncode == 0
  stdout_sna2 = ret_sna2.stdout.rstrip().split("\n")
  assert stdout_sna2 == stdout_expected
