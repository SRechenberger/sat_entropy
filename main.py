#!/usr/bin/python

from sat.experiment import *
from sat.prob_sat import *
import sys
import os
import time
import io

from experiments import experiments, short_cut


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
    outfile_path = '{}.csv'.format(experiment_name)
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


    with open(outfile_path, 'w') as outfile:
        # Running the experiment.
        i = 0
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


        total_time = 0
        need_label = True
        while i < repeat:
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


            # Extract and print the results
            try:
                exp.printResults(
                    outfile=outfile,
                    label=need_label
                )
                need_label = False
            except Exception as e:
                print(
                    'Error: While printing the experiments results: {}.'
                    .format(e),
                    file=sys.stderr
                )
                sys.exit(1)

            # Repeat
            i += 1

    outfile.close()
    sys.exit(0)
