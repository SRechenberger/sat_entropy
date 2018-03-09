import csv
class Table:

    def __init__(self, filename, columns):
        self.table = Table.read_table_from_csv(filename, columns)

    def select(
        self,
        *keys,
        where       = lambda line:True,
        reduce_with = lambda x: x
    ):
        cols = {}
        for line in self.table:
            if where(line):
                for key in keys:
                    if key in cols:
                        cols[key].append(line[key])
                    else:
                        cols[key] = [line[key]]

        return reduce_with(cols)


    def read_table_from_csv(filename, columns):
        tmp = []
        with open(filename,'r') as f:
            for row in csv.DictReader(f):
                tmp.append({})
                for k,t in columns.items():
                    tmp[-1][k] = t(row[k])

        return tmp
