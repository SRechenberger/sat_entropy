#!/usr/bin/python

import csv
import os
import statistics as stat
import matplotlib.pyplot as plot
from matplotlib import rc
from collections import Iterable
from functools import reduce

rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
rc('text', usetex=True)

document_template = r"""
\documentclass[a4paper]{{scrartcl}}
\usepackage[a4paper, left=2cm, right=1.5cm, top=0.5cm, bottom=0.5cm]{{geometry}}
\usepackage{{graphicx}}
\title{{{}}}
\begin{{document}}
{}
\end{{document}}
"""

section_template = r"""
\section{{{}}}
\includegraphics[width=1\textwidth]{{{}}}
"""

plot_template = r"""
\includegraphics[width=1\textwidth]{{{}}}
"""


lbls=dict(
    h=r'$\frac{H}{H_{max}}$',
    cb=r'$c_b$',
    t=r'$t$',
    er=r'$early restarts$'
)

def count_different_values(*seqs):
    s = set()
    for seq in seqs:
        for x in seq:
            s.add(x)
    return len(s)

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



def make_axes(data, *keys, where=None, represented_by=lambda x:x):
    axes = {key:[] for key in keys}
    for line in data:
        if not where or where(line):
            for k in keys:
                axes[k].append(represented_by(line[k]))

    return axes



def extract_columns(data, *keys, where=None):
    to_return = []
    for line in data:
        if not where or where(line):
            tmp = {}
            for key in keys:
                tmp[key] = line[key]
            to_return.append(tmp)

    return to_return


def sort_data_by_key(data, key, reverse=False):
    data.sort(key=lambda line: line[key], reverse=reverse)


def plot_cb_to_entropy(data, ax):
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
    ax.legend(['runtime', 'mean runtime'])
    ax.set(xlabel=lbls['cb'], ylabel=lbls['h'])


def plot_cb_to_runtime(data, ax):
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

    ax.grid(linestyle='--')
    ax.scatter(
        cb_to_runtime['cb'],
        cb_to_runtime['totalFlips'],
        s=1
    )
    ax.set(xlabel=lbls['cb'], ylabel=lbls['t'])


def plot_entropy_to_solve_ratio(data, ax):
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
            represented_by = lambda entropy: round(entropy, 3),
        ),
        'entropy',
        'ratio',
    )


    ax.grid(linestyle='--')

    ax.scatter(
        entropy_to_sat_count['entropy'],
        entropy_to_sat_count['ratio'],
        color='green',
        s=1
    )
    ax.set(xlabel=lbls['h'], ylabel=r'$\frac{solved}{total}$')


def plot_entropy_to_cases(data, ax):
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
            represented_by = lambda entropy: round(entropy, 3),
        ),
        'entropy',
        'sat',
        'total'
    )


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

    ax.legend(['total','solved'])
    ax.set(xlabel=lbls['h'],ylabel=r'$instances$')



def plot_entropy_to_runtime(data, ax):
    sort_data_by_key(data, 'entropy')
    entropy_to_runtime_stdev = make_grouped_axes(
        group_by(
            data,
            'entropy',
            'totalFlips',
            combine_by='totalFlips',
            reduce_by=stat.pstdev,
            represented_by=lambda entropy: round(entropy,3),
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
            represented_by=lambda entropy: round(entropy,3),
            # where=lambda line: line['sat']
        ),
        'entropy',
        'totalFlips'
    )

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
    ax.set(xlabel=lbls['h'],ylabel=lbls['t'])



def failed_success_entropy(data, ax):
    parser = dict(sat=int)
    processed_data = make_axes(
        data,
        'sat',
        'lastRunEntropy'
    )
    average_data = make_grouped_axes(
        group_by(
            data,
            'sat',
            'lastRunEntropy',
            combine_by='lastRunEntropy',
            reduce_by=stat.mean,
        ),
        'sat',
        'avg_entropy'
    )

    sat = make_axes(
        extract_columns(
            data,
            'lastRunEntropy',
            where=lambda line: line['sat'],
        ),
        'lastRunEntropy'
    )

    unsat = make_axes(
        extract_columns(
            data,
            'lastRunEntropy',
            where=lambda line: not line['sat'],
        ),
        'lastRunEntropy'
    )


    ax.grid(linestyle='--')

    ax.hist(
        [sat['lastRunEntropy'],unsat['lastRunEntropy']],
        count_different_values(
            sat['lastRunEntropy'],
            unsat['lastRunEntropy']
        )//20
    )

    ax.set(xlabel=lbls['h'],
           xlim=[0.4,1])


def successful_run_entropy(data, ax):
    sort_data_by_key(data, 'lastRunEntropy')
    data_scatter = make_axes(
        data,
        'lastRunEntropy',
        'flips',
        where=lambda line: line['sat'],
        # where=lambda line: line['sat'] and 2.3 <= line['cb'] < 2.5,
    )

    data_mean = make_grouped_axes(
        group_by(
            data,
            'lastRunEntropy',
            'flips',
            # where=lambda line: line['sat'] and 2.3 <= line['cb'] < 2.5,
            where=lambda line: line['sat'],
            combine_by='flips',
            reduce_by=stat.mean,
            represented_by=lambda h: round(h,2)
        ),
        'lastRunEntropy',
        'avg_flips'
    )


    ax.grid(linestyle='--')
    ax.scatter(
        data_scatter['lastRunEntropy'],
        data_scatter['flips'],
        s=1
    )
    ax.plot(
        data_mean['lastRunEntropy'],
        data_mean['avg_flips'],
        color='red'
    )
    ax.set(
        xlabel=lbls['h'],
        ylabel=lbls['t'],
        xlim=[0.4,1]
    )


