#include "builtin.h"
#include "sp.h"
#include "sps/deterministic.h"

map<string,VentureValuePtr> initBuiltInValues() 
{
  map<string,VentureValuePtr> m;
  m["true"] = shared_ptr<VentureBool>(new VentureBool(true));
  m["false"] = shared_ptr<VentureBool>(new VentureBool(false));
  return m;
}

map<string,shared_ptr<VentureSP> > initBuiltInSPs()
{
  map<string,shared_ptr<VentureSP> > m;

  /* Deterministic SPs */
  m["plus"] = shared_ptr<VentureSP>(new VentureSP(new NullRequestPSP(), new PlusOutputPSP()));
  m["minus"] = shared_ptr<VentureSP>(new VentureSP(new NullRequestPSP(), new MinusOutputPSP()));
  m["times"] = shared_ptr<VentureSP>(new VentureSP(new NullRequestPSP(), new TimesOutputPSP()));
  m["div"] = shared_ptr<VentureSP>(new VentureSP(new NullRequestPSP(), new DivOutputPSP()));
  m["eq"] = shared_ptr<VentureSP>(new VentureSP(new NullRequestPSP(), new EqOutputPSP()));
  m["gt"] = shared_ptr<VentureSP>(new VentureSP(new NullRequestPSP(), new GtOutputPSP()));
  m["gte"] = shared_ptr<VentureSP>(new VentureSP(new NullRequestPSP(), new GteOutputPSP()));
  m["lt"] = shared_ptr<VentureSP>(new VentureSP(new NullRequestPSP(), new LtOutputPSP()));
  m["lte"] = shared_ptr<VentureSP>(new VentureSP(new NullRequestPSP(), new LteOutputPSP()));
  m["sin"] = shared_ptr<VentureSP>(new VentureSP(new NullRequestPSP(), new SinOutputPSP()));
  m["cos"] = shared_ptr<VentureSP>(new VentureSP(new NullRequestPSP(), new CosOutputPSP()));
  m["tan"] = shared_ptr<VentureSP>(new VentureSP(new NullRequestPSP(), new TanOutputPSP()));
  m["hypot"] = shared_ptr<VentureSP>(new VentureSP(new NullRequestPSP(), new HypotOutputPSP()));
  m["exp"] = shared_ptr<VentureSP>(new VentureSP(new NullRequestPSP(), new ExpOutputPSP()));
  m["log"] = shared_ptr<VentureSP>(new VentureSP(new NullRequestPSP(), new LogOutputPSP()));
  m["pow"] = shared_ptr<VentureSP>(new VentureSP(new NullRequestPSP(), new PowOutputPSP()));
  m["sqrt"] = shared_ptr<VentureSP>(new VentureSP(new NullRequestPSP(), new SqrtOutputPSP()));
  m["not"] = shared_ptr<VentureSP>(new VentureSP(new NullRequestPSP(), new NotOutputPSP()));
  m["is_symbol"] = shared_ptr<VentureSP>(new VentureSP(new NullRequestPSP(), new IsSymbolOutputPSP()));

  return m;
}
