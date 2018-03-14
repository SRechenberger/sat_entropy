from sat.prob_sat import ProbSAT

def float_range_list(begin, end, step):
    factor = 1
    while (step * factor) % 1 > 0:
        factor *= 10

    return list(
        map(
            lambda x: x/factor,
            range(
                int(begin*factor),
                int(end*factor),
                int(step*factor)
            )
        )
    )



experiments = {
    'k3-v20': dict(
        dirs   = [
            'unif-k3-r4.0-v20-c80',
            'unif-k3-r4.1-v20-c82'
        ],
        solver = ProbSAT,
        prob   = 10,
        config = dict(
            cb = float_range_list(2,3,0.1),
            maxFlips = 50 * 20,
            timeLimit = 10
        )
    ),
    'k3-v500-r4.1': dict(
        dirs   = ['unif-k3-r4.1-v500-c2050'],
        solver = ProbSAT,
        prob   = 500,
        config = dict(
            maxFlips = 50 * 500,
            timeLimit = 20
        )
    ),
    'k3-v500-r4.1-er': dict(
        dirs   = ['unif-k3-r4.1-v500-c2050'],
        solver = ProbSAT,
        prob   = 500,
        config = dict(
            maxFlips = 50 * 500,
            lookBack = list(map(lambda f: f*500, range(1,3))),
            minEntropyF = float_range_list(0.1,0.3,0.05),
            timeLimit = 20,
        )
    )
    'k3-v500-r4.2': dict(
        dirs   = ['unif-k3-r4.2-v500-c2100'],
        solver = ProbSAT,
        prob   = 500,
        config = dict(
            maxFlips = 50 * 500,
            timeLimit = 20
        )
    ),
    'k3-v500-r4.2-er': dict(
        dirs   = ['unif-k3-r4.2-v500-c2100'],
        solver = ProbSAT,
        prob   = 500,
        config = dict(
            maxFlips = 50 * 500,
            lookBack = list(map(lambda f: f*500, range(1,3))),
            minEntropyF = float_range_list(0.1,0.3,0.05),
            timeLimit = 20,
        )
    )
}

short_cut = {i:k for k,i in zip(experiments.keys(), range(0,len(experiments)))}

