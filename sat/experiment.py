import os
import sys
import time
import random
from io import IOBase
from sat.utils import CNF
from multiprocessing import Pool


# def run(f):
#    f()
#    return f

class Experiment:
    # TODO needs overhaul!!!

    def __init__(self,
                 directory,
                 poolsize = 1,
                 solver   = None,
                 config   = dict(),
                 verbose  = False,
                 seed     = None,
                 prob     = 1,
                 log      = sys.stdout):
        if type(prob) is float and prob > 1 or prob <= 0:
            raise ValueError(
                'prob={} must be in (0,1].'
                .format(prob)
            )
        elif type(prob) is int and prob < 1:
            raise ValueError(
                'prob={} must be greater than 1.'
                .format(prob)
            )

        self.verbose=verbose
        self.log=log
        self.setupFormulae(directory, prob)
        self.poolsize = poolsize
        self.config = config
        self.seed = None
        if solver:
            self.solver=solver
            self.ready=True
        else:
            self.ready=False
        self.executed = False


    def setupSolvers(self, solver, config = dict()):
        if self.verbose:
            print('Setting up {} solvers... '.format(solver.__name__),
                  flush=True,
                  file=self.log)

        if type(config) is not dict:
            raise TypeError('kwargs=({}:{}) should be a dict.'
                            .format(kwargs, type(kwargs)))

        self.solvers = list(
            map(lambda cnf: solver(cnf, **config),
                self.formulae))

        self.ready = True
        self.run = False
        if self.verbose:
            print(' ...solvers set up.',
                  flush=True,
                  file=self.log)


    def setupFormulae(self, directory, prob):
        if self.verbose:
            print('Setting up formulae... ',
                  flush=True,
                  file=self.log)

        # Check the argument type.
        if type(directory) is not str:
            raise TypeError('directory=({}::{}) should be a str.'
                            .format(directory, type(directory)))

        # Load the formulae
        #   os.listdir directory
        #   >>> filter (\f -> f.endswith('.cnf'))
        #   >>> map CNF
        self.formulae = list(
            map(
                lambda f: os.path.join(directory, f),
                filter(
                    lambda f: f.endswith('.cnf'),
                    os.listdir(directory)
                )
            )
        )

        self.formulae = random.sample(
            self.formulae,
            int(len(self.formulae)*prob) if type(prob) is float else prob
        )

        # Raise a waring, if the directory is empty,
        # and no output is to be expected.
        if len(self.formulae) <= 0:
            raise RuntimeWarning(
                'There are no test files: there will be no output.')

        if self.verbose:
            print(' ...formulae set up.',
                  flush=True,
                  file=self.log)


    def _runSolver(self, filepath):
        solver = self.solver(filepath,**self.config)
        solver.solve(self.seed)
        return dict(
            variables      = solver.formula.numVars,
            clauses        = solver.formula.numClauses,
            ratio          = solver.formula.ratio,
            cb             = solver.cb,
            sat            = 1 if solver.sat else 0,
            # assignment    = solver.assignment,
            tries          = solver.tries,
            flips          = solver.flips,
            totalFlips     = ((solver.tries-1) * solver.maxFlips + solver.flips) * (10 if solver.sat == 0 else 1),
            earlyRestarts  = solver.earlyRestarts,
            entropy        = solver.averageEntropy,
            flipsPerSecond = solver.flipsPerSecond,
            lastRunEntropy = solver.lastRunEntropy
        )

    def runExperiment(self):
        if self.verbose:
            print('Running Solvers... ',
                  file=self.log,
                  flush=True)

        if not self.ready:
            raise RuntimeError('First run prepareSolvers.')

        if self.executed:
            raise RuntimeWarning('Experiment already run!')



        with Pool(processes=self.poolsize) as pool:
            log = self.log
            del self.log
            begin = time.time()
            self.results = pool.map(self._runSolver, self.formulae)
            end = time.time()
            self.log = log

        totalSecs = int(end - begin)
        secs = totalSecs % 60
        mins = (totalSecs // 60) % 60
        hours = totalSecs // (60*60)


        if self.verbose:
            print(' ...solvers run; took {}h{}m{}s'.format(hours, mins, secs),
                  file=self.log,
                  flush=True)

        self.executed = True


    def getResultsAsString(self,
                           requestedColumns=None,
                           pretty=False,
                           label=False):
        if len(self.results) <= 0:
            raise RuntimeWarning(
                'There are no results, maybe due to missing test files.')
            return ''

        if requestedColumns:
            columns = requestedColumns
        else:
            columns = list(self.results[0].keys())


        def formatField(field):
            width = 1 + max(list(map(len, columns)))

            template = '{:'
            if pretty:
                if type(field) == str:
                    template += '>'

                template += str(width)

            if type(field) == float:
                template += '.4f'

            template += '}'

            return template.format(field)

        toReturn = ""
        if label:
            for c in columns[:-1]:
                toReturn += formatField(c) + ','
            toReturn += formatField(columns[-1]) + '\n'

        for r in self.results:
            for c in columns[:-1]:
                field = formatField(r[c])
                toReturn += field + ','
            toReturn += formatField(r[columns[-1]]) + '\n'

        return toReturn


    def printResults(self,
                     outfile=None,
                     requestedColumns=None,
                     pretty=False,
                     label=False):
        if outfile and (type(outfile) is not str and not isinstance(outfile, IOBase)):
            raise TypeError('outfile::{} should be a str or a IOBase.'
                            .format(type(outfile)))
        ownFile = False
        if outfile:
            if type(outfile) == str:
                f = open(outfile, 'w')
                ownFile = True
            elif isinstance(outfile, IOBase):
                f = outfile
        else:
            f = sys.stdout

        f.write(self.getResultsAsString(requestedColumns=requestedColumns,
                                        pretty=pretty,
                                        label=label))

        if ownFile:
            f.close()







