"""
Exceptions for the library
"""

class PyPluginsError(Exception):
  """parent class for package-specific errors"""
  pass

class InterfaceRequirementError(PyPluginsError):
  """raised when a requirement in api_config is not met"""
  pass

class UnsupportedLangError(PyPluginsError):
  """raised when a plugin is written in an unsupported language"""
  pass
