#
# (c) 2021-2022 Giorgio Gonnella, University of Goettingen, Germany
#

import yaml
from attrtables import AttributeValueTables
from prenacs import AttributeDefinition, AttributeDefinitionsManager,\
                      ResultsLoader
from helper import PFXAVT, ECHO, TESTDATA, check_attributes, \
                    check_values_after_run, check_no_attributes

def test_prenacs_api(connection):
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
