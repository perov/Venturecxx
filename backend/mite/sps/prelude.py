from venture.parser.church_prime.parse import ChurchPrimeParser
from venture.sivm.core_sivm import _modify_expression
from venture.sivm.macro_system import desugar_expression

import venture.lite.exp as e
import venture.lite.types as t
import venture.lite.value as v

from venture.mite.sp_registry import registerBuiltinSP
import venture.mite

with open(venture.mite.__path__[0] + '/prelude.vnt') as f:
  prelude_source = f.read()

parser = ChurchPrimeParser.instance()
instructions = parser.parse_instructions(prelude_source)
for instr in instructions:
  assert instr['instruction'] == 'define'
  name = t.Symbol.asPython(v.VentureValue.fromStackDict(instr['symbol']))
  expr = _modify_expression(desugar_expression(instr['expression']))
  expr = t.Exp.asPython(v.VentureValue.fromStackDict(expr))
  assert e.isLambda(expr)
  (params, body) = e.destructLambda(expr)
  registerBuiltinSP(name, (params, body))
