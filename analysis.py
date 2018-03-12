import csv
import os
import statistics as stat
import matplotlib.pyplot as plot
from collections import Iterable
from functools import reduce

def group_by(data,
             group_key,
             *keys,
             represented_by=lambda x:x,
             combine_by=None,
             reduce_by=None,
             where=None):
    """ Given a dictionary, group the values designated by the keys
    by the group_key, then combine the values designated by the keys
    with combine_by, if given, and reduce the whole list with reduce_by.

    Example:
        Input:
            a,  b,  c
            1,  2,  3
            1,  4,  5
            2,  6,  7

        group_by(data, 'a', 'b', 'c')
            == dict(
                1: [{'b': 2, 'c': 3}, {'b': 4, 'c': 5}],
                2, [{'b': 6, 'c': 7}]
            )
    """

    # initialize the dict to return
    to_return = {}

    # for each line in the data
    for line in filter(where,data):
        # get the value to group by
        group_value = line[group_key]

        # initialize a temporary new line
        temp = {}
        # for each key to group
        for key in keys:
            # fetch the value in the line,
            # and save it accordingly
            temp[key] = line[key]

        if combine_by:
            if callable(combine_by):
                temp = combine_by(temp)
            elif combine_by in temp:
                temp = temp[combine_by]
            else:
                raise ValueError('Cannot extract anything from temp={} with combine_by={}.'
                                 .format(temp, combine_by))

        # if the key is already in the dict
        if represented_by(group_value) in to_return:
            # append it to the list of lines
            to_return[represented_by(group_value)].append(temp)
        # otherwise
        else:
            # initialize the a new list
            to_return[represented_by(group_value)] = [temp]

    if reduce_by:
        for group_value, values in to_return.items():
            to_return[group_value] = reduce_by(values)

    return to_return



def load_data(csv_file,
              as_axes=False,
              keys=None,
              default_parser=float,
              sort_by=None,
              reverse=False,
              parsers=dict()):
    def convert(value, key):
        if key in parsers:
            return parsers[key](value)
        else:
            return default_parser(value)

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        to_return = list(
            map(
                lambda line: {k: convert(v, k) for k,v in line.items()},
                map(dict, reader)
            )
        )

    if sort_by:
        to_return.sort(
            key=lambda line: line[sort_by],
            reverse=reverse
        )

    if keys:
        to_return = extract_columns(to_return, *keys)

    if as_axes:
        to_return = make_axes(to_return, *to_return[0].keys())

    return to_return



def bool_parser(false_value=0, true_value=1):
    """ Returns a function, mapping two values to either true or false.
    This function raises a ValueError, if the given value matches
    neither of the given values.
    """
    def to_return(value):
        if value == true_value:
            return True
        elif value == false_value:
            return False
        else:
            raise ValueError(
                'value={} is neither true_value={} nor false_value={}.'
                .format(value, true_value, false_value)
            )

    return to_return



def make_grouped_axes(data, key, *keys):
    axes = {key: [], **{k:[] for k in keys}}

    for key_value, values in data.items():
        axes[key].append(key_value)
        if hasattr(values, '__len__') and len(values) != len(keys):
            raise ValueError(
                'len(values)={} does not match len(keys)={}.'
                .format(len(values), len(keys))
            )
        if type(values) == dict:
            for k, v in values.items():
                axes[k].append(v)
        elif isinstance(values, Iterable):
            for (k,v) in zip(keys, values):
                axes[k].append(v)
        elif len(keys) == 1:
            axes[keys[0]].append(values)
        else:
            raise ValueError(
                'What the fuck am I supposed to do with values={} and keys={}?!'
                .format(values, keys)
            )

    return axes



def make_axes(data, *keys):
    axes = {key:[] for key in keys}
    for line in data:
        for k in keys:
            axes[k].append(line[k])

    return axes



def extract_columns(data, *keys):
    to_return = []
    for line in data:
        tmp = {}
        for key in keys:
            tmp[key] = line[key]
        to_return.append(tmp)

    return to_return



def plot_cb_to_entropy(data, filename):
    cb_to_entropy_mean = make_grouped_axes(
        group_by(
            data,
            'cb',
            'entropy',
            combine_by='entropy',
            reduce_by=stat.mean
        ),
        'cb',
        'entropy'
    )

    cb_to_entropy_scatter=make_axes(
        data,
        'cb',
        'entropy'
    )


    fig, ax = plot.subplots()
    ax.grid(linestyle='--')
    ax.scatter(
        cb_to_entropy_scatter['cb'],
        cb_to_entropy_scatter['entropy'],
        color='red',
        s=1
    )
    ax.plot(
        cb_to_entropy_mean['cb'],
        cb_to_entropy_mean['entropy']
    )
    fig.savefig(filename)

def sort_data_by_key(data, key, reverse=False):
    data.sort(key=lambda line: line[key], reverse=reverse)

