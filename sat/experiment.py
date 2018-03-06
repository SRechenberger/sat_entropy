import os
from sat.utils import CNF
from multiprocessing import Pool

def run(f):
    f()
    return f

class Experiment:

    def __init__(self, solverconstr, directory, config = dict(), poolsize = 1):
        if type(config) is not dict:
            raise TypeError('kwargs=({}:{}) should be a dict.'
                            .format(kwargs, type(kwargs)))
        print('Reading formulae... ', end='', flush=True)
        self.prepareFormulae(directory)
        print('Done.', flush=True)
        self.poolsize = poolsize
        print('Initializing solvers... ', end='', flush=True)
        self.solvers = list(
            map(lambda cnf: solverconstr(cnf, **config),
                self.formulae))
        print('Done.', flush=True)



    def prepareFormulae(self, directory):
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




    def runExperiment(self, outfile=None):
        if type(outfile) is not str:
            raise TypeError('outfile::{} should be a str.'
                            .format(type(outfile)))

        print('Running Solvers... ', end='', flush=True)
        with Pool(processes=self.poolsize) as pool:
            self.solvers = pool.map(run, self.solvers)
        print(' Done.', end='\n', flush=True)

        self.results=[]
        for solver in self.solvers:
            self.results.append(dict(
                sat           = 1 if solver.sat else 0,
                assignment    = solver.assignment,
                tries         = solver.tries,
                flips         = solver.flips,
                earlyRestarts = solver.earlyRestarts,
                entropy       = solver.tracker.getEntropy()))

        if outfile:
            with open(outfile, 'w') as f:
                f.write('{},{},{},{},{}\n'
                        .format('sat',
                                'tries',
                                'flips',
                                'earlyRestarts',
                                'entropy'))
                for result in self.results:
                    f.write('{},{},{},{},{:.5f}\n'
                            .format(result['sat'],
                                    result['tries'],
                                    result['flips'],
                                    result['earlyRestarts'],
                                    result['entropy']))






