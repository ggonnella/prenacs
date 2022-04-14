#
# (c) 2021-2022 Giorgio Gonnella, University of Goettingen, Germany
#

import pytest
from sqlalchemy import create_engine, select, text
from sqlalchemy.schema import MetaData
import yaml
from pathlib import Path
import uuid
import os
from attrtables import AttributeValueTables
from provbatch import AttributeDefinition, AttributeDefinitionsManager, \
                      ResultsLoader
import provbatch.database

ECHO=False
SELFPATH = Path(os.path.abspath(os.path.dirname(__file__)))
TESTDATA = SELFPATH / "testdata"
PREFIX = "pr_attribute_value_t"

def check_attributes(definitions, connection):
  meta = MetaData()
  meta.reflect(bind=connection)
  adef_t = meta.tables["pr_attribute_definition"]
  rows = connection.execute(select(adef_t.c.name, adef_t.c.datatype,
                                   adef_t.c.computation_group)).all()
  assert(set(r.name for r in rows) == set(definitions.keys()))
  for r in rows:
    assert(r.datatype == definitions[r.name]["datatype"])
    assert(r.computation_group == definitions[r.name]["computation_group"])
  assert(f"{PREFIX}4" not in meta.tables)
  for n in [0, 1, 2, 3]:
    assert(f"{PREFIX}{n}" in meta.tables)
  print(set(meta.tables[f"{PREFIX}0"].c.keys()))
  assert(set(meta.tables[f"{PREFIX}0"].c.keys()) ==
         {"entity_id", "g1a_v", "g1a_c", "g1b_v", "g1b_c",
                       "g1c_v", "g1c_c", "g1_g"})
  assert(set(meta.tables[f"{PREFIX}1"].c.keys()) ==
         {"entity_id", "g1d_v", "g1d_c", "g1_g",
                       "g2a_v", "g2a_c", "g2b_v", "g2b_c", "g2_g"})
  assert(set(meta.tables[f"{PREFIX}2"].c.keys()) ==
         {"entity_id", "g3a_v0", "g3a_v1", "g3a_c", "g3_g"})
  assert(set(meta.tables[f"{PREFIX}3"].c.keys()) ==
         {"entity_id", "g3b_v0", "g3b_v1", "g3b_v2", "g3b_v3",
                       "g3b_c", "g3_g"})

def check_no_attributes(connection):
  meta = MetaData()
  meta.reflect(bind=connection)
  adef_t = meta.tables["pr_attribute_definition"]
  rows = connection.execute(select(adef_t.c.name, adef_t.c.datatype,
                                   adef_t.c.computation_group)).all()
  assert(len(rows) == 0)
  assert(f"{PREFIX}4" not in meta.tables)
  for n in [0, 1, 2, 3]:
    assert(f"{PREFIX}{n}" in meta.tables)
    assert(set(meta.tables[f"{PREFIX}{n}"].c.keys()) == {"entity_id"})

def computation_id(n):
  return uuid.UUID(f'00000000-0000-0000-0000-00000000000{n}').bytes

def get_attribute_value_rows(connection):
  meta = MetaData()
  meta.reflect(bind=connection)
  tnums = [0,1,2,3]
  r = []
  for n in tnums:
    t = meta.tables[f"pr_attribute_value_t{n}"]
    rows = connection.execute(select(t)).all()
    r.append({row.entity_id: row for row in rows})
  return r

def check_g1_t0(row, run):
  if run != 2:
    assert(row.g1a_v == 1)
    assert(row.g1b_v == 2)
    assert(row.g1c_v == 3)
    # computation ID in _g and not _c, as whole grp computed
    assert(row.g1_g == computation_id(1))
    for field in ["g1a_c", "g1b_c", "g1c_c"]:
      assert(getattr(row, field) == None)
  else:
    # computation IDs stored in _c for re-computed values
    # as not entire group recomputed
    assert(row.g1a_v == 5)
    assert(row.g1a_c == computation_id(2))
    assert(row.g1b_v == 2)
    assert(row.g1b_c == None)
    assert(row.g1_g == computation_id(1))
    assert(row.g1c_v == 6)
    assert(row.g1c_c == computation_id(2))

def check_g1_t1(row, run):
  assert(row.g1d_c == None)
  if run != 2:
    assert(row.g1d_v == 4)
    assert(row.g1_g == computation_id(1))
  else:
    assert(row.g1d_v == 7)
    assert(row.g1_g == computation_id(2))

def check_g2_t1(row, run):
  if run < 3:
    for field in ["g2a_v", "g2a_c", "g2b_v", "g2b_c", "g2_g"]:
      assert(getattr(row, field) == None)
  else:
    assert(row.g2a_v == 8)
    assert(row.g2a_c == None)
    assert(row.g2_g == computation_id(3))
    if run == 3:
      assert(row.g2b_v == 9)
      assert(row.g2b_c == None)
    else:
      assert(row.g2b_v == 10)
      assert(row.g2b_c == computation_id(4))

def check_g3_t2(row, run):
  assert(row.g3a_v0 == 10)
  assert(row.g3a_v1 == 2.3)
  assert(row.g3a_c == None)
  if run <= 6:
    assert(row.g3_g == computation_id(5))
  else:
    assert(row.g3_g == computation_id(7))

def check_g3_t3(row, run):
  assert(row.g3b_v0 == 1.0)
  assert(row.g3b_v1 == 11)
  assert(row.g3b_v2 == 12)
  assert(row.g3b_v3 == 13)
  assert(row.g3b_c == None)
  if run == 5:
    assert(row.g3_g == computation_id(5))
  else:
    assert(row.g3_g == computation_id(6))

def check_values_after_run(n, connection):
  r = get_attribute_value_rows(connection)
  for accession in ['A1','A2','A3','A4']:
    check_g1_t0(r[0][accession], n)
    check_g1_t1(r[1][accession], n)
    check_g2_t1(r[1][accession], n)
  if n <= 4:
    assert(r[2] == {})
    assert(r[3] == {})
  else:
    for accession in ['A1','A2','A3','A4']:
      check_g3_t2(r[2][accession], n)
      check_g3_t3(r[3][accession], n)

def run_load_results(n, avt):
  results_loader = ResultsLoader(avt, TESTDATA/f"fake_plugin{n}.py",
                                 verbose=ECHO)
  results_loader.run(TESTDATA/f"fake_results{n}.tsv",
                     TESTDATA/f"fake_report{n}.yaml",
                     verbose=ECHO)

def test_provbatch(connection):
  avt = AttributeValueTables(connection,
                             attrdef_class=AttributeDefinition,
                             tablename_prefix=PREFIX)
  avt.target_n_columns = 9
  adm = AttributeDefinitionsManager(avt)
  with open(TESTDATA/"fake_attrs.yaml") as f:
    definitions = yaml.safe_load(f)
  adm.apply_definitions(definitions)
  check_attributes(definitions, connection)
  for testn in [1, 2, 1, 3, 4, 5, 6, 7]:
    run_load_results(testn, avt)
    check_values_after_run(testn, connection)
  adm.apply_definitions({})
  check_no_attributes(connection)
