#!/usr/bin/python

import os
import statistics as stat
import matplotlib
import matplotlib.pyplot as plot
import seaborn
import sqlite3
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
\maketitle
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
    return len(set(x for seq in seqs for x in seq))

def fetch_axes(db_conn, query, *args):
    """ Executes a query in the database db_conn, given also the arguments
    args, and returns the data as axes """
    return list(zip(*db_conn.cursor().execute(query, args)))

if __name__ == '__main__':
    with sqlite3.connect('data/k3-v500-r4.1.raw.db') as db:
        x, = fetch_axes(
            db,
            #'SELECT algorithm_run.id, COUNT(search_run.id) FROM algorithm_run JOIN search_run ON algorithm_run.id = search_run.algorithm_run_id GROUP BY algorithm_run.id'
            'SELECT id FROM algorithm_run WHERE sat = 0',
        )
        #seaborn.distplot(y)
        print(x)
