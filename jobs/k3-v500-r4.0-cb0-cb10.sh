#!/bin/bash
#MSUB -l nodes=1:ppn=16
#MSUB -l walltime=5:00:00
#MSUB -l pmem=2000mb
#MSUB -N k3-v500-r4.2-cb0-cb10
#MSUB -o k3-v500-r4.2-cb0-cb10.out
#MSUB -M sascha.rechenberger@uni-ulm.de
#MSUB -m bea
#MSUB -q singlenode

module load devel/python/3.5.2

python main.py k3-v500-r4.0-cb0-cb10 --input_root $WORK/formulae --output_root $WORK/sat_experiment_data --poolsize 16 --repeat 20
