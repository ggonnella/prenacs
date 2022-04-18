#
# (c) 2021-2022 Giorgio Gonnella, University of Goettingen, Germany
#
from sqlalchemy import select
from sqlalchemy.schema import MetaData
from pathlib import Path
import yaml
import getpass
import socket
import uuid
import os

ECHO=False
SELFPATH = Path(os.path.abspath(os.path.dirname(__file__)))
TESTDATA = SELFPATH / "testdata"
BIN = SELFPATH / ".." / "bin"
PREFIX = "prenacs_"
PFXAVT = f"{PREFIX}attribute_value_t"

def check_attributes(definitions, connection):
  meta = MetaData()
  meta.reflect(bind=connection)
  adef_t = meta.tables[f"{PREFIX}attribute_definition"]
  rows = connection.execute(select(adef_t.c.name, adef_t.c.datatype,
                                   adef_t.c.computation_group)).all()
  assert(set(r.name for r in rows) == set(definitions.keys()))
  for r in rows:
    assert(r.datatype == definitions[r.name]["datatype"])
    assert(r.computation_group == definitions[r.name]["computation_group"])
  assert(f"{PFXAVT}4" not in meta.tables)
  for n in [0, 1, 2, 3]:
    assert(f"{PFXAVT}{n}" in meta.tables)
  print(set(meta.tables[f"{PFXAVT}0"].c.keys()))
  assert(set(meta.tables[f"{PFXAVT}0"].c.keys()) ==
         {"entity_id", "g1a_v", "g1a_c", "g1b_v", "g1b_c",
                       "g1c_v", "g1c_c", "g1_g"})
  assert(set(meta.tables[f"{PFXAVT}1"].c.keys()) ==
         {"entity_id", "g1d_v", "g1d_c", "g1_g",
                       "g2a_v", "g2a_c", "g2b_v", "g2b_c", "g2_g"})
  assert(set(meta.tables[f"{PFXAVT}2"].c.keys()) ==
         {"entity_id", "g3a_v0", "g3a_v1", "g3a_c", "g3_g"})
  assert(set(meta.tables[f"{PFXAVT}3"].c.keys()) ==
         {"entity_id", "g3b_v0", "g3b_v1", "g3b_v2", "g3b_v3",
                       "g3b_c", "g3_g"})

def check_no_attributes(connection):
  meta = MetaData()
  meta.reflect(bind=connection)
  adef_t = meta.tables[f"{PREFIX}attribute_definition"]
  rows = connection.execute(select(adef_t.c.name, adef_t.c.datatype,
                                   adef_t.c.computation_group)).all()
  assert(len(rows) == 0)
  assert(f"{PFXAVT}4" not in meta.tables)
  for n in [0, 1, 2, 3]:
    assert(f"{PFXAVT}{n}" in meta.tables)
    assert(set(meta.tables[f"{PFXAVT}{n}"].c.keys()) == {"entity_id"})

def computation_id(n):
  return uuid.UUID(f'00000000-0000-0000-0000-00000000000{n}').bytes

def get_attribute_value_rows(connection):
  meta = MetaData()
  meta.reflect(bind=connection)
  tnums = [0,1,2,3]
  r = []
  for n in tnums:
    t = meta.tables[f"{PFXAVT}{n}"]
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

def check_results(outfilename, expectedfilename, basename=False):
  results = {}
  expected = {}
  with open(expectedfilename) as f:
    for line in f:
      elems = line.rstrip().split("\t")
      key = elems.pop(0)
      expected[key] = elems
  with open(outfilename) as f:
    for line in f:
      elems = line.rstrip().split("\t")
      entity_id = elems.pop(0)
      if basename:
        entity_id = os.path.basename(entity_id)
      results[entity_id] = elems
  assert(results == expected)

def check_file_content(filename, expected):
  with open(filename) as f:
    assert(f.read() == expected)

def check_empty_file(filename):
  check_file_content(filename, "")

def check_report(reportfilename,
                 plugin_id, plugin_version, n_units, comp_status, reason=None,
                 user_id=getpass.getuser(), system_id=socket.gethostname(),
                 params={}):
  with open(reportfilename) as f:
    report = yaml.safe_load(f)
  assert(report["plugin_id"] == plugin_id)
  assert(report["plugin_version"] == plugin_version)
  assert(report["n_units"] == n_units)
  assert(report["comp_status"] == comp_status)
  report_params = yaml.safe_load(report["parameters"])
  assert(report_params == params)
  assert(report["user_id"] == user_id)
  assert(report["system_id"] == system_id)
  assert(report["reason"] == reason)

