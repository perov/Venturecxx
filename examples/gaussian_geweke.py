from venture.shortcuts import (make_puma_church_prime_ripl,
                               make_lite_church_prime_ripl)
import pandas as pd
import seaborn as sns

NSAMPLE = 50
BURN = 50
THIN = 100

def build_ripl():
  ripl = make_lite_church_prime_ripl()
  program = '''
  [ASSUME mu (scope_include (quote parameters) 0 (normal 0 10))]
  [ASSUME sigma (scope_include (quote parameters) 1 (sqrt (inv_gamma 1 1)))]
  [ASSUME x (scope_include (quote data) 0 (lambda () (normal mu sigma)))]
  '''
  ripl.execute_program(program)
  return ripl

def format_results_marginal(res):
  res = res[0]['value']
  return pd.DataFrame({key : map(lambda x: x['value'], res[key]) for key in res})

def collect_marginal_conditional(ripl):
  'Take draws from priors for mu and sigma'
  infer_statement = '''
  [INFER (cycle
           ((peek mu) (peek sigma)
            (mh (quote parameters) all 1)) {0})]'''.format(NSAMPLE)
  res = format_results_marginal(ripl.execute_program(infer_statement))
  return res

def format_results_successive(res):
  return pd.DataFrame([{key : x['value'][key][0]['value'] for key in x['value']} for x in res])

def collect_succesive_conditional(ripl):
  'Simulate data, infer based on it, forget the simulation, repeat'
  program = '''
    forgetme : [ASSUME dummy (x)]
    [INFER (cycle
             ((peek mu) (peek sigma) (peek dummy)
              (hmc (quote parameters) all 0.1 10 1)) 1)]
    [FORGET forgetme]'''
  res = []
  for i in range(BURN + NSAMPLE * THIN):
  tmp = ripl.execute_program(program)
    if (i >= BURN) and not ((i - BURN) % THIN):
      res.append(tmp)
      print (i - BURN) / THIN
    ripl.forget('forgetme')
  return format_results_successive(res)

def compute_statistics(df, g):
  'Compute the two first and 3 second moments of the parameter vector (mu, sigma)'
  res = pd.DataFrame([f(df) for f in g]).T
  res.columns = ['g' + str(i + 1) for i in range(res.shape[1])]
  M = res.shape[0]
  g_bar, sigma2_g = res.mean(), res.var()
  return {'g' : res, 'M' : M, 'g_bar' : g_bar, 'sigma2_g' : sigma2_g}

def main():
  df_marginal = collect_marginal_conditional(build_ripl())
  df_successive = collect_succesive_conditional(build_ripl())
  # the list of functions of the data and parameters to compute
  g = [lambda df: df.mu,
       lambda df: df.sigma,
       lambda df: df.mu ** 2,
       lambda df: df.sigma ** 2,
       lambda df: df.mu * df.sigma]
  res_marginal = compute_statistics(df_marginal, g)
  res_successive = compute_statistics(df_successive, g)

