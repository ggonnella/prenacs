#
# (c) 2022 Giorgio Gonnella, University of Goettingen, Germany
#
import pytest
import os

@pytest.fixture
def testdata():
  return lambda fn: os.path.join(\
      os.path.join(os.path.dirname(__file__),"testdata/"), fn)

@pytest.fixture
def testplugins():
  return lambda fn: os.path.join(\
      os.path.join(os.path.dirname(__file__),"testplugins/"), fn)

@pytest.fixture
def examples():
  return lambda fn: os.path.join(\
      os.path.join(os.path.dirname(__file__),"../examples/"), fn)

@pytest.fixture
def fas_api_config():
  api_config = {}
  api_config["req_func"] = ["compute"]
  api_config["opt_func"] = ["initialize", "finalize"]
  api_config["req_const"] = ["ID", "VERSION", "INPUT", "OUTPUT"]
  api_config["opt_const"] = ["METHOD", "IMPLEMENTATION", "PARAMETERS",
                             "ADVICE","REQ_SOFTWARE", "REQ_HARDWARE"]
  return api_config
