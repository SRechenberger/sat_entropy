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
            lookBack = list(map(lambda f: f*500, range(1,10))),
            minEntropyF = float_range_list(0.8,0.85,0.01),
            timeLimit = 20,
        )
    ),
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
            lookBack = list(map(lambda f: f*500, range(1,10))),
            minEntropyF = float_range_list(0.8,1.0,0.01),
            timeLimit = 20,
        )
    ),
    'k3-v10-r4.0-er': dict(
        dirs   = ['unif-k3-r4.0-v10-c40'],
        solver = ProbSAT,
        prob   = 2,
        config = dict(
            maxFlips = 50 * 10,
            lookBack = list(map(lambda f: f*10, range(2,10))),
            minEntropyF = float_range_list(0.8,1.0,0.01),
            timeLimit = 20,
        )
    ),
    'k3-v500-r4.2-cb0-cb10': dict(
        dirs   = ['unif-k3-r4.2-v500-c2100'],
        solver = ProbSAT,
        prob   = 500,
        config = dict(
            maxFlips  = 50 * 500,
            cb        = float_range_list(0,5,0.1),
            timeLimit = 20
        ),
    ),
    'k3-v500-r4.1-cb0-cb10': dict(
        dirs   = ['unif-k3-r4.1-v500-c2050'],
        solver = ProbSAT,
        prob   = 500,
        config = dict(
            maxFlips  = 50 * 500,
            cb        = float_range_list(0,5,0.1),
            timeLimit = 20
        ),
    ),
    'k3-v500-r4.0-cb0-cb10': dict(
        dirs   = ['unif-k3-r4.0-v500-c2000'],
        solver = ProbSAT,
        prob   = 500,
        config = dict(
            maxFlips  = 50 * 500,
            cb        = float_range_list(0,5,0.1),
            timeLimit = 20
        ),
    ),
    'k5-v250-r20': dict(
        dirs   = ['unif-k5-r20.0-v250-c5000'],
        solver = ProbSAT,
        prob   = 500,
        config = dict(
            maxFlips  = 50 * 250,
            cb        = float_range_list(0, 10, 0.1),
            timeLimit = 20,
        ),
    ),
    'k5-v250-r19.5': dict(
        dirs   = ['unif-k5-r19.5-v250-c4875'],
        solver = ProbSAT,
        prob   = 500,
        config = dict(
            maxFlips  = 50 * 250,
            cb        = float_range_list(0, 10, 0.1),
            timeLimit = 20,
        ),
    ),
}

short_cut = {i:k for k,i in zip(experiments.keys(), range(0,len(experiments)))}

