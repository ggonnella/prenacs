#
# (c) 2021-2022 Giorgio Gonnella, University of Goettingen, Germany
#

import yaml
from attrtables import AttributeValueTables
from prenacs import AttributeDefinition, AttributeDefinitionsManager,\
                      ResultsLoader, BatchComputation
from helper import PFXAVT, ECHO, TESTDATA, check_attributes, \
                   check_values_after_run, check_no_attributes, \
                   check_results, check_file_content, check_empty_file, \
                   check_report
import tempfile
import os
from contextlib import contextmanager

def test_prenacs_api_database(connection):
  avt = AttributeValueTables(connection,
                             attrdef_class=AttributeDefinition,
                             tablename_prefix=PFXAVT)
  avt.target_n_columns = 9
  adm = AttributeDefinitionsManager(avt)
  with open(TESTDATA/"fake_attrs.yaml") as f:
    definitions = yaml.safe_load(f)
  adm.apply_definitions(definitions)
  connection.commit()
  check_attributes(definitions, connection)
  for testn in [1, 2, 1, 3, 4, 5, 6, 7]:
    results_loader = ResultsLoader(avt, TESTDATA/f"fake_plugin{testn}.py",
                                   verbose=ECHO)
    results_loader.run(TESTDATA/f"fake_results{testn}.tsv",
                       TESTDATA/f"fake_report{testn}.yaml",
                       verbose=ECHO)
    connection.commit()
    check_values_after_run(testn, connection)
  adm.apply_definitions({})
  connection.commit()
  check_no_attributes(connection)
  avt.drop_all()

@contextmanager
def outfiles(bc, **kwargs):
  reportfile = tempfile.NamedTemporaryFile(mode="w", delete=False)
  outfile = tempfile.NamedTemporaryFile(mode="w", delete=False)
  outfile.close()
  logfile = tempfile.NamedTemporaryFile(mode="w", delete=False)
  logfile.close()
  bc.setup_computation(reportfile=reportfile, **kwargs)
  bc.set_output(outfilename=outfile.name, logfilename=logfile.name)
  yield outfile.name, logfile.name, reportfile.name
  os.unlink(outfile.name)
  os.unlink(logfile.name)
  os.unlink(reportfile.name)

def test_prenacs_api_batch_computing_files():
  for parallel in [True, False]:
    bc = BatchComputation(str(TESTDATA/"wc_from_filename_plugin.sh"))
    bc.input_from_globpattern(str(TESTDATA/"*.data"), verbose=ECHO)
    with outfiles(bc) as (outfilename, logfilename, reportfilename):
      bc.run(verbose=ECHO, parallel=parallel)
      bc.finalize()
      check_report(reportfilename, "wc", "1.0", 9, "completed")
      check_results(outfilename, str(TESTDATA/"wc_expected_wfilename.tsv"),
                    basename=True)
      check_empty_file(logfilename)

def test_prenacs_api_batch_computing_ids():
  for parallel in [True, False]:
    bc = BatchComputation(str(TESTDATA/"wc_from_id_plugin.sh"))
    bc.input_from_idsfile(str(TESTDATA/"ids.tsv"), verbose=ECHO)
    params = {"testdatadir": str(TESTDATA)}
    with outfiles(bc, params=params, system="testsystem") as \
        (outfilename, logfilename, reportfilename):
      bc.run(verbose=ECHO, parallel=parallel)
      bc.finalize()
      check_report(reportfilename, "wc", "1.0", 9, "completed", params=params,
                   system_id="testsystem")
      check_results(outfilename, str(TESTDATA/"wc_expected.tsv"))
      check_empty_file(logfilename)

def test_prenacs_api_batch_computing_ids_with_error_in_one_unit():
  for parallel in [True, False]:
    bc = BatchComputation(str(TESTDATA/"wc_from_id_plugin.sh"))
    bc.input_from_idsfile(str(TESTDATA/"ids.tsv"), 2, verbose=ECHO)
    params = {"testdatadir": str(TESTDATA)}
    with outfiles(bc, params=params, user="testuser") as \
        (outfilename, logfilename, reportfilename):
      bc.run(verbose=ECHO, parallel=parallel)
      bc.finalize()
      check_report(reportfilename, "wc", "1.0", 9, "completed", params=params,
                   user_id="testuser")
      check_results(outfilename, str(TESTDATA/"wc_expected_wo_9.tsv"))
      check_file_content(logfilename,
          f"0\t{TESTDATA}/input0.data does not exist\n")

def test_prenacs_api_batch_computing_ids_with_proc():
  for parallel in [True, False]:
    bc = BatchComputation(str(TESTDATA/"wc_from_id_plugin.sh"))
    bc.input_from_idsfile(str(TESTDATA/"ids.tsv"), 2, verbose=ECHO,
                          idsproc_module=str(TESTDATA/"one_adder_idsproc.sh"))
    params = {"testdatadir": str(TESTDATA)}
    with outfiles(bc, params=params, reason="new_attributes") as \
        (outfilename, logfilename, reportfilename):
      bc.run(verbose=ECHO, parallel=parallel)
      bc.finalize()
      check_report(reportfilename, "wc", "1.0", 9, "completed", params=params,
                   reason="new_attributes")
      check_results(outfilename, str(TESTDATA/"wc_expected.tsv"))
      check_empty_file(logfilename)
