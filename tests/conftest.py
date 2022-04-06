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
  api_config["required"] = {"functions": ["compute"],
                            "constants": {"strings": ["ID", "VERSION", "INPUT"],
                                          "lists": ["OUTPUT"]}}
  api_config["optional"] = {"functions": ["initialize", "finalize"],
                            "constants": {"strings": ["METHOD",
                                              "IMPLEMENTATION", "ADVICE",
                                              "REQ_SOFTWARE", "REQ_HARDWARE"],
                                          "nested": ["PARAMETERS"]}}
  return api_config
