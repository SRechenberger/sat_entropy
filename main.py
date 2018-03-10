#!/usr/bin/python

from sat.experiment import *
from sat.prob_sat import *
import sys
import statistics
import os
import time
import io

def log(msg, streams, **kwargs):
    for stream in streams:
        if stream and isinstance(stream, io.IOBase):
            print(msg, file=stream, flush=True, **kwargs)

def experiment(
    solver                 = None,
    input_directories      = dict(),
    output_directory       = '.',
    output_file_name       = 'output',
    # output_file_raw_suffix = 'raw',
    output_file_suffix     = 'csv',
    log_file_suffix        = 'log',
    logstream              = None,
    poolsize               = 1,
    verbose                = False,
    prob                   = 1,
    timeLimit              = None
    ):


    # Set up everything.
    ## Check, if a solver was given.
    if not solver:
        raise ValueError('No solver given.')

    ## set the output file
    output_file_path = os.path.join(
        output_directory,
        '{}.{}'.format(output_file_name,output_file_suffix)
    )

    ## set up the logfile path
    log_file_path = os.path.join(
        output_directory,
        '{}.{}'.format(output_file_name, log_file_suffix)
    )

    config = dict(
        poolsize = poolsize,
        verbose  = verbose,
        log      = sys.stderr,
        solver   = solver,
        prob     = prob,
        config   = dict(
            timeLimit = timeLimit,
        )
    )

    cbs = map(
        lambda x: x/10,
        range(0,50)
    )
    with open(output_file_path, 'w') as outfile:
        with open(log_file_path, 'w') as logfile:
            totalBegin = time.time()
            log('BEGIN', [logfile, logstream])

            needLabel = True
            for (k, vars, ratio), dir in input_directories.items():
                dirBegin = time.time()
                log('  BEGIN directory {}'.format(dir), [logfile, logstream])
                for cb in cbs:
                    cbBegin = time.time()
                    log('    BEGIN cb {:.2f}'.format(cb), [logfile, logstream], end='')

                    config['config']['cb'] = cb
                    config['config']['maxFlips'] = 50 * vars

                    exp = Experiment(dir, **config)
                    exp.runExperiment()
                    exp.printResults(
                        outfile=outfile,
                        label=needLabel,
                    )
                    needLabel = False

                    cbEnd = time.time()
                    cbTime = (cbEnd - cbBegin)
                    log(' ...END cb {} ({:10.0f} sec)'.format(cb, cbTime), [logfile, logstream])

                dirEnd = time.time()
                dirTime = (dirEnd - dirBegin)
                log('  END dir {} ({:10.0f} sec)'.format(dir, dirTime), [logfile, logstream])

            totalEnd = time.time()
            totalTime = (totalEnd - totalBegin)
            log('END ({:10.0f} sec)'.format(totalTime), [logfile, logstream])




if __name__ == '__main__':
    root = sys.argv[1]
    dirs = {
        3: {
    #       (3, 10, 4.0): os.path.join(root,'unif-k3-r4.0-v10-c40'),
    #       (3, 10, 4.1): os.path.join(root,'unif-k3-r4.1-v10-c41'),
    #       (3, 10, 4.2): os.path.join(root,'unif-k3-r4.2-v10-c42')
    #       (3, 500, 4.0): os.path.join(root,'unif-k3-r4.0-v500-c2000'),
    #       (3, 500, 4.1): os.path.join(root,'unif-k3-r4.1-v500-c2050'),
    #       (3, 500, 4.2): os.path.join(root,'unif-k3-r4.2-v500-c2100')
    #       (3, 1000, 4.0): os.path.join(root,'unif-k3-r4.0-v1000-c4000'),
    #       (3, 1000, 4.1): os.path.join(root,'unif-k3-r4.1-v1000-c4100'),
            (3, 1000, 4.2): os.path.join(root,'unif-k3-r4.2-v1000-c4200'),
    #       (3, 1000, 4.26): os.path.join(root,'unif-k3-r4.26-v1000-c4260')
        },
        5: {
            (5, 500, 20): os.path.join(root,'unif-k5-r20.0-v500-c10000')
        },
        7: {
            (7, 500, 85): os.path.join(root,'unif-k7-r85.0-v90-c7650')
        }
    }
    experiment(
        solver            = ProbSAT,
        input_directories = dirs[int(sys.argv[2])],
        output_directory  = sys.argv[3],
        output_file_name  = sys.argv[4],
        poolsize          = int(sys.argv[5]),
        # logstream         = sys.stderr,
        prob              = 1,
        verbose           = False,
        timeLimit         = int(sys.argv[6])
    )
