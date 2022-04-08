import pytest
import snacli

@pytest.mark.script_launch_mode('subprocess')
def test_complete(script_runner, cases, casesdir):
  script_fn = cases("complete.py")
  snake_fn = cases("complete.snake")
  arguments = ["testdata/input1",
               "testdata/input2",
               "test_out/output1",
               "test_out/output2",
               "param1",
               "param2",
               "--i3", "testdata/input3",
               "-x", "testdata/x",
               "--o3", "test_out/output3",
               "-y", "test_out/y",
               "--p3",
               "-z"]
  stdout_expected = ["testdata/input1",
                     "testdata/input2",
                     "testdata/input3",
                     "testdata/x",
                     "test_out/output1",
                     "test_out/output2",
                     "test_out/output3",
                     "test_out/y",
                     "param1",
                     "param2",
                     "True",
                     "True"]
  ret_cli = script_runner.run(script_fn, *arguments)
  assert ret_cli.returncode == 0
  stdout_cli = ret_cli.stdout.rstrip().split("\n")
  assert stdout_cli == stdout_expected
  ret_sna = script_runner.run("snakemake",
       "-d", casesdir, "-j", "1", "-s", snake_fn)
  assert ret_sna.returncode == 0
  stdout_sna = ret_sna.stdout.rstrip().split("\n")
  assert stdout_sna == stdout_expected
