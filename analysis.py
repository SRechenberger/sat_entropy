import csv

def group_by(data, group_key, *keys, combine_by=None, reduce_by=None):
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

        # if the key is already in the dict
        if group_value in to_return:
            # append it to the list of lines
            to_return[group_value].append(temp)
        # otherwise
        else:
            # initialize the a new list
            to_return[group_value] = [temp]

    return to_return



def load_data(csv_file, default_parser=float, parsers=dict()):
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


    return to_return


def bool_parser(true_value, false_value):
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







# if __name__ == '__main__':

