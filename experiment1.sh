#!/bin/bash
#MSUB -l nodes=1:ppn=16
#MSUB -l walltime=3:00:00
#MSUB -l pmem=2000mb
#MSUB -N 3sat
#MSUB -M sascha.rechenberger@uni-ulm.de
#MSUB -m bea
#MSUB -q singlenode

module load devel/python/3.5.2

python $WORK/sat_entropy/main.py $WORK/formulae/ $WORK/output/experiment1 output 16
