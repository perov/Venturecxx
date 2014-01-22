from psp import PSP
import numpy as np

### Simplex Points

class SimplexOutputPSP(PSP):
  def simulate(self,args): return np.array(args.operandValues)

### Polymorphic Operators
class LookupOutputPSP(PSP):
  def simulate(self,args): return args.operandValues[0][int(args.operandValues[1])]

class ContainsOutputPSP(PSP):
  def simulate(self,args): return args.operandValues[1] in args.operandValues[0]

class SizeOutputPSP(PSP):
  def simulate(self,args): return len(args.operandValues[0])

### Dicts
class DictOutputPSP(PSP):
  def simulate(self,args): 
    d = {}
    d.update(zip(*args.operandValues))
    return d

### Arrays

class ArrayOutputPSP(PSP):
  def simulate(self,args): return np.array(args.operandValues)

class IsArrayOutputPSP(PSP):
  def simulate(self,args): return isinstance(args.operandValues[0],np.ndarray)


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


