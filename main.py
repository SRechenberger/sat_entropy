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

def experiment1(
    solver                 = None,
    input_directories      = dict(),
    output_directory       = '.',
    output_file_name       = 'output',
    output_file_raw_suffix = 'raw',
    output_file_suffix     = 'csv',
    log_file_suffix        = 'log',
    logstream              = None,
    poolsize               = 1,
    verbose                = False
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

    ## set the template for the raw data output files
    output_file_raw_template = os.path.join(
        output_directory,
        '{}.{}.{}.{}'.format(output_file_name,'{}',output_file_raw_suffix,output_file_suffix)
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
        prob     = 1,
        config   = dict(
            maxTries = 100
        )
    )

    raw = 0
    with open(output_file_path, 'w') as outfile:
        with open(log_file_path, 'w') as logfile:
            # f(vars,ratio,cb) = (medianRuntime, medianEntropy)
            print(
                'k',
                'vars',
                'ratio',
                'cb',
                'medianRuntime',
                'minimalRuntime',
                'maximalRuntime',
                'medianEntropy',
                sep=',',
                file=outfile
            )
            totalBegin = time.time()
            log('BEGIN', [logfile, logstream])

            for (k, vars, ratio), dir in dirs.items():
                dirBegin = time.time()
                log('  BEGIN directory {}'.format(dir), [logfile, logstream])

                for cb in range(0, 20):
                    cbBegin = time.time()
                    log('    BEGIN cb {:.2f}'.format(cb*2 / 10), [logfile, logstream], end='')

                    config['config']['cb'] = cb*2 / 10
                    config['config']['maxFlips'] = 50 * vars

                    exp = Experiment(dir, **config)
                    exp.runExperiment()
                    with open(output_file_raw_template.format(raw), 'w') as fRaw:
                        exp.printResults(
                            outfile=fRaw,
                            label=True,
                        )
                    raw += 1

                    medianRuntime = []
                    medianEntropy = []
                    minimalRuntime = sys.maxsize
                    maximalRuntime = -1

                    for r in exp.results:
                        medianRuntime.append(r['totalFlips'])
                        medianEntropy.append(r['entropy'])
                        if r['totalFlips'] > maximalRuntime:
                            maximalRuntime = r['totalFlips']
                        if r['totalFlips'] < minimalRuntime:
                            minimalRuntime = r['totalFlips']

                    medianRuntime = statistics.median(medianRuntime)
                    medianEntropy = statistics.median(medianEntropy)

                    print(
                        k,
                        r['variables'],
                        r['ratio'],
                        r['cb'],
                        medianRuntime,
                        minimalRuntime,
                        maximalRuntime,
                        medianEntropy,
                        sep = ',',
                        file = outfile
                    )
                    cbEnd = time.time()
                    cbTime = (cbEnd - cbBegin)
                    log(' ...END cb {} ({:10.0f} sec)'.format(cb/10, cbTime), [logfile, logstream])

                dirEnd = time.time()
                dirTime = (dirEnd - dirBegin)
                log('  END dir {} ({:10.0f} sec)'.format(dir, dirTime), [logfile, logstream])

            totalEnd = time.time()
            totalTime = (totalEnd - totalBegin)
            log('END ({:10.0f} sec)'.format(totalTime), [logfile, logstream])




if __name__ == '__main__':
    root = sys.argv[1]
    dirs = {
    #   (3, 10, 4.0): os.path.join(root,'unif-k3-r4.0-v10-c40'),
    #   (3, 10, 4.1): os.path.join(root,'unif-k3-r4.1-v10-c41'),
    #   (3, 10, 4.2): os.path.join(root,'unif-k3-r4.2-v10-c42')
    #   (3, 500, 4.0): os.path.join(root,'unif-k3-r4.0-v500-c2000'),
    #   (3, 500, 4.1): os.path.join(root,'unif-k3-r4.1-v500-c2050'),
    #   (3, 500, 4.2): os.path.join(root,'unif-k3-r4.2-v500-c2100')
       (3, 1000, 4.0): os.path.join(root,'unif-k3-r4.0-v1000-c4000'),
       (3, 1000, 4.1): os.path.join(root,'unif-k3-r4.1-v1000-c4100'),
       (3, 1000, 4.2): os.path.join(root,'unif-k3-r4.2-v1000-c4200'),
       (3, 1000, 4.26): os.path.join(root,'unif-k3-r4.26-v1000-c4260')
    }
    experiment1(
        solver            = ProbSAT,
        input_directories = dirs,
        output_directory  = sys.argv[2],
        output_file_name  = sys.argv[3],
        poolsize          = int(sys.argv[4]),
        logstream         = sys.stderr,
        verbose           = False
    )
