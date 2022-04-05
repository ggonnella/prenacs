import pytest
import pyplugins

def test_auto_bash_fas_plugin_disabled(testdata, examples, fas_api_config):
  config = fas_api_config.copy()
  config["disable_bash"] = True
  with pytest.raises(pyplugins.error.UnsupportedLangError):
    pyplugins.importer(examples("fas_stats_sh.sh"), config)

def test_bash_const_req_error(testdata, examples, fas_api_config):
  with pytest.raises(pyplugins.error.InterfaceRequirementError):
    plugin = pyplugins.bash(testdata("sh_const_req_error.sh"),
                                     fas_api_config)

def test_bash_func_req_error(testdata, examples, fas_api_config):
  with pytest.raises(pyplugins.error.InterfaceRequirementError):
    plugin = pyplugins.bash(testdata("sh_func_req_error.sh"),
                                     fas_api_config)

def test_py_const_req_error(testdata, examples, fas_api_config):
  with pytest.raises(pyplugins.error.InterfaceRequirementError):
    plugin = pyplugins.py(testdata("py_const_req_error.py"),
                                   fas_api_config)

def test_py_func_req_error(testdata, examples, fas_api_config):
  with pytest.raises(pyplugins.error.InterfaceRequirementError):
    plugin = pyplugins.py(testdata("py_func_req_error.py"),
                                   fas_api_config)

def test_rust_const_req_error(testdata, examples, fas_api_config):
  with pytest.raises(pyplugins.error.InterfaceRequirementError):
    plugin = pyplugins.rust(testdata("rust_const_req_error.rs"),
                                   fas_api_config)

def test_rust_func_req_error(testdata, examples, fas_api_config):
  with pytest.raises(pyplugins.error.InterfaceRequirementError):
    plugin = pyplugins.rust(testdata("rust_func_req_error.rs"),
                                   fas_api_config)

def test_nim_const_req_error(testdata, examples, fas_api_config):
  with pytest.raises(pyplugins.error.InterfaceRequirementError):
    plugin = pyplugins.nim(testdata("nim_const_req_error.nim"),
                                   fas_api_config)

def test_nim_func_req_error(testdata, examples, fas_api_config):
  with pytest.raises(pyplugins.error.InterfaceRequirementError):
    plugin = pyplugins.nim(testdata("nim_func_req_error.nim"),
                                   fas_api_config)

def test_bash_opt_consts(testdata, examples, fas_api_config):
  plugin = pyplugins.bash(testdata("sh_no_req_error.sh"),
                                   fas_api_config)
  assert plugin.ADVICE is not None
  assert plugin.METHOD is None
  assert not hasattr(plugin, "UNDECLARED_CONST")
  assert plugin.initialize is not None
  assert plugin.finalize is None
  assert not hasattr(plugin, "undeclared_func")

def test_py_opt_consts(testdata, examples, fas_api_config):
  plugin = pyplugins.py(testdata("py_no_req_error.py"),
                                 fas_api_config)
  assert plugin.ADVICE is not None
  assert plugin.METHOD is None
  assert plugin.UNDECLARED_CONST == "imported"
  assert plugin.initialize is not None
  assert plugin.finalize is None
  assert plugin.undeclared_func() == "imported"

def test_rust_opt_const(testdata, examples, fas_api_config):
  plugin = pyplugins.rust(testdata("rust_no_req_error.rs"),
                                   fas_api_config)
  assert plugin.ADVICE is not None
  assert plugin.METHOD is None
  assert plugin.UNDECLARED_CONST == "imported"
  assert plugin.initialize is not None
  assert plugin.finalize is None
  assert plugin.undeclared_func() == "imported"

def test_nim_opt_const(testdata, examples, fas_api_config):
  plugin = pyplugins.nim(testdata("nim_no_req_error.nim"),
                                   fas_api_config)
  assert plugin.ADVICE is not None
  assert plugin.METHOD is None
  assert plugin.UNDECLARED_CONST == "imported"
  assert plugin.initialize is not None
  assert plugin.finalize is None
  assert plugin.undeclared_func() == "imported"

def test_nim_changed_const_pfx(testdata, examples, fas_api_config):
  with pytest.raises(pyplugins.error.InterfaceRequirementError):
    plugin = pyplugins.nim(testdata("nim_changed_const_pfx.nim"),
                                   fas_api_config)
  api_config = fas_api_config.copy()
  api_config["nim_const_pfx"] = "python_constant_"
  plugin = pyplugins.nim(testdata("nim_changed_const_pfx.nim"),
                                   api_config)
  assert plugin.ID is not None

def test_rust_changed_const_klass(testdata, examples, fas_api_config):
  with pytest.raises(pyplugins.error.InterfaceRequirementError):
    plugin = pyplugins.rust(testdata("rust_changed_const_klass.rs"),
                                   fas_api_config)
  api_config = fas_api_config.copy()
  api_config["rust_const_klass"] = "PythonConstants"
  plugin = pyplugins.rust(testdata("rust_changed_const_klass.rs"),
                                   api_config)
  assert plugin.ID is not None
