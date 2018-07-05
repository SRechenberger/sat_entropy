import numpy as np
import math
import sqlite3 as sql

### Calculating entropy
def lb(x):
    return 0 if x == 0 else math.log(x, 2)

def entropy(p):
    return -p * lb(p)

### Maximum likelihood
def log_likelihood(pdf, data):
    f = np.vectorize(lambda x: lb(pdf(x)))
    return sum(f(data))

a4_dims = (11.7, 8.27)

def print_table_schemes(fname, *tables):
    format_template = '  {:20} {:20} {}'
    for table in tables:
        with sql.connect(fname) as conn:
            print('TABLE',table)
            print(format_template.format("NAME","DATA_TYPE","PRIMARY_KEY"))
            for (_,name,data_type,_,_,pk) in conn.cursor().execute('PRAGMA table_info({})'.format(table)):
                print(format_template.format(name, data_type, pk))
            print()


