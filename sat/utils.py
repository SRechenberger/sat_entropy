import random
import re
import math

class Queue:
    """ Models a queue with no need for explicit deletion. """
    def __init__(self, size):
        self.size = size
        self.begin = 0
        self.filled = 0
        self.lst = []

    def __len__(self):
        return len(self.lst)

    def isFilled(self):
        if self.size == None:
            return True
        return len(self.lst) >= self.size


    def write(self, elem):
        """ Writes an element into the queue and returns the value
        overwritten, or None.
        """
        if not self.isFilled() or self.size == None:
            # Filling phase
            self.lst.append(elem)
            self.filled += 1
            return None
        else:
            tmp = self.lst[self.begin]
            self.lst[self.begin] = elem
            self.begin += 1
            self.begin %= self.size
            return tmp
class Falselist:
    """ Models a list with no need for order. """
    def __init__(self):
        self.lst = []
        self.mapping = {}


    def remove(self, idx):
        if not type(idx) == int:
            raise TypeError('Type of idx :: {} is not int'
                            .format(type(idx)))
        if idx < 0:
            raise IndexError('idx = {} is negative'
                             .format(idx))
        if idx >= len(self.lst):
            raise IndexError('idx = {} is greater or equal to len(lst) = {}'
                             .format(idx, len(self.lst)))

        tmp = self.lst[idx]
        if idx == len(self.lst)-1:
            self.lst.pop()
        else:
            self.lst[idx] = self.lst.pop()
            self.mapping[self.lst[idx]] = idx
        del self.mapping[tmp]


    def add(self, elem):
        self.lst.append(elem)
        self.mapping[elem] = len(self.lst)-1


    def __len__(self):
        return self.length()

    def length(self):
        return len(self.lst)

class Entropytracker:
    def __init__(self, size = None):
        self.queue = Queue(size)
        self.count = {}
        self.entropy = 0
        self.size = size
        self.isInit = False


    def calculateEntropy(self):
        self.entropy = 0
        if self.size == None:
            elements = len(self.queue.lst)
        else:
            elements = self.size

        if not self.isInit or self.size == None:
            for _, cnt in self.count.items():
                p = cnt / elements
                self.entropy -= p * math.log(p,2)
            self.isInit = True and self.size != None



    def add(self, elem):
        """ Adds a new element to the queue, and updates the entropy. """
        ret = self.queue.write(elem)
        if self.size == None:
            elements = len(self.queue.lst)
        else:
            elements = self.size

        # if there is some return value,
        # the queue is filled sufficiently.
        if ret:
            # If the queue was not sufficiently filled until now,
            # initiate the entropy.
            self.calculateEntropy()

            # Calculate the old probability of the removed element.
            p = self.count[ret] / elements
            # Remove it from the sum.
            self.entropy += p * math.log(p,2)

            # Decrement the counter of the dropped element.
            self.count[ret] -= 1
            # If the counter is null, delete the field.
            if self.count[ret] == 0:
                del self.count[ret]
            # Otherwise, calculate the new entropy,
            # and add it to the sum.
            else:
                p = self.count[ret] / elements
                self.entropy -= p * math.log(p,2)

            # If the added element is new in the queue,
            # set its counter to 1.
            if elem not in self.count:
                self.count[elem] = 1
            # Otherwise, calculate the old probability of the new element,
            # and remove it from the sum.
            else:
                p = self.count[elem] / elements
                self.entropy += p * math.log(p,2)
                # Increment the counter of the new element.
                self.count[elem] += 1

            # Calculate the new probability of the added element,
            # and add it to the sum.
            p = self.count[elem] / elements
            self.entropy -= p *  math.log(p,2)
        else:
            if elem in self.count:
                self.count[elem] += 1
            else:
                self.count[elem] = 1


    def getEntropy(self):
        """ If the queue is sufficiently filled, return the entropy,
        otherwise return None.
        """

        # Return the entropy only, if the queue is sufficiently filled,
        # for it would not be valid otherwise.
        if self.queue.isFilled() or self.size == None:
            if self.size == None or self.entropy == 0:
                self.calculateEntropy()
            return self.entropy
        else:
            return None
