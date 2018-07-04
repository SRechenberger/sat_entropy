#!/usr/bin/python

from sat.experiment import *
from sat.prob_sat import *
import sys
import os
import time
import io
import sqlite3

from experiments import experiments, short_cut


make_experiment = """
CREATE TABLE IF NOT EXISTS experiment
    ( id              INTEGER PRIMARY KEY
    , experiment_name TEXT
    )
"""

save_experiment = """
INSERT INTO experiment
    ( experiment_name )
VALUES
    (?)
"""

make_algorithm_run = """
CREATE TABLE IF NOT EXISTS algorithm_run
    ( id            INTEGER PRIMARY KEY
    , experiment_id INTEGER
    , solver        TEXT
    , formula_fname TEXT
    , max_clause_len    INTEGER
    , variables     INTEGER
    , clauses       INTEGER
    , cb            REAL
    , time          INTEGER
    , sat           BOOL
    , FOREIGN KEY(experiment_id) REFERENCES experiment(id)
    )
"""

save_algorithm_run = """
INSERT INTO algorithm_run
    ( experiment_id
    , solver
    , formula_fname
    , max_clause_len
    , variables
    , clauses
    , cb
    , time
    , sat
    )
VALUES
    (?,?,?,?,?,?,?,?,?)
"""

make_search_run = """
CREATE TABLE IF NOT EXISTS search_run
    ( id               INTEGER PRIMARY KEY
    , algorithm_run_id INTEGER
    , flips            INTEGER
    , minimal_unsat    INTEGER
    , last_unsat       INTEGER
    , h_1              REAL
    , h_2              REAL
    , FOREIGN KEY(algorithm_run_id) REFERENCES algorithm_run(id)
    )
"""

save_search_run = """
INSERT INTO search_run
    ( algorithm_run_id
    , flips
    , minimal_unsat
    , last_unsat
    , h_1
    , h_2
    )
VALUES
    (?,?,?,?,?,?)
"""

make_dist_1 = """
CREATE TABLE IF NOT EXISTS dist_1
    ( id        INTEGER PRIMARY KEY
    , run_id    INTEGER
    , label     TEXT
    , variable  INTEGER
    , measure   REAL
    , FOREIGN KEY(run_id) REFERENCES search_run(id)
    )
"""

save_dist_1 = """
INSERT INTO dist_1
    ( run_id
    , label
    , variable
    , measure
    )
VALUES
    (?, ?, ?, ?)
"""

make_dist_2 = """
CREATE TABLE IF NOT EXISTS dist_2
    ( id         INTEGER PRIMARY KEY
    , run_id     INTEGER
    , label      TEXT
    , variable_1 INTEGER
    , variable_2 INTEGER
    , measure    REAL
    , FOREIGN KEY(run_id) REFERENCES search_run(id)
    )
"""

save_dist_2 = """
INSERT INTO dist_2
    ( run_id
    , label
    , variable_1
    , variable_2
    , measure
    )
VALUES
    (?,?,?,?,?)
"""

def eval_dist(dist):
    s = sum([c for _,c in dist.items()])
    probs = {k: c/s for k,c in dist.items()}
    h = lambda p: -math.log(p) * p
    entropies = {k:h(p) for k,p in probs.items()}
    max_h = max(entropies, key = entropies.get)
    min_h = min(entropies, key = entropies.get)
    max_p = max(probs, key = probs.get)
    min_p = min(probs, key = probs.get)
    h = sum(entropies.values())

    return (
        h,
        {
            'max_h': (max_h, entropies[max_h]),
            'min_h': (min_h, entropies[min_h]),
            'max_p': (max_p, probs[max_p]),
            'min_p': (min_p, probs[min_p])
        }
    )

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
    outfile_path = '{}.db'.format(experiment_name)
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
        c.execute(make_experiment)
        c.execute(make_algorithm_run)
        c.execute(make_search_run)
        c.execute(make_dist_1)
        c.execute(make_dist_2)

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
            c.execute(save_experiment, (experiment_name,))
            exp_id = c.lastrowid
            for result in exp.results:
                c.execute(
                    save_algorithm_run,
                    (
                        exp_id,
                        "probSAT",
                        result['formula_fname'],
                        result['max_clause_len'],
                        result['variables'],
                        result['clauses'],
                        result['cb'],
                        result['time'],
                        result['sat'],
                    )
                )
                alg_id = c.lastrowid
                for run in result['runs']:

                    h_1, ms_1 = eval_dist(run['dist_1'])
                    h_2, ms_2 = eval_dist(run['dist_2'])

                    c.execute(
                        save_search_run,
                        (
                            alg_id,
                            run['flips'],
                            run['minimal_unsat'],
                            run['last_unsat'],
                            h_1,
                            h_2,
                        ),
                    )

                    run_id = c.lastrowid
                    for lbl, (var, measure) in ms_1.items():
                        c.execute(
                            save_dist_1,
                            (
                                run_id,
                                lbl,
                                var,
                                measure,
                            )
                        )
                    for lbl, ((var_1, var_2), measure) in ms_2.items():
                        c.execute(
                            save_dist_2,
                            (
                                run_id,
                                lbl,
                                var_1,
                                var_2,
                                measure,
                            )
                        )

            conn.commit()

            # Repeat
            i += 1

    sys.exit(0)
