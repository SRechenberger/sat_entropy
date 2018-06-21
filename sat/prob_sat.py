from sat.utils import *
import time
import sys
import random
import copy

class ProbSAT:
    # TODO needs overhaul!!!

    defaultCB = {3: {'poly': 2.38, 'exp' : 2.5},
                 4: {'poly': 3.0,  'exp' : 3.0},
                 5: {'poly': 3.6,  'exp' : 3.6},
                 6: {'poly': 4.4,  'exp' : 4.4},
                 7: {'poly': 4.7,  'exp' : 4.4}}


    def initProbs(self):
        if self.func == 'poly':
            self.probs = []
            for i in range(0, self.formula.maxOccs+1):
                self.probs.append(pow(self.eps+i, -self.cb))
        elif self.func == 'exp':
            self.probs = []
            for i in range(0, self.formula.maxOccs+1):
                if i > 308 and self.cb < 1 and self.cb > 0:
                    self.probs.append(int(1/self.cb)**-(i-1))
                else:
                    self.probs.append(
                        (self.cb ** -i) if self.cb > 0 else 1
                    )
        else:
            raise ValueError('func=\'{}\' must either be \'poly\' or \'exp\'.'
                             .format(self.func))


    def __init__(self,
                 formula,
                 cb=None,
                 maxFlips=None,
                 maxTries=None,
                 timeLimit=None,
                 func=None,
                 minEntropyF=0,
                 lookBack=None,
                 seed=None):
        if isinstance(formula, CNF):
            self.formula = formula
        elif type(formula) == str:
            self.formula = CNF(formula)
            self.formula_fname = formula
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

        if timeLimit == None:
            self.timeLimit = None
        elif type(timeLimit) == int:
            self.timeLimit = timeLimit
        else:
            raise TypeError("timeLimit={} is not of type int."
                            .format(timeLimit))

        if func:
            self.func = func
        elif self.formula.maxClauseLength <= 3:
            self.func = 'poly'
        else:
            self.func = 'exp'


        if cb == None:
            self.cb = ProbSAT.defaultCB[max(map(len, self.formula.clauses))][self.func]
        elif type(cb) == float:
            self.cb = cb
        else:
            raise TypeError("cb={} is not of type float."
                            .format(cb))

        self.eps = 0.9
        self.initProbs()
        self.flips = 0
        self.tries = 0
        self.earlyRestarts = 0
        self.result = None
        self.sat=None
        self.assignment = None

        self.withLookBack = type(minEntropyF) == float and type(lookBack) == int
        if self.withLookBack and (minEntropyF < 0 or minEntropyF > 1):
            raise ValueError('minEntropyF={} should be between 0 and 1.'
                             .format(minEntropyF))

        self.maxEntropy=math.log(self.formula.numVars, 2)
        #if self.withLookBack:
        self.minEntropy = self.maxEntropy*minEntropyF
        self.minEntropyF = minEntropyF

        self.lookBack = lookBack
        self.seed = seed
        self.averageEntropy = 0
        self.runs = []


    def initWalk(self):
        # Init empty list of false clauses
        self.falseClauses = Falselist()
        # Init random assignment
        self.assignment   = Assignment(
            atoms=None,
            varCount = self.formula.numVars,
        )
        # Init break scoreboard
        self.scoreboard   = Breakscore(self.formula,
                                       self.assignment,
                                       self.falseClauses)

    def __call__(self):
        self.solve(self.seed)




    def solve(self, seed):
        def choose(seq, weights):
            s = sum(weights)
            acc = s

            r = random.random() * s
            for i in range(0,len(weights)):
                t = seq[i]
                acc -= weights[i]
                if r >= acc:
                    break

            return t

        random.seed(seed)

        begin = time.time()

        for t in range(1, self.maxTries+1):

            if self.timeLimit and time.time() - begin > self.timeLimit:
                break

            entropy_tracker = Entropytracker(self.maxFlips, self.formula.numVars)

            self.initWalk()

            minUnsat = len(self.falseClauses)

            if self.withLookBack:
                walkTracker = Entropytracker(self.lookBack, self.formula.numVars)


            # Default information for this run
            record = dict(
                flips                    = None,
                early_restart            = False,
                entropy                  = None,
                entropy_estim_at_restart = None,
                minimal_unsat            = None,
                last_unsat               = None,
            )
            for f in range(1, self.maxFlips+1):
                record['flips'] = f
                unsat = len(self.falseClauses)
                if unsat < minUnsat:
                    minUnsat = unsat

                # if (a is model for F) then
                #   return a
                if unsat == 0:
                    end = time.time()
                    self.time = end-begin
                    self.sat = True
                    print(len(self.runs))
                    return

                # C_u <- randomly selected unsat clause
                ci  = self.falseClauses.lst[random.randint(0, unsat-1)]
                c   = self.formula.clauses[ci]

                # for x in C_u do
                #   compute f(x,a)
                ws  = [self.probs[self.scoreboard.getBreakScore(abs(lit))]
                       for lit in c]

                # var <- random variable x according to probability
                #   f(x,a)/sum(x in C_u, f(x,a))
                lit = choose(c, ws)
                entropy_tracker.add(abs(lit))

                # flip(var)
                self.scoreboard.flip(
                    abs(lit),
                    self.formula,
                    self.assignment,
                    self.falseClauses
                )

                # Measuring step data
                if self.withLookBack:
                    walkTracker.add(abs(lit))
                    record['entropy_estim_at_restart'] = walkTracker.getEntropy(relative = True)
                    h = walkTracker.getEntropy(relative = True) if walkTracker.queue.isFilled() else None
                    if h and h > self.minEntropyF:
                        if random.random() >= (self.minEntropyF/h):
                            self.earlyRestarts += 1
                            record['early_restart'] = True
                            break

            record['minimal_unsat'] = minUnsat
            record['last_unsat']    = unsat
            record['entropy']       = entropy_tracker.getEntropy(relative = True)
            self.runs.append(record)


        end = time.time()
        print(len(self.runs))
        self.time = end-begin
        self.sat = False
