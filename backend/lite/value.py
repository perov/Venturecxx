from abc import ABCMeta
from numbers import Number

class VentureValue(object):
  __metaclass__ = ABCMeta

  def getNumber(self): raise Exception("Cannot convert %s to number" % type(self))
  def getAtom(self): raise Exception("Cannot convert %s to atom" % type(self))
  def getBool(self): raise Exception("Cannot convert %s to bool" % type(self))
  def getSymbol(self): raise Exception("Cannot convert %s to symbol" % type(self))
  def getArray(self, elt_type=None): raise Exception("Cannot convert %s to array" % type(self))
  def getPair(self): raise Exception("Cannot convert %s to pair" % type(self))
  def getSimplex(self): raise Exception("Cannot convert %s to simplex" % type(self))
  def getDict(self): raise Exception("Cannot convert %s to dict" % type(self))
  def getMatrix(self): raise Exception("Cannot convert %s to matrix" % type(self))
  def getSP(self): raise Exception("Cannot convert %s to sp" % type(self))
  def getEnvironment(self): raise Exception("Cannot convert %s to environment" % type(self))

  def asStackDict(self): raise Exception("Cannot convert %s to a stack dictionary" % type(self))

class VentureNumber(VentureValue):
  def __init__(self,number): self.number = number
  def getNumber(self): return self.number
  def asStackDict(self): return {"type":"number","value":self.number}

class VentureAtom(VentureValue):
  def __init__(self,atom): self.atom = atom
  def getNumber(self): return self.atom
  def getBool(self): return self.atom
  def asStackDict(self): return {"type":"atom","value":self.atom}

class VentureBool(VentureValue):
  def __init__(self,boolean): self.boolean = boolean
  def getBool(self): return self.boolean
  def asStackDict(self): return {"type":"boolean","value":self.boolean}

class VentureSymbol(VentureValue):
  def __init__(self,symbol): self.symbol = symbol
  def getSymbol(self): return self.symbol
  def asStackDict(self): return {"type":"symbol","value":self.symbol}

# Venture arrays are heterogeneous, with O(1) access and O(n) copy.
# Venture does not yet have a story for homogeneous packed arrays.
class VentureArray(VentureValue):
  def __init__(self,array): self.array = array
  def getArray(self, elt_type=None):
    if elt_type is None: # No conversion
      return self.array
    else:
      return [elt_type.asPython(v) for v in self.array]
  def asStackDict(self):
    # TODO Are venture arrays reflected as lists to the stack?
    return {"type":"list","value":[v.asStackDict() for v in self.array]}

class VentureNil(VentureValue):
  def __init__(self): pass

class VenturePair(VentureValue):
  def __init__(self,first,rest):
    self.first = first
    self.rest = rest
  def getPair(self): return (self.first,self.rest)

class VentureSimplex(VentureValue):
  def __init__(self,simplex): self.simplex = simplex
  def getSimplex(self): return self.simplex

class VentureDict(VentureValue):
  def __init__(self,d): self.dict = d
  def getDict(self): return self.dict

class VentureMatrix(VentureValue):
  def __init__(self,matrix): self.matrix = matrix
  def getMatrix(self): return self.matrix

class SPRef(VentureValue):
  def __init__(self,makerNode): self.makerNode = makerNode
  def asStackDict(self): return {"type":"SP","value":self}

## SPs and Environments as well
## Not Requests, because we do not reflect on them

def isVentureValue(thing):
  return thing is None or isinstance(thing, VentureValue)

class VentureType(object): pass

# TODO Is there any way to make these guys be proper singleton
# objects?

# This is a prototypical example of the classes I am autogenerating
# below, for legibility.  I could have removed this and added "Number"
# to the list in the for.
class NumberType(VentureType):
  def asVentureValue(self, thing): return VentureNumber(thing)
  def asPython(self, vthing): return vthing.getNumber()

# TODO Also Nil?
for typename in ["Atom", "Bool", "Symbol", "Array", "Pair", "Simplex", "Dict", "Matrix", "SP", "Environment"]:
  # Exec is appropriate for metaprogramming, but indeed should not be used lightly.
  # pylint: disable=exec-used
  exec("""
class %sType(VentureType):
  def asVentureValue(self, thing): return Venture%s(thing)
  def asPython(self, vthing): return vthing.get%s()
""" % (typename, typename, typename))

class NilType(VentureType):
  def asVentureValue(self, thing):
    # TODO Throw an error if not null-line?
    return VentureNil()
  def asPython(self, vthing):
    # TODO Throw an error if not nil?
    return []

# A Venture expression is either a Venture self-evaluating object
# (bool, number, atom), or a Venture symbol, or a Venture array of
# Venture Expressions.
# data Expression = Bool | Number | Atom | Symbol | Array Expression
class ExpressionType(VentureType):
  def asVentureValue(self, thing):
    if isinstance(thing, bool):
      return VentureBool(thing)
    if isinstance(thing, Number):
      return VentureNumber(thing)
    # TODO How do we actually evaluate literal atoms?
    if isinstance(thing, str):
      return VentureSymbol(thing)
    if hasattr(thing, "__getitem__"): # Already not a string
      return VentureArray([self.asVentureValue(v) for v in thing])
    else:
      raise Exception("Cannot convert Python object %r to a Venture Expression" % thing)

  def asPython(self, thing):
    if isinstance(thing, VentureBool):
      return thing.getBool()
    if isinstance(thing, VentureNumber):
      return thing.getNumber()
    if isinstance(thing, VentureAtom):
      return thing.getAtom()
    if isinstance(thing, VentureSymbol):
      return thing.getSymbol()
    if isinstance(thing, VentureArray):
      return thing.getArray(self)