def plot_cb_to_runtime(data, filename):
    cb_to_runtime = make_grouped_axes(
        group_by(
            data,
            'cb',
            'totalFlips',
            combine_by='totalFlips',
            reduce_by=stat.mean
        ),
        'cb',
        'totalFlips'
    )

    fig, ax = plot.subplots()
    ax.grid(linestyle='--')
    ax.scatter(
        cb_to_runtime['cb'],
        cb_to_runtime['totalFlips'],
        s=1
    )

    fig.savefig(filename)

def plot_entropy_to_solve_ratio(data, filename):
    sort_data_by_key(data, 'entropy')
    def add_dicts(acc, line):
        for k in acc.keys():
            acc[k] += line[k]
        return acc

    entropy_to_sat_count = make_grouped_axes(
        group_by(
            data,
            'entropy',
            'sat',
            combine_by = lambda ls: dict(sat=1, total=1) if ls['sat'] else dict(sat=0, total=1),
            reduce_by = lambda ls: (lambda line: line['sat']/line['total'])(reduce(add_dicts, ls)),
            represented_by = lambda entropy: round(entropy, 2),
        ),
        'entropy',
        'ratio',
    )

    fig, ax = plot.subplots()

    ax.grid(linestyle='--')

    ax.scatter(
        entropy_to_sat_count['entropy'],
        entropy_to_sat_count['ratio'],
        color='green',
        s=1
    )

    fig.savefig(filename)

def plot_entropy_to_cases(data, filename):
    sort_data_by_key(data, 'entropy')
    def add_dicts(acc, line):
        for k in acc.keys():
            acc[k] += line[k]
        return acc

    entropy_to_sat_count = make_grouped_axes(
        group_by(
            data,
            'entropy',
            'sat',
            combine_by = lambda ls: dict(sat=1, total=1) if ls['sat'] else dict(sat=0, total=1),
            reduce_by = lambda ls: reduce(add_dicts, ls),
            represented_by = lambda entropy: round(entropy, 2),
        ),
        'entropy',
        'sat',
        'total'
    )

    fig, ax = plot.subplots()

    ax.grid(linestyle='--')

    ax.scatter(
        entropy_to_sat_count['entropy'],
        entropy_to_sat_count['total'],
        color='red',
        s=1
    )

    ax.scatter(
        entropy_to_sat_count['entropy'],
        entropy_to_sat_count['sat'],
        color='green',
        s=1
    )

    fig.savefig(filename)


def plot_entropy_to_runtime(data, filename):
    sort_data_by_key(data, 'entropy')
    entropy_to_runtime_stdev = make_grouped_axes(
        group_by(
            data,
            'entropy',
            'totalFlips',
            combine_by='totalFlips',
            reduce_by=stat.pstdev,
            represented_by=lambda entropy: round(entropy,2),
            #where=lambda line: line['sat']
        ),
        'entropy',
        'totalFlips'
    )

    entropy_to_runtime_mean = make_grouped_axes(
        group_by(
            data,
            'entropy',
            'totalFlips',
            combine_by='totalFlips',
            reduce_by=stat.mean,
            represented_by=lambda entropy: round(entropy,2),
            where=lambda line: line['sat']
        ),
        'entropy',
        'totalFlips'
    )

    fig, ax = plot.subplots()
    ax.grid(linestyle='--')
    ax.scatter(
        entropy_to_runtime_mean['entropy'],
        entropy_to_runtime_mean['totalFlips'],
        s=1,
    )
    ax.scatter(
        entropy_to_runtime_stdev['entropy'],
        entropy_to_runtime_stdev['totalFlips'],
        s=1,
        color='r',
    )
    ax.legend(['mean runtime', 'standard deviation'])
    ax.set_xlabel('entropy')
    ax.set_ylabel('runtime')

    fig.savefig(filename)


def full_analysis(data_folder, experiment_name, analyses=dict()):
    parsers = dict(sat=bool_parser(false_value='0', true_value='1'))
    data = load_data(
        os.path.join(
            data_folder,
            '{}.raw.csv'.format(experiment_name)
        ),
        parsers=parsers
    )

    output_folder = os.path.join(
        data_folder,
        '{}_plots'.format(experiment_name)
    )

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for name, func in analyses.items():
        plotted_file = '{}.pdf'.format(name)
        output_file = os.path.join(output_folder, plotted_file)
        func(data, output_file)


if __name__ == '__main__':
    analyses = dict(
        cb_to_entropy      = plot_cb_to_entropy,
        cb_to_runtime      = plot_cb_to_runtime,
        entropy_to_runtime = plot_entropy_to_runtime,
        entropy_to_cases   = plot_entropy_to_cases,
        entropy_to_solve_ratio = plot_entropy_to_solve_ratio
    )

    experiments = [
        'k3-r4.0-v1000',
        'k3-r4.2-v1000',
        'k3-r4.0-r4.2-v500-cb2-cb3',
    ]

    data_folder = 'data'

    for experiment in experiments:
        full_analysis(data_folder, experiment, analyses=analyses)

