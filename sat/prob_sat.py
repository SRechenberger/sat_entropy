from sat.utils import *

class ProbSAT:

    defaultCB = {3: {'poly': 2.38, 'exp' : 2.5},
                 4: {'poly': 3.0,  'exp' : 3.0},
                 5: {'poly': 3.6,  'exp' : 3.6},
                 6: {'poly': 4.4,  'exp' : 4.4}}


    def initProbs(self):
        if self.func == 'poly':
            self.probs = []
            for i in range(0, self.formula.maxOccs+1):
                self.probs.append(pow(self.eps+i, -self.cb))
        elif self.func == 'exp':
            self.probs = []
            for i in range(0, self.formula.maxOccs+1):
                self.probs.append(pow(self.cb, -i))
        else:
            raise ValueError('func=\'{}\' must either be \'poly\' or \'exp\'.'
                             .format(self.func))


    def __init__(self, formula, cb=None, maxFlips=None, maxTries=None, func='poly'):
        if isinstance(formula, CNF):
            self.formula = formula
        elif type(formula) == str:
            self.formula = CNF(formula)
        else:
            raise TypeError("formula = {} is neither a cnf-formula nor a string"
                            .format(formula))


        if maxFlips == None:
            self.maxFlips = sys.maxsize
        elif type(maxFlips) == int:
            self.maxFlips = maxFlips
        else:
            raise TypeError("maxFlips={} is not of type int."
                            .format(maxFlips))

        if maxTries == None:
            self.maxTries = sys.maxsize
        elif type(maxTries) == int:
            self.maxTries = maxTries
        else:
            raise TypeError("maxTries={} is not of type int."
                            .format(maxTries))

        if cb == None:
            self.cb = ProbSAT.defaultCB[max(map(len, self.formula.clauses))][func]
        elif type(cb) == float:
            self.cb = cb
        else:
            raise TypeError("cb={} is not of type float."
                            .format(cb))

        self.func = func
        self.eps = 1
        self.initProbs()
        self.tracker = Entropytracker()
        self.flips = 0
        self.tries = 0


    def initWalk(self, seed=None):
        # Init empty list of false clauses
        self.falseClauses = Falselist()
        # Init random assignment
        self.assignment   = Assignment(atoms=None,
                                       varCount = self.formula.numVars,
                                       seed=seed)
        # Init break scoreboard
        self.scoreboard   = Breakscore(self.formula,
                                       self.assignment,
                                       self.falseClauses)


    def solve(self, seed=None, minEntropy=None, lookBack=None):
        withLookBack = type(minEntropy) == float and type(lookBack) == int

        for t in range(0, self.maxTries):
            self.tries = t
            self.initWalk(seed)
            if withLookBack:
                walkTracker = Entropytracker(size=lookBack)
            for f in range(0, self.maxFlips):

                self.flips = f
                unsat = len(self.falseClauses)
                # if (a is model for F) then
                #   reeturn a
                if unsat == 0:
                    return True
                # C_u <- randomly selected unsat clause
                ci  = self.falseClauses.lst[f % unsat]
                c   = self.formula.clauses[ci]

                # for x in C_u do
                #   compute f(x,a)
                ws  = [self.probs[self.scoreboard.getBreakScore(abs(lit))]
                       for lit in c]

                # var <- random variable x according to probability
                #   f(x,a)/sum(x in C_u, f(x,a))
                lit = random.choices(c, weights=ws)[0]

                # flip(var)
                self.scoreboard.flip(abs(lit),
                                     self.formula,
                                     self.assignment,
                                     self.falseClauses)
                self.tracker.add(abs(lit))
                if withLookBack:
                    walkTracker.add(abs(lit))
                    h = walkTracker.getEntropy()
                    if not h == None and h < minEntropy:
                        print('Early break at h={} (flips={})'
                              .format(h, f))
                        break



        return False
