from .dimacs import CNF
from .assignment import Assignment
from .falselist import Falselist

class Breakscore:
    def __init__(self, formula, assignment, falselist):
        if not isinstance(formula, CNF):
            raise TypeError("The given object formula={} is no cnf-formula."
                            .format(formula))
        if not isinstance(assignment, Assignment):
            raise TypeError("The given object assignment={} is no assignment."
                            .format(assignment))
        if not isinstance(falselist, Falselist):
            raise TypeError("The given object falselist={} is no assignment."
                            .format(falselist))


        self.critVar = []
        self.numTrueLit = []
        self.breaks = {}

        # Begin at clause 0
        clauseIdx = 0
        # for each clause of the formula
        for clause in formula.clauses:
            # init the criticial variable
            self.critVar.append(None)
            # init the number of true literals for this clause
            self.numTrueLit.append(0)
            # a local variable to track the critical variable
            critVar = 0
            # for each literal of the clause
            for lit in clause:
                # if the literal is satisfied
                if assignment.isTrue(lit):
                    # it MAY BE the critical variable of the clause
                    critVar = abs(lit)
                    # there is one more true literal
                    self.numTrueLit[-1] += 1

            # if after the traverse of the clause there is exactly one true
            # literal
            if self.numTrueLit[-1] == 1:
                # it is the critical literal
                self.critVar[-1] = critVar
                # thus it breaks the clause
                self.incrementBreakScore(critVar)

            # if there is no true literal
            elif self.numTrueLit[-1] == 0:
                # add the clause to the list of false clauses
                falseList.add(clauseIdx)

            # next clause
            clauseIdx += 1


    def incrementBreakScore(self, variable):
        if type(variable) != int:
            raise TypeError("variable={} is not of type int.".format(variable))

        if variable in self.breaks:
            self.breaks[variable] += 1
        else:
            self.breaks[variable] = 1


    def flip(self, variable, formula, assignment, falselist):
        if type(variable) != int:
            raise TypeError("variable={} is not of type int.".format(variable))
        if not isinstance(formula, CNF):
            raise TypeError("The given object formula={} is no cnf-formula."
                            .format(formula))
        if not isinstance(assignment, Assignment):
            raise TypeError("The given object assignment={} is no assignment."
                            .format(assignment))
        if not isinstance(falselist, Falselist):
            raise TypeError("The given object falselist={} is no assignment."
                            .format(falselist))

        # a[v] = -a[v]
        assignment.flip(variable)
        # satisfyingLiteral = a[v] ? v : -v
        satisfyingLiteral = variable if self.assignment.isTrue(v) else -variable
        # falsifyingLiteral = a[v] ? -v : v
        # isn't this just -satisfyingLiteral ?
        falsifyingLiteral = -variable if self.assignment.isTrue(v) else variable
        occs = formula.occurrences
        for clauseIdx in occs[satisfyingLiteral]:
            if self.numTrueLit[clauseIdx] == 0:
                falseList.remove(clauseIdx)
                self.incrementBreakScore(variable)
                self.critVar[clauseIdx] = variable
            elif numTrueLit[clauseIdx] == 1:
                self.breaks[self.critVar[clauseIdx]] -= 1
            self.numTrueLit[clauseIdx] += 1

        for clauseIdx in occs[falsifyingLiteral]:
            if self.numTrueLit[clauseIdx] == 1:
                falseList.add(clauseIdx)
                self.breaks[variable] -= 1
                self.critVar[clauseIdx] = variable
            elif self.numTrueLit[clauseIdx] == 2:
                for lit in self.formula.clauses[clauseIdx]:
                    if assignment.isTrue(lit):
                        self.critVar[clauseIdx] = abs(lit)
                        self.incrementBreakScore(abs(lit))
            self.numTrueLit[clauseIdx] -= 1



