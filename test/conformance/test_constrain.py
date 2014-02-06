from venture.test.stats import statisticalTest, reportKnownMean
from nose.tools import eq_, raises
from venture.test.config import get_ripl, collectSamples
from nose import SkipTest

def testConstrainAVar1a():
  ripl = get_ripl()
  ripl.assume("x","(normal 0.0 1.0)")
  ripl.assume("y","(normal 0.0 1.0)")
  ripl.observe("(if (scope_include 0 0 (flip)) x y)", 3.0)
  ripl.predict("x", label="pid")
  ripl.infer({"kernel":"mh","transitions":20,"scope":0,"block":0})
  eq_(ripl.report("pid"), 3)

def testConstrainAVar1b():
  ripl = get_ripl()
  ripl.assume("x","(normal 0.0 1.0)")
  ripl.assume("y","(normal 0.0 1.0)")
  ripl.predict("x", label="pid")
  ripl.observe("(if (scope_include 0 0 (flip)) x y)", 3.0)
  ripl.infer({"kernel":"mh","transitions":20,"scope":0,"block":0})
  eq_(ripl.report("pid"), 3)

def testConstrainAVar2a():
  ripl = get_ripl()
  ripl.assume("x","(normal 0.0 1.0)")
  ripl.assume("y","(normal 0.0 1.0)")
  ripl.assume("f","(mem (lambda () (scope_include 0 0 (flip))))")
  ripl.predict("(if (f) x y)", label="pid")
  ripl.observe("(if (f) x y)", 3.0)
  ripl.infer({"kernel":"mh","transitions":20,"scope":0,"block":0})
  eq_(ripl.report("pid"), 3)

def testConstrainAVar2b():
  ripl = get_ripl()
  ripl.assume("x","(normal 0.0 1.0)")
  ripl.assume("y","(normal 0.0 1.0)")
  ripl.assume("f","(mem (lambda () (scope_include 0 0 (flip))))")
  ripl.predict("(if (not (f)) x y)", label="pid")
  ripl.observe("(if (f) x y)", 3.0)
  ripl.infer({"kernel":"mh","transitions":20,"scope":0,"block":0})
  eq_(ripl.report("pid"), 3)

def testConstrainAVar3a():
  ripl = get_ripl()
  ripl.assume("x","(normal 0.0 1.0)")
  ripl.assume("y","(normal 0.0 1.0)")
  ripl.assume("f","(mem (lambda () (flip)))")
  ripl.predict("x", label="pid")
  ripl.observe("(if (f) x y)", 3.0)
  ripl.observe("(f)","true")
  ripl.infer({"kernel":"mh","transitions":20})
  eq_(ripl.report("pid"), 3)

def testConstrainAVar3b():
  ripl = get_ripl()
  ripl.assume("x","(normal 0.0 1.0)")
  ripl.assume("y","(normal 0.0 1.0)")
  ripl.assume("f","(mem (lambda () (flip)))")
  ripl.observe("(if (f) x y)", 3.0)
  ripl.predict("x", label="pid")
  ripl.observe("(f)","true")
  ripl.infer({"kernel":"mh","transitions":20})
  eq_(ripl.report("pid"), 3)


def testConstrainAVar4a():
  """We allow downstream processing with no requests and no randomness."""
  ripl = get_ripl()
  ripl.assume("x","(normal 0.0 1.0)")
  ripl.assume("y","(normal 0.0 1.0)")
  ripl.assume("f","(mem (lambda () (scope_include 0 0 (flip))))")
  ripl.predict("(if (f) (* x 5) (* y 5))", label="pid")
  ripl.observe("(if (f) x y)", 3.0)
  ripl.infer({"kernel":"mh","transitions":20,"scope":0,"block":0})

def testConstrainAVar4b():
  ripl = get_ripl()
  ripl.assume("x","(normal 0.0 1.0)")
  ripl.assume("y","(normal 0.0 1.0)")
  ripl.assume("f","(mem (lambda () (scope_include 0 0 (flip))))")
  ripl.predict("(if (not (f)) (* x 5) (* y 5))", label="pid")
  ripl.observe("(if (f) x y)", 3.0)
  ripl.infer({"kernel":"mh","transitions":20,"scope":0,"block":0})

