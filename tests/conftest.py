#
# (c) 2022 Giorgio Gonnella, University of Goettingen, Germany
#
import pytest
import os

@pytest.fixture
def cases():
  return lambda fn: os.path.join(\
      os.path.join(os.path.dirname(__file__),"cases/"), fn)

@pytest.fixture
def casesdir():
  return os.path.join(os.path.dirname(__file__),"cases")



