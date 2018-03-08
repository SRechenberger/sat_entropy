import os
import sys
import time
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
                 log      = sys.stdout):
        self.verbose=verbose
        self.log=log
        self.setupFormulae(directory)
        self.poolsize = poolsize
        if solver:
            self.setupSolvers(solver, config)
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


    def setupFormulae(self, directory):
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
        self.formulae = list(map(lambda f: CNF(os.path.join(directory, f)),
                                 filter(lambda f: f.endswith('.cnf'),
                                        os.listdir(directory))))

        # Raise a waring, if the directory is empty,
        # and no output is to be expected.
        if len(self.formulae) <= 0:
            raise RuntimeWarning(
                'There are no test files: there will be no output.')

        if self.verbose:
            print(' ...formulae set up.',
                  flush=True,
                  file=self.log)


    def _run(self,f):
        f()
        return f

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
            self.solvers = pool.map(self._run, self.solvers)
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

        self.results=[]
        for solver in self.solvers:
            self.results.append(dict(
                variables     = solver.formula.numVars,
                clauses       = solver.formula.numClauses,
                ratio         = solver.formula.ratio,
                cb            = solver.cb,
                sat           = 1 if solver.sat else 0,
                # assignment    = solver.assignment,
                tries         = solver.tries,
                flips         = solver.flips,
                earlyRestarts = solver.earlyRestarts,
                entropy       = solver.averageEntropy))

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

        if label:
            toReturn = ""
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







