#!/usr/bin/python

from sat.experiment import *
from sat.prob_sat import *

if __name__ == '__main__':
    root = '/media/sf_VBoxshare/SAT/'
    dirs = { 4.0: root+'unif-k3-r4.0-v1000-c4000',
             4.1: root+'unif-k3-r4.1-v1000-c4100',
             4.2: root+'unif-k3-r4.2-v1000-c4200'}

    config = dict(
        poolsize = 4,
        verbose  = True,
        log      = sys.stderr,
        solver   = ProbSAT,
        config   = dict(
            maxFlips = 20000,
            maxTries = 100
        )
    )

    needLabel = True

    with open('k3.log', 'w') as outfile:
        for dir in dirs.values():
            exp = Experiment(dir, **config)
            exp.runExperiment()
            exp.printResults(
                outfile = outfile,
                label = needLabel
            )
            needLabel=False

