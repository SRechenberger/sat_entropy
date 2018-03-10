#!/bin/bash
#MSUB -l nodes=1:ppn=16
#MSUB -l walltime=24:00:00
#MSUB -l pmem=2000mb
#MSUB -N 5sat
#MSUB -o 5sat.out
#MSUB -M sascha.rechenberger@uni-ulm.de
#MSUB -m bea
#MSUB -q singlenode

module load devel/python/3.5.2

python $WORK/sat_entropy/main.py $WORK/formulae/ 5 $WORK/output/experiment5SAT output 16 60
