#
# (c) 2021-2022 Giorgio Gonnella, University of Goettingen, Germany
#

import pytest
import yaml
from helper import TESTDATA, check_attributes, \
                   BIN, check_values_after_run, check_no_attributes

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
