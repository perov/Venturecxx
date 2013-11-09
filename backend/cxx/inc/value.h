#ifndef VALUE_H
#define VALUE_H

#include "debug.h"
#include "srs.h"
#include "all.h"

#include <string>
#include <valarray>
#include <iostream>
#include <unordered_map>
#include <vector>

#include <boost/python/object.hpp>
#include <boost/python/dict.hpp>
#include <boost/functional/hash.hpp>

struct SP;
struct Node;
struct SPAux;

/* Should be abstract. */
struct VentureValue { 
  virtual boost::python::dict toPython() const;

  virtual string toString() const { return "no_name"; }
  virtual VentureValue * inverseEvaluate() { return this; }

  virtual size_t toHash() const { assert(false); return 0; }
  virtual VentureValue * clone() const { assert(false); return nullptr; }

  virtual ~VentureValue() {}; 

  /* TODO this needs to be implemented for other types besides symbols. */
  virtual bool equals(const VentureValue * & other) const
    { assert(false); return false; } 
};

namespace std {
  template<>
  struct hash<VentureValue*> 
  {
    size_t operator()(const VentureValue * v) const
      { return v->toHash(); }
  };
  template<>
  struct equal_to<VentureValue*> 
  {
    bool operator()(const VentureValue* v1,const VentureValue* v2) const
      { return v1->equals(v2); }
  };
}

struct VentureSymbol : VentureValue
{
  VentureSymbol(const string & sym): sym(sym) {}
  string sym;
  size_t toHash() const override;
  VentureValue * clone() const override;
  VentureValue * inverseEvaluate() override;

  bool equals(const VentureValue * & other) const override;

  boost::python::dict toPython() const override;

};

struct VentureList : VentureValue 
{ 


};

struct VentureNil : VentureList 
{ 
  size_t toHash() const override;
  virtual boost::python::dict toPython() const;
  VentureValue * clone() const override;

};

struct VenturePair : VentureList
{
  VenturePair(VentureValue * first, VentureList * rest): 
    first(first), rest(rest) {}

  size_t toHash() const override;
  VentureValue * clone() const override;
  VentureValue * inverseEvaluate() override;

  virtual boost::python::dict toPython() const;

  VentureValue * first;
  VentureList * rest;
};

struct VentureMap : VentureValue
{ 
  unordered_map<VentureValue*,VentureValue*> map;
};

struct VentureBool : VentureValue 
{ 
  VentureBool(bool pred): pred(pred) {}; 
  VentureValue * clone() const override; 
  size_t toHash() const override { return hash<bool>()(pred); }
  bool pred;
  boost::python::dict toPython() const override;
};

struct VentureNumber : VentureValue 
{ 
  VentureNumber(double x): x(x) {}
  size_t toHash() const override { return hash<double>()(x); }
  VentureValue * clone() const override;
  int getInt() const { return static_cast<int>(x); }
  double x;
  boost::python::dict toPython() const override;
  
};

struct VentureAtom : VentureValue
{
  VentureAtom(uint32_t n): n(n) {}
  size_t toHash() const override { return n; }
  VentureValue * clone() const override;
  uint32_t n;
  boost::python::dict toPython() const override;
};

struct VentureVector : VentureValue
{
  VentureVector(const vector<VentureValue *> xs): xs(xs) {}
  vector<VentureValue *> xs;
  boost::python::dict toPython() const override;

};

/* RequestPSPs must return VentureRequests. */
struct VentureRequest : VentureValue
{
  VentureRequest() {}
  VentureRequest(vector<ESR> esrs): esrs(esrs) {}
  VentureRequest(vector<HSR *> hsrs): hsrs(hsrs) {}
  
  vector<ESR> esrs;
  vector<HSR *> hsrs;

  ~VentureRequest() { for (HSR * hsr : hsrs) { delete hsr; }  }
};

struct VentureSP : VentureValue
{
  VentureSP(SP * sp): sp(sp) {}
  SP * sp;
  Node * makerNode{nullptr}; // set in processMadeSP()
  string toString() const override;
  boost::python::dict toPython() const override;
  VentureValue * clone() const override;
  // TODO return the toPython of the Aux

  ~VentureSP();

};



#endif


