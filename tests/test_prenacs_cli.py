#
# (c) 2021-2022 Giorgio Gonnella, University of Goettingen, Germany
#

import pytest
import yaml
from helper import TESTDATA, check_attributes, ECHO, \
                   BIN, check_values_after_run, check_no_attributes, \
                   check_results, check_file_content, check_empty_file, \
                   check_report
import os
import tempfile
from contextlib import contextmanager

@pytest.mark.script_launch_mode('subprocess')
def test_prenacs_cli(connection_creator, connection_args, script_runner):
  ret = script_runner.run(str(BIN/"prenacs-setup-database"), *connection_args)
  assert(ret.returncode == 0)
  attrs = connection_args + [TESTDATA/"fake_attrs.yaml", "--testmode"]
  ret = script_runner.run(str(BIN/"prenacs-manage-attributes"), *attrs)
  assert(ret.returncode == 0)
  with open(TESTDATA/"fake_attrs.yaml") as f:
    definitions = yaml.safe_load(f)
  connection = connection_creator()
  check_attributes(definitions, connection)
  connection.close()
  for testn in [1, 2, 1, 3, 4, 5, 6, 7]:
    attrs = connection_args + [TESTDATA/f"fake_results{testn}.tsv",
                               TESTDATA/f"fake_report{testn}.yaml",
                               TESTDATA/f"fake_plugin{testn}.py"]
    script_runner.run(str(BIN/"prenacs-load-results"), *attrs)
    connection = connection_creator()
    check_values_after_run(testn, connection)
    connection.close()
  attrs = connection_args + [TESTDATA/"empty_dict.yaml", "--drop", "--testmode"]
  ret = script_runner.run(str(BIN/"prenacs-manage-attributes"), *attrs)
  assert(ret.returncode == 0)
  connection = connection_creator()
  check_no_attributes(connection)
  connection.close()
  ret = script_runner.run(str(BIN/"prenacs-destroy-database"), *connection_args)

@contextmanager
def auto_args(parallel, verbose, params = None):
  reportfile = tempfile.NamedTemporaryFile(mode="w", delete=False)
  reportfile.close()
  outfile = tempfile.NamedTemporaryFile(mode="w", delete=False)
  outfile.close()
  logfile = tempfile.NamedTemporaryFile(mode="w", delete=False)
  logfile.close()
  args = ["--out", outfile.name, "--report", reportfile.name,
         "--log", logfile.name]
  if not parallel:
    args.append("--serial")
  if verbose:
    args.append("--verbose")
  if params:
    paramsfile = tempfile.NamedTemporaryFile(mode="w", delete=False)
    yaml.dump(params, paramsfile)
    paramsfile.close()
    args += ["--params", paramsfile.name]
    yield (args, outfile.name, reportfile.name, logfile.name, paramsfile.name)
    os.unlink(paramsfile.name)
  else:
    yield (args, outfile.name, reportfile.name, logfile.name, None)
  os.unlink(outfile.name)
  os.unlink(logfile.name)
  os.unlink(reportfile.name)

@pytest.mark.script_launch_mode('subprocess')
def test_prenacs_cli_batch_computing_files(script_runner):
  for parallel in [False, True]:
    with auto_args(parallel, ECHO) as \
        (args, outfilename, reportfilename, logfilename, paramsfilename):
      ret = script_runner.run(str(BIN/"prenacs-batch-compute"),
                              str(TESTDATA/"wc_from_filename_plugin.sh"),
                              "files", str(TESTDATA/"*.data"), *args)
      assert(ret.returncode == 0)
      check_report(reportfilename, "wc", "1.0", 9, "completed")
      check_results(outfilename, str(TESTDATA/"wc_expected_wfilename.tsv"),
                    basename=True)
      check_empty_file(logfilename)

@pytest.mark.script_launch_mode('subprocess')
def test_prenacs_cli_batch_computing_ids(script_runner):
  for parallel in [False, True]:
    params = {"testdatadir": str(TESTDATA)}
    with auto_args(parallel, ECHO, params) as \
        (args, outfilename, reportfilename, logfilename, paramsfilename):
      ret = script_runner.run(str(BIN/"prenacs-batch-compute"),
                              str(TESTDATA/"wc_from_id_plugin.sh"),
                              "ids", str(TESTDATA/"ids.tsv"),
                              "--system", "testsystem", *args)
      assert(ret.returncode == 0)
      check_report(reportfilename, "wc", "1.0", 9, "completed", params=params,
                   system_id="testsystem")
      check_results(outfilename, str(TESTDATA/"wc_expected.tsv"))
      check_empty_file(logfilename)

@pytest.mark.script_launch_mode('subprocess')
def test_prenacs_cli_batch_computing_ids_with_error_in_one_unit(script_runner):
  for parallel in [False, True]:
    params = {"testdatadir": str(TESTDATA)}
    with auto_args(parallel, ECHO, params) as \
        (args, outfilename, reportfilename, logfilename, paramsfilename):
      ret = script_runner.run(str(BIN/"prenacs-batch-compute"),
                              str(TESTDATA/"wc_from_id_plugin.sh"),
                              "ids", str(TESTDATA/"ids.tsv"), "2",
                              "--user", "testuser", *args)
      assert(ret.returncode == 0)
      check_report(reportfilename, "wc", "1.0", 9, "completed", params=params,
                   user_id="testuser")
      check_results(outfilename, str(TESTDATA/"wc_expected_wo_9.tsv"))
      check_file_content(logfilename,
          f"0\t{TESTDATA}/input0.data does not exist\n")

@pytest.mark.script_launch_mode('subprocess')
def test_prenacs_cli_batch_computing_ids_with_proc(script_runner):
  for parallel in [False, True]:
    params = {"testdatadir": str(TESTDATA)}
    with auto_args(parallel, ECHO, params) as \
        (args, outfilename, reportfilename, logfilename, paramsfilename):
      ret = script_runner.run(str(BIN/"prenacs-batch-compute"),
                              str(TESTDATA/"wc_from_id_plugin.sh"),
                              "ids", str(TESTDATA/"ids.tsv"), "2",
                              "--idsproc", str(TESTDATA/"one_adder_idsproc.sh"),
                              "--reason", "new_attributes", *args)
      assert(ret.returncode == 0)
      check_report(reportfilename, "wc", "1.0", 9, "completed", params=params,
                   reason="new_attributes")
      check_results(outfilename, str(TESTDATA/"wc_expected.tsv"))
      check_empty_file(logfilename)
