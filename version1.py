#!/usr/bin/python

# Copyright 2016, Gurobi Optimization, Inc.

# Solve the classic diet model, showing how to add constraints
# to an existing model.

from gurobipy import *



kategorie, minOdzywianie, maxOdzywianie = multidict({
  'kalorie': [1800, 2200],
  'bialko':  [91, GRB.INFINITY],
  'tluszcz':      [0, 65],
  'sod':   [0, 1779] })

jedzenie, koszt = multidict({
  'hamburger': 2.49,
  'kurczak':   2.89,
  'hot dog':   1.50,
  'frytki':     1.89,
  'makaron':  2.09,
  'pizza':     1.99,
  'salata':     2.49,
  'mleko':      0.89,
  'lody': 1.59 })

# Nutrition values for the foods
odzywianieWartosci = {
  ('hamburger', 'kalorie'): 410,
  ('hamburger', 'bialko'):  24,
  ('hamburger', 'tluszcz'):      26,
  ('hamburger', 'sod'):   730,
  ('kurczak',   'kalorie'): 420,
  ('kurczak',   'bialko'):  32,
  ('kurczak',   'tluszcz'):      10,
  ('kurczak',   'sod'):   1190,
  ('hot dog',   'kalorie'): 560,
  ('hot dog',   'bialko'):  20,
  ('hot dog',   'tluszcz'):      32,
  ('hot dog',   'sod'):   1800,
  ('frytki',     'kalorie'): 380,
  ('frytki',     'bialko'):  4,
  ('frytki',     'tluszcz'):      19,
  ('frytki',     'sod'):   270,
  ('makaron',  'kalorie'): 320,
  ('makaron',  'bialko'):  12,
  ('makaron',  'tluszcz'):      10,
  ('makaron',  'sod'):   930,
  ('pizza',     'kalorie'): 320,
  ('pizza',     'bialko'):  15,
  ('pizza',     'tluszcz'):      12,
  ('pizza',     'sod'):   820,
  ('salata',     'kalorie'): 320,
  ('salata',     'bialko'):  31,
  ('salata',     'tluszcz'):      12,
  ('salata',     'sod'):   1230,
  ('mleko',      'kalorie'): 100,
  ('mleko',      'bialko'):  8,
  ('mleko',      'tluszcz'):      2.5,
  ('mleko',      'sod'):   125,
  ('lody', 'kalorie'): 330,
  ('lody', 'bialko'):  8,
  ('lody', 'tluszcz'):      10,
  ('lody', 'sod'):   180 }

# Model
m = Model("diet")

# Create decision variables for the nutrition information,
# which we limit via bounds
odzywianie = m.addVars(kategorie, lb=minOdzywianie, ub=maxOdzywianie, name="odzywianie")

# Create decision variables for the foods to buy
kup = m.addVars(jedzenie, name="kup")

# You could use Python looping constructs and m.addVar() to create
# these decision variables instead.  The following would be equivalent
# to the preceding two statements...
#
# nutrition = {}
# for c in categories:
#   nutrition[c] = m.addVar(lb=minNutrition[c], ub=maxNutrition[c], name=c)
#
# buy = {}
# for f in foods:
#   buy[f] = m.addVar(name=f)

# The objective is to minimize the costs
m.setObjective(kup.prod(koszt), GRB.MINIMIZE)

# Using looping constructs, the preceding statement would be:
#
# m.setObjective(sum(buy[f]*cost[f] for f in foods), GRB.MINIMIZE)

# Nutrition constraints
m.addConstrs(
    (quicksum(odzywianieWartosci[f,c] * kup[f] for f in jedzenie) == odzywianie[c]
     for c in kategorie), "_")

# Using looping constructs, the preceding statement would be:
#
# for c in categories:
#  m.addConstr(
#     sum(nutritionValues[f,c] * buy[f] for f in foods) == nutrition[c], c)

def printSolution():
    if m.status == GRB.Status.OPTIMAL:
        print('\nKoszt: %g' % m.objVal)
        print('\nKup:')
        kupx = m.getAttr('x', kup)
        odzywianiex = m.getAttr('x', odzywianie)
        for f in jedzenie:
            if kup[f].x > 0.0001:
                print('%s %g' % (f, kupx[f]))
        print('\nOdzywianie:')
        for c in kategorie:
            print('%s %g' % (c, odzywianiex[c]))
    else:
        print('Brak rozwiazania')

# Solve
m.optimize()
printSolution()

print('\nDodanie ograniczenia: przynajmniej x porcji nabialu')
m.addConstr(kup.sum(['mleko','lody']) <= 10, "limit_dairy")

# Solve
m.optimize()
printSolution()