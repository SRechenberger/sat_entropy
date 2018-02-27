import sat_entropy.utils.assignment as assgn
import re

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

        if not isinstance(assignment, assgn.Assignment):
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


