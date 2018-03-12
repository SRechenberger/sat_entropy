import csv
from collections import Iterable

def group_by(data,
             group_key,
             *keys,
             represented_by=lambda x:x,
             combine_by=None,
             reduce_by=None):
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
    for line in data:
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
            temp = combine_by(temp)

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






# if __name__ == '__main__':


