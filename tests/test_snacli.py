#
# (c) 2022 Giorgio Gonnella, University of Goettingen, Germany
#
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

@pytest.mark.script_launch_mode('subprocess')
def test_mandatory(script_runner, cases, casesdir):
  script_fn = cases("complete.py")
  snake_fn = cases("complete.snake")
  arguments = ["testdata/input1",
               "testdata/input2",
               "test_out/output1",
               "test_out/output2",
               "param1"]
  stdout_expected = ["testdata/input1",
                     "testdata/input2",
                     "None",
                     "None",
                     "test_out/output1",
                     "test_out/output2",
                     "None",
                     "None",
                     "param1",
                     "None",
                     "False",
                     "False"]
  ret_cli = script_runner.run(script_fn, *arguments)
  assert ret_cli.returncode == 0
  stdout_cli = ret_cli.stdout.rstrip().split("\n")
  assert stdout_cli == stdout_expected
  ret_sna = script_runner.run("snakemake",
       "-d", casesdir, "-j", "1", "-s", snake_fn, "mandatory")
  assert ret_sna.returncode == 0
  stdout_sna = ret_sna.stdout.rstrip().split("\n")
  assert stdout_sna == stdout_expected

@pytest.mark.script_launch_mode('subprocess')
def test_noparams(script_runner, cases, casesdir):
  script_fn = cases("noparams.py")
  snake_fn = cases("noparams.snake")
  arguments = ["testdata/input1",
               "testdata/input2",
               "test_out/output1",
               "test_out/output2",
               "--i3", "testdata/input3",
               "-x", "testdata/x",
               "--o3", "test_out/output3",
               "-y", "test_out/y"]
  stdout_expected = ["testdata/input1",
                     "testdata/input2",
                     "testdata/input3",
                     "testdata/x",
                     "test_out/output1",
                     "test_out/output2",
                     "test_out/output3",
                     "test_out/y"]
  ret_cli = script_runner.run(script_fn, *arguments)
  assert ret_cli.returncode == 0
  stdout_cli = ret_cli.stdout.rstrip().split("\n")
  assert stdout_cli == stdout_expected
  ret_sna = script_runner.run("snakemake",
       "-d", casesdir, "-j", "1", "-s", snake_fn)
  assert ret_sna.returncode == 0
  stdout_sna = ret_sna.stdout.rstrip().split("\n")
  assert stdout_sna == stdout_expected

@pytest.mark.script_launch_mode('subprocess')
def test_noinput(script_runner, cases, casesdir):
  script_fn = cases("noinput.py")
  snake_fn = cases("noinput.snake")
  arguments = ["test_out/output1",
               "test_out/output2",
               "param1",
               "param2",
               "--o3", "test_out/output3",
               "-y", "test_out/y",
               "--p3",
               "-z"]
  stdout_expected = ["test_out/output1",
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
       "-d", casesdir, "-j", "1", "-s", snake_fn, "-f")
  assert ret_sna.returncode == 0
  stdout_sna = ret_sna.stdout.rstrip().split("\n")
  assert stdout_sna == stdout_expected

@pytest.mark.script_launch_mode('subprocess')
def test_nooutput(script_runner, cases, casesdir):
  script_fn = cases("nooutput.py")
  snake_fn = cases("nooutput.snake")
  arguments = ["testdata/input1",
               "testdata/input2",
               "param1",
               "param2",
               "--i3", "testdata/input3",
               "-x", "testdata/x",
               "--p3",
               "-z"]
  stdout_expected = ["testdata/input1",
                     "testdata/input2",
                     "testdata/input3",
                     "testdata/x",
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

@pytest.mark.script_launch_mode('subprocess')
def test_custom_map(script_runner, cases, casesdir):
  script_fn = cases("custom_map.py")
  snake_fn = cases("custom_map.snake")
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

