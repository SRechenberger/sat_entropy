#!/usr/bin/python

from sat.experiment import *
from sat.prob_sat import *
import sys
import os
import time
import io
import sqlite3

from experiments import experiments, short_cut

make_algorithm_run = """
CREATE TABLE IF NOT EXISTS algorithm_run
    ( id            INTEGER PRIMARY KEY
    , solver        TEXT
    , clause_len    INTEGER
    , variables     INTEGER
    , clauses       INTEGER
    , cb            REAL
    , lookback      INTEGER
    , min_entropy   REAL
    , sat           BOOL
    )
"""

make_search_run = """
CREATE TABLE IF NOT EXISTS search_run
    ( id               INTEGER PRIMARY KEY
    , algorithm_run_id INTEGER
    , early_restart    BOOL
    , FOREIGN KEY(algorithm_run_id) REFERENCES algorithm_run(id)
    )
"""

make_search_step = """
CREATE TABLE IF NOT EXISTS search_step
    ( id            INTEGER PRIMARY KEY
    , search_run_id INTEGER
    , estim_entropy REAL
    , hamming_dist  INTEGER
    , unsat         INTEGER
    , flipped       INTEGER
    , FOREIGN KEY(search_run_id) REFERENCES search_run(id)
    )
"""

save_algorithm_run = """
INSERT INTO algorithm_run
    ( solver
    , clause_len
    , variables
    , clauses
    , cb
    , lookback
    , min_entropy
    , sat
    )
VALUES
    (?,?,?,?,?,?,?,?)
"""

save_search_run = """
INSERT INTO search_run
    ( algorithm_run_id
    , early_restart
    )
VALUES
    (?,?)
"""

save_search_step = """
INSERT INTO search_step
    ( search_run_id
    , estim_entropy
    , hamming_dist
    , unsat
    , flipped
    )
VALUES
    (?,?,?,?,?)
"""

if __name__ == '__main__':
    # Parse arguments
    if len(sys.argv) <= 1:
        print(
            'Error: You need at least the experiments name.',
            file=sys.stderr
        )
        sys.exit(1)

    ## Default values
    try:
        experiment_name = short_cut[int(sys.argv[1])]
    except ValueError:
        experiment_name = sys.argv[1]
    except Exception as e:
        print(
            'Error: While fetching the experiments name: {}.'
            .format(e),
            file=sys.stderr
        )
        sys.exit(1)

    repeat = 1
    outfile_path = '{}.raw.json'.format(experiment_name)
    poolsize = 1
    input_root = ''
    output_root = ''

    ## Loop through arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--repeat':
            i += 1
            try:
                repeat = int(sys.argv[i])
            except ValueError:
                print(
                    'Error: Could not parse \'{}\' into an int.'
                    .format(sys.argv[i]),
                    file=sys.stderr
                )
                sys.exit(1)
        elif sys.argv[i] == '--outfile':
            i += 1
            outfile_path = sys.argv[i]
        elif sys.argv[i] == '--poolsize':
            i += 1
            try:
                poolsize = int(sys.argv[i])
            except ValueError:
                print(
                    'Error: Could not parse \'{}\' into an int.'
                    .format(sys.argv[i]),
                    file=sys.stderr
                )
                sys.exit(1)
        elif sys.argv[i] == '--input_root':
            i += 1
            input_root = sys.argv[i]
        elif sys.argv[i] == '--output_root':
            i += 1
            output_root = sys.argv[i]
        else:
            print(
                'Warning: Unknown flag: {}.'.format(sys.argv[i]),
                file=sys.stderr
            )
        i += 1


    outfile_path = os.path.join(output_root, outfile_path)
    # Running the experiment.
    try:
        experiment = experiments[experiment_name]
    except KeyError:
        print(
            'Error: The experiment \'{}\' was not specified.'
            .format(experiment_name),
            file=sys.stderr
        )
        sys.exit(1)
    except Exception as e:
        print(
            'Error: {}.'
            .format(e),
            file=sys.stderr
        )
        sys.exit(1)


    with sqlite3.connect(outfile_path, timeout=5*60) as conn:
        c = conn.cursor()
        c.execute(make_algorithm_run)
        c.execute(make_search_run)
        c.execute(make_search_step)
        conn.commit()

        total_time = 0
        need_label = True
        i = 0

        while i < repeat:
            # results = []
            # Initialize the experiment.
            try:
                dirs = list(
                    map(
                        lambda d: os.path.join(input_root,d),
                        experiment['dirs']
                    )
                )
                exp = Experiment(
                    directories = dirs,
                    solver = experiment['solver'],
                    prob   = experiment['prob'],
                    config = experiment['config'],
                    poolsize = poolsize,
                )
            except Exception as e:
                print(
                    'Error: While initializing the experiment: {}.'
                    .format(e),
                    file=sys.stderr
                )
                sys.exit(1)

            # Run the experiment.
            try:
                print(
                    'Experiment #{} {}... '.format(i, experiment_name),
                    file=sys.stdout,
                    end='',
                    flush=True
                )
                exp_begin = time.time()
                exp.runExperiment()
                exp_end = time.time()
                exp_dur = exp_end - exp_begin
                print(
                    'done after {:10d} seconds.'.format(int(exp_dur)),
                    file=sys.stdout,
                    end='\n',
                    flush=True
                )
            except ValueError as e:
                print(
                    'Error: While running the experiment: {}.'
                    .format(e),
                    file=sys.stderr
                )
                sys.exit(1)

            # Extract the results
            # results += exp.results


            # Save the results
            # with sqlite3.connect(outfile_path, timeout=5*60) as conn:
            for result in exp.results:
                c.execute(
                    save_algorithm_run,
                    (
                        "probSAT",
                        result['max_clause_len'],
                        result['variables'],
                        result['clauses'],
                        result['cb'],
                        result['lookback'],
                        result['min_entropy'],
                        result['sat'],
                    )
                )
                lastrowid = c.lastrowid
                for run in result['runs']:
                    c.execute(
                        save_search_run,
                        (
                            lastrowid,
                            run['early_restart'],
                        ),
                    )
                    lastrowid2 = c.lastrowid
                    for step in run['steps']:
                        c.execute(
                            save_search_step,
                            (
                                lastrowid2,
                                step['estim_entropy'],
                                step['hamming_dist'],
                                step['unsat'],
                                step['flipped'],
                            ),
                        )
            conn.commit()

            # Repeat
            i += 1

    sys.exit(0)
