#
# This file defines a macro, for simplifying the export of constants to Python
#
# export the following consts:
#  const
#    X=1
#    Y=2
#
# without macro:
#   proc py_const_X() {.exportpy.} = X
#   proc py_const_Y() {.exportpy.} = Y
#
# with the macro:
#   exportpy_consts(X, Y)
#
# or, when a different prefix is setup in PyPlugins `api_config`:
#   exportpy_consts_wpfx("c_", X, Y)
#

import macros
const PY_CONST_PFX = "py_const_"

macro exportpy_consts_wpfx*(pfx: string, cnsts: varargs[untyped]): untyped =
  result = newNimNode(nnkStmtList)
  for cnst in cnsts.children:
    let procname = ident($pfx & $cnst)
    let r = quote do:
      proc `procname`(): type(`cnst`) {.exportpy.} = `cnst`
    result.add(r)

macro exportpy_consts*(cnsts: varargs[untyped]): untyped =
  let pfx = PY_CONST_PFX
  result = quote do:
    exportpy_consts_wpfx(`pfx`, `cnsts`)
