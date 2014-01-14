# Copyright (c) 2013, MIT Probabilistic Computing Project.
#
# This file is part of Venture.
#
# Venture is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Venture is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with Venture.  If not, see <http://www.gnu.org/licenses/>.
from venture import shortcuts
from venture.unit import *

class Sprinkler(VentureUnit):
  def makeAssumes(self):
    self.assume("rain","(bernoulli 0.2)")
    self.assume("sprinkler","(bernoulli (if rain 0.01 0.4))")
    self.assume("grassWet","""
(bernoulli
 (if rain
   (if sprinkler 0.99 0.8)
   (if sprinkler 0.9 0.00001)))
""")

  def makeObserves(self):
    self.observe("grassWet", True)

if __name__ == '__main__':
  ripl = shortcuts.make_church_prime_ripl()
  model = Sprinkler(ripl)
  history = model.runFromConditional(50, verbose=True)
  history.plot(fmt='png')