class CNF:
    """ Models CNF-Formulas in the DIMACS format """

    def __init__(self, filepath = None):
        """ Create a new formula which is either empty,
        and must be initialized later on, or give a filepath
        from which the formula is read.
        """
        self.clauses = []
        self.numClauses = 0
        self.numVars = 0
        self.comments = []
        self.occurrences = {}

        if filepath == None:
            self.isInit = False
        else:
            self.initFormulaFromFile(filepath)

    def initFormulaFromFile(self, filepath):
        """ Given the filepath of a CNF file in DIMACS format,
        read it and initialize the object.
        """
        if not type(filepath) == str:
            raise TypeError("Argument 'filepath' was no string.")

        # Terminate, if the file has no .cnf extension.
        if not filepath.endswith('.cnf'):
            raise ValueError(filepath + " is no .cnf file.")

        # Parse the file.
        with open(filepath) as f:
            r = re.compile(r'-?\d+')  # find numbers

            for line in f:
                if line[0] == 'c':
                    self.comments.append(line)
                elif line[0] == 'p':
                    n, m = r.findall(line)
                    self.numVars = int(n)
                    self.numClauses = int(m)
                else:
                    self.clauses.append(list(map(int, r.findall(line)))[:-1])

        for idx in range(0, self.numClauses):
            for literal in self.clauses[idx]:
                if literal in self.occurrences:
                    self.occurrences[literal].append(idx)
                else:
                    self.occurrences[literal] = [idx]

        self.maxOccs = 0
        for _, occ in self.occurrences.items():
            if len(occ) > self.maxOccs:
                self.maxOccs = len(occ)


        self.isInit = True



    def __str__(self):
        """ Represent formula in DIMACS format """

        self.checkInit()

        toReturn = ''

        for comment in self.comments:
            toReturn += comment
        toReturn += 'p cnf {} {}\n'.format(self.numVars, self.numClauses)
        for clause in self.clauses:
            for literal in clause:
                toReturn += '{} '.format(literal)
            toReturn += '0\n'

        return toReturn


    def isSatisfiedBy(self, assignment):
        self.checkInit()

        if not isinstance(assignment, Assignment):
            raise TypeError('The given argument is no assignment.')

        for clause in self.clauses:
            trueClause = False
            for literal in clause:
                if assignment.isTrue(literal):
                    trueClause = True
                    break
            if not trueClause:
                return False

        return True

    def checkInit(self):
        if not self.isInit:
            raise RuntimeError("Formula not initialized yet.")

    def getOccurrences(self, literal):
        if literal in self.occurrences:
            return self.occurrences[literal]
        else:
            return []


class Assignment:

    def __init__(self, atoms = None, varCount = None, seed = None):
        if atoms == None and varCount == None:
            self.atoms = None
            self.varCount = None
            self.isInit = False
        elif atoms == None:
            if not type(varCount) == int:
                raise TypeError("varCount was no int.")
            self.varCount = varCount
            self.initRandomly()
        else:
            if varCount == None:
                self.varCount = len(atoms)
                self.atoms = atoms
            else:
                if len(atoms) != varCount:
                    raise ValueError(
                        "len(atoms) = {} and given varCount = {} do net match."
                            .format(len(atoms), varCount))
                else:
                    self.varCount = varCount
                    self.atoms = atoms


    def initRandomly(self):
        self.atoms = [None]
        for i in range(1, self.varCount+1):
            if random.randint(0,1) == 0:
                self.atoms.append(False)
            else:
                self.atoms.append(True)


    def isTrue(self, literal):
        if not type(literal) == int:
            raise TypeError("literal = {} is no int.".format(literal))

        var = abs(literal)
        if var <= 0:
            raise ValueError("var = {} is negative or zero.".format(var))

        if var > self.varCount:
            raise ValueError("var = {} is greater than varCount = {}"
                            .format(var, self.varCount))

        return (literal > 0) == self.atoms[abs(literal)]


    def flip(self, var):
        if not type(var) == int:
            raise TypeError("var = {} is no int.".format(var))

        if var <= 0:
            raise ValueError("var = {} is negative or zero.".format(var))

        if var > self.varCount:
            raise ValueError("var = {} is greater than varCount = {}"
                            .format(var, self.varCount))

        self.atoms[var] = not self.atoms[var]


    def __str__(self):
        l = 0
        toReturn = 'n = {}'.format(self.varCount)
        for i in range(1,self.varCount+1):
            if l % 32 == 0:
                toReturn += '\n'
            if self.atoms[i]:
                toReturn += '1'
            else:
                toReturn += '0'
            l += 1

        return toReturn

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
                falselist.add(clauseIdx)

            # next clause
            clauseIdx += 1


    def incrementBreakScore(self, variable):
        if not type(variable) == int:
            raise TypeError("variable={} is not of type int.".format(variable))

        if variable in self.breaks:
            self.breaks[variable] += 1
        else:
            self.breaks[variable] = 1

    def getBreakScore(self, variable):
        if not type(variable) == int:
            raise TypeError("variable={} is not of type int.".format(variable))

        if variable in self.breaks:
            return self.breaks[variable]
        else:
            return 0



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
        satisfyingLiteral = variable if assignment.isTrue(variable) else -variable
        # falsifyingLiteral = a[v] ? -v : v
        # isn't this just -satisfyingLiteral ?
        falsifyingLiteral = -variable if assignment.isTrue(variable) else variable
        occs = formula.occurrences
        for clauseIdx in formula.getOccurrences(satisfyingLiteral):
            if self.numTrueLit[clauseIdx] == 0:
                falselist.remove(falselist.mapping[clauseIdx])
                self.incrementBreakScore(variable)
                self.critVar[clauseIdx] = variable
            elif self.numTrueLit[clauseIdx] == 1:
                self.breaks[self.critVar[clauseIdx]] -= 1
            self.numTrueLit[clauseIdx] += 1

        for clauseIdx in formula.getOccurrences(falsifyingLiteral):
            if self.numTrueLit[clauseIdx] == 1:
                falselist.add(clauseIdx)
                self.breaks[variable] -= 1
                self.critVar[clauseIdx] = variable
            elif self.numTrueLit[clauseIdx] == 2:
                for lit in formula.clauses[clauseIdx]:
                    if assignment.isTrue(lit):
                        self.critVar[clauseIdx] = abs(lit)
                        self.incrementBreakScore(abs(lit))
            self.numTrueLit[clauseIdx] -= 1