def successful_run_entropy_count(data, ax):

    data_hist=make_axes(
        extract_columns(
            data,
            'lastRunEntropy',
            # where=lambda line: line['sat'] and 2.3 <= line['cb'] < 2.5,
            where=lambda line: line['sat'],
        ),
        'lastRunEntropy',
        represented_by=lambda h:round(h,3),
    )

    ax.grid(linestyle='--')
    ax.hist(
        data_hist['lastRunEntropy'],
        count_different_values(data_hist['lastRunEntropy'])//2,
    )
    ax.set(
        xlabel=lbls['h'],
        ylabel='successful runs',
        xlim=[0.5,1]
    )

def failed_run_entropy_count(data, ax):

    data_hist=make_axes(
        extract_columns(
            data,
            'lastRunEntropy',
            # where=lambda line: line['sat'] and 2.3 <= line['cb'] < 2.5,
            where=lambda line: not line['sat'],
        ),
        'lastRunEntropy',
        represented_by=lambda h:round(h,3),
    )

    ax.grid(linestyle='--')
    ax.hist(
        data_hist['lastRunEntropy'],
        count_different_values(data_hist['lastRunEntropy'])//2,
    )
    ax.set(
        xlabel=lbls['h'],
        ylabel='failed runs',
        xlim=[0.5,1]
    )


def plot_early_restarts_to_runtime(data, ax):
    processed_data = make_grouped_axes(
        group_by(
            data,
            'earlyRestarts',
            'totalFlips',
            combine_by='totalFlips',
            reduce_by = stat.mean,
        ),
        'earlyRestarts',
        'totalFlips',
    )

    ax.grid(linestyle='--')
    ax.scatter(
        processed_data['earlyRestarts'],
        processed_data['totalFlips'],
        s=1
    )
    ax.set(
        xlabel=lbls['er'],
        ylabel=lbls['t']
    )


def plot_early_restarts_to_entropy(data, ax):
    processed_data = make_grouped_axes(
        group_by(
            data,
            'earlyRestarts',
            'entropy',
            combine_by='entropy',
            reduce_by = stat.mean,
        ),
        'earlyRestarts',
        'entropy',
    )

    ax.grid(linestyle='--')
    ax.scatter(
        processed_data['earlyRestarts'],
        processed_data['entropy'],
        s=1
    )
    ax.set(
        xlabel=lbls['er'],
        ylabel=lbls['h']
    )

def full_analysis(data_folder, experiment_name, *analyses):
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

    sections = ""
    for analysis in analyses:
        plotted_file = '{}.pdf'.format(analysis['name'])
        sections += section_template.format(analysis['name'], plotted_file)
        output_file = os.path.join(output_folder, plotted_file)

        fig, axarr = plot.subplots(len(analysis['plots']), sharex=True)
        lbl=''
        for i,f in enumerate(analysis['plots']):
            ax = axarr[i] if len(analysis['plots']) > 1 else axarr
            f(data, ax)
            lbl = ax.get_xlabel()
            ax.set_xlabel('')

        ax.set_xlabel(lbl)
        fig.savefig(output_file)

    document = document_template(experiment_name, sections)
    tex_file = os.path.join(
        output_folder,
        '{}.tex'.format(experiment_name)
    )
    with open(tex_file, 'w') as f:
        print(
            document,
            file=f
        )


if __name__ == '__main__':
    analyses_cb = dict(
        name='cb',
        plots=[
            plot_cb_to_entropy,
            plot_cb_to_runtime,
        ]
    )

    analyses_entropy = dict(
        name='entropy',
        plots=[
            plot_entropy_to_runtime,
            plot_entropy_to_cases,
            plot_entropy_to_solve_ratio
        ]
    )

    analyses_last_run = dict(
        name='last_run',
        plots=[
            successful_run_entropy,
            successful_run_entropy_count,
            failed_run_entropy_count

        ]
    )

    analyses_sat = dict(
        name='sat',
        plots=[
            failed_success_entropy,
        ]
    )

    analyses_early_restart = dict(
        name='er_to_avg_t',
        plots=[
            plot_early_restarts_to_entropy,
            plot_early_restarts_to_runtime
        ]
    )

    experiments = [
        'k3-r4.0-r4.2-v500-cb2-cb3-quick',
        'k3-r4.0-r4.2-v500-cb2-cb3',
        'k3-v500-r4.1',
    ]

    experiments_er = [
        'k3-v500-r4.1-er',
    ]

    data_folder = 'data'

    for experiment in experiments:
        full_analysis(
            data_folder,
            experiment,
            analyses_entropy,
            analyses_sat,
            analyses_last_run
        )
    for experiment in experiments_er:
        full_analysis(
            data_folder,
            experiment,
            analyses_entropy,
            analyses_sat,
            analyses_last_run,
            analyses_early_restart
        )

