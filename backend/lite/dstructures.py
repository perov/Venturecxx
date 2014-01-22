from psp import PSP

### Simplex Points

class SimplexOutputPSP(PSP):
  def simulate(self,args): return args.operandValues

### Polymorphic Operators
class LookupOutputPSP(PSP):
  def simulate(self,args): return args.operandValues[0][args.operandValues[1]]


### Lists (use Python lists instead of VenturePairs
class PairOutputPSP(PSP):
  def simulate(self,args): return [args.operandValues[0]] + args.operandValues[1]

class IsPairOutputPSP(PSP): 
  def simulate(self,args): return len(args.operandValues[0]) > 0

class ListOutputPSP(PSP): 
  def simulate(self,args): return args.operandValues

class ListRefOutputPSP(PSP): 
  def simulate(self,args): return args.operandValues[0][args.operandValues[1]]

class FirstListOutputPSP(PSP): 
  def simulate(self,args): return args.operandValues[0][0]

class RestListOutputPSP(PSP): 
  def simulate(self,args): return args.operandValues[0][1:]

### Arrays

class ArrayOutputPSP(PSP):
  def simulate(self,args): return args.operandValues

