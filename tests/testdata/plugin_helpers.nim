import macros
import nimpy

const PY_CONST_PFX = "py_const_"

macro exportconst(cnst: untyped): untyped =
  let procname = ident(PY_CONST_PFX & $cnst)
  result = quote do:
    proc `procname`(): type(`cnst`) {.exportpy.} = `cnst`

macro exportconst_as_none(cnst: untyped): untyped =
  let procname = ident(PY_CONST_PFX & $cnst)
  result = quote do:
    let py = pyBuiltinsModule()
    proc `procname`(): type(py.None) {.exportpy.} = py.None

template exportoptional(sym: untyped): untyped =
  ##
  ## This template checks if a symbol has been declared and if not, it calls a
  ## macro which exports it as Python None. The template is necessary, as it
  ## is not possible to check if the symbol is declared inside the macros.
  ##
  when not declared(sym):
    exportconst_as_none(sym)
  else:
    exportconst(sym)

template export_plugin_metadata*(): untyped =
  ##
  ## Template to call _after_ defining the constants for the plugin metadata.
  ## This exports the constants to Python as functions with no arguments,
  ## adding a prefix "py_const_" to them.
  ##
  exportoptional(ID)
  exportoptional(VERSION)
  exportoptional(INPUT)
  exportoptional(OUTPUT)
  exportoptional(PARAMETERS)
  exportoptional(METHOD)
  exportoptional(IMPLEMENTATION)
  exportoptional(REQ_SOFTWARE)
  exportoptional(REQ_HARDWARE)
  exportoptional(ADVICE)
