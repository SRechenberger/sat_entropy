#!/bin/bash
#MSUB -l nodes=1:ppn=16
#MSUB -l walltime=5:00:00
#MSUB -l pmem=2000mb
#MSUB -N 3sat-cb-2-3
#MSUB -o 3sat-cb-2-3.out
#MSUB -M sascha.rechenberger@uni-ulm.de
#MSUB -m bea
#MSUB -q singlenode

module load devel/python/3.5.2

python \
  $WORK/sat_entropy/main.py \
  $WORK/formulae/ \
  3 \
  $WORK/output/experiment3SAT-cb-2-3 \
  output \
  16 \
  30 \
  2 3
