#
# (c) 2022 Giorgio Gonnella, University of Goettingen, Germany
#
"""
Exceptions for the library
"""

class MultiplugError(Exception):
  """parent class for package-specific errors"""
  pass

class InterfaceRequirementError(MultiplugError):
  """raised when a requirement in api_config is not met"""
  pass

class UnsupportedLangError(MultiplugError):
  """raised when a plugin is written in an unsupported language"""
  pass
