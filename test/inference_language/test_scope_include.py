from venture.test.config import get_ripl, broken_in

@broken_in('puma', "puma can't handle arrays as blocks in a scope_include.")
def testArrayBlock():
  ripl = get_ripl()
  
  ripl.predict('(scope_include 1 (array 1 1) (flip))')
  
  ripl.infer('(mh 1 (array 1 1) 1)')
