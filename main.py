#!/usr/bin/python

from sat.experiment import *
from sat.prob_sat import *
import sys
import statistics


def ratio_cb__medianRuntime_medianEntropy(root, dirs, log, filepath, poolsize, solver):

    config = dict(
        poolsize = poolsize,
        verbose  = True,
        log      = log,
        solver   = solver,
        config   = dict(
            maxTries = 100
        )
    )

    with open(filepath, 'w') as outfile:
        # f(vars,ratio,cb) = (medianRuntime, medianEntropy)
        outfile.write('k,vars,ratio,cb,medianRuntime,medianEntropy\n')
        for (k,vars, ratio), dir in dirs.items():
            for cb in range(0, 50):
                config['config']['cb'] = cb / 10
                config['config']['maxFlips'] = 20 * vars

                exp = Experiment(dir, **config)
                exp.runExperiment()

                medianRuntime = []
                medianEntropy = []

                for r in exp.results:
                    medianRuntime.append(r['totalRuntime'])
                    medianEntropy.append(r['entropy'])

                medianRuntime = statistics.median(medianRuntime)
                medianEntropy = statistics.median(medianEntropy)

                outfile.write(
                    '{},{},{},{},{},{}\n'
                    .format(
                        k,
                        r['variables'],
                        r['ratio'],
                        r['cb'],
                        medianRuntime,
                        medianEntropy
                    )
                )



if __name__ == '__main__':
    root = sys.argv[1]
    dirs = { 
        (3, 500, 4.0): os.path.join(root,'unif-k3-r4.0-v500-c2000'),
        (3, 500, 4.1): os.path.join(root,'unif-k3-r4.1-v500-c2050'),
        (3, 500, 4.2): os.path.join(root,'unif-k3-r4.2-v500-c2100')
    #   (3, 1000, 4.0): os.path.join(root,'unif-k3-r4.0-v1000-c4000'),
    #   (3, 1000, 4.1): os.path.join(root,'unif-k3-r4.1-v1000-c4100'),
    #   (3, 1000, 4.2): os.path.join(root,'unif-k3-r4.2-v1000-c4200')
    }
    ratio_cb__medianRuntime_medianEntropy__3SAT500(
        root,
        dirs,
        sys.stderr,
        'experiment1.csv',
        int(sys.argv[2]),
        ProbSAT
    )