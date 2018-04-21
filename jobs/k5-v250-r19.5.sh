#!/bin/bash
#MSUB -l nodes=1:ppn=16
#MSUB -l walltime=5:00:00
#MSUB -l pmem=2000mb
#MSUB -N k5-v250-r19.5
#MSUB -o k5-v250-r19.5.out
#MSUB -M sascha.rechenberger@uni-ulm.de
#MSUB -m bea
#MSUB -q singlenode

module load devel/python/3.5.2

python main.py k5-v250-r19.5 --input_root $WORK/formulae --output_root $WORK/sat_experiment_data --poolsize 16 --repeat 20