def testConstrainAVar4c():
  ripl = get_ripl()
  ripl.assume("x","(normal 0.0 1.0)")
  ripl.assume("y","(normal 0.0 1.0)")
  ripl.assume("f","(mem (lambda () (scope_include 0 0 (flip))))")
  ripl.predict("(* x 5)", label="pid")
  ripl.observe("(if (f) x y)", 3.0)
  ripl.infer({"kernel":"mh","transitions":20,"scope":0,"block":0})

@raises(Exception)
def testConstrainAVar5a():
  """
    This program is illegal, because when proposing to f, we may end up constraining x,
    which needs to be propagated but the propagation reaches a random choice. This could
    in principal be allowed because there is no exchangeable couping, but for now we have
    decided to forbid all non-identity downstream edges.
  """
  ripl = get_ripl()
  ripl.assume("x","(normal 0.0 1.0)")
  ripl.assume("y","(normal 0.0 1.0)")
  ripl.assume("f","(mem (lambda () (scope_include 0 0 (flip))))")
  ripl.predict("(normal x 0.0001)")
  ripl.observe("(if (f) x y)", 3.0)
  ripl.infer({"kernel":"mh","transitions":20,"scope":0,"block":0})

@raises(Exception)
def testConstrainAVar5b():
  """
    This program is illegal, because when proposing to f, we may end up constraining x,
    and x has a child in A (it is in the (new)brush itself).
  """
  ripl = get_ripl()
  ripl.assume("x","(normal 0.0 1.0)")
  ripl.assume("y","(normal 0.0 1.0)")
  ripl.assume("f","(mem (lambda () (scope_include 0 0 (flip))))")
  ripl.predict("(if (f) (normal x 0.0001) (normal y 0.0001))")
  ripl.observe("(if (f) x y)", 3.0)
  ripl.infer({"kernel":"mh","transitions":20,"scope":0,"block":0})

@raises(Exception)
def testConstrainAVar6a():
  """
    This program is illegal, because when proposing to f, we may end up constraining x,
    and x has a child that makes requests.
  """
  ripl = get_ripl()
  ripl.assume("x","(normal 0.0 1.0)")
  ripl.assume("y","(normal 0.0 1.0)")
  ripl.assume("f","(mem (lambda () (scope_include 0 0 (flip))))")
  ripl.predict("(if (< (normal x 1.0) 3) x y)")
  ripl.observe("(if (f) x y)", 3.0)
  ripl.infer({"kernel":"mh","transitions":20,"scope":0,"block":0})

@raises(Exception)
def testConstrainAVar6b():
  """
    This program is illegal, because when proposing to f, we may end up constraining x,
    and x has a child that makes requests.
  """
  ripl = get_ripl()
  ripl.assume("x","(normal 0.0 1.0)")
  ripl.assume("y","(normal 0.0 1.0)")
  ripl.assume("f","(mem (lambda () (scope_include 0 0 (flip))))")
  ripl.observe("(if (f) x y)", 3.0)
  ripl.predict("(if (< (normal x 1.0) 3) x y)")
  ripl.infer({"kernel":"mh","transitions":20,"scope":0,"block":0})

@raises(Exception)
def testConstrainWithAPredict1():
  """
  We may constrain the (flip) in f, and this has a child that makes requests. Therefore this
  should (currently) throw an exception.
  """
  ripl = get_ripl()
  ripl.assume("f","(mem (lambda () (flip)))")
  ripl.assume("op1","(if (flip) flip (lambda () (f)))")
  ripl.assume("op2","(if (op1) op1 (lambda () (op1)))")
  ripl.assume("op3","(if (op2) op2 (lambda () (op2)))")
  ripl.assume("op4","(if (op3) op2 op1)")
  ripl.predict("(op4)")
  ripl.observe("(op4)",True)
  predictions = collectSamples(ripl,6)


@statisticalTest
def testConstrainWithAPredict2():
  """This test will fail at first, since we previously considered a program like this to be illegal
     and thus did not handle it correctly (we let the predict go stale). So we do not continually
     bewilder our users, I suggest that we handle this case WHEN WE CAN, which means we propagate
     from a constrain as long as we don't hit an absorbing node or a DRG node with a kernel."""
  ripl = get_ripl()
  ripl.assume("f","(if (flip) (lambda () (normal 0.0 1.0)) (mem (lambda () (normal 0.0 1.0))))")
  ripl.observe("(f)","1.0")
  ripl.predict("(* (f) 100)",label="pid")
  predictions = collectSamples(ripl,"pid")
  return reportKnownMean(50, predictions)

