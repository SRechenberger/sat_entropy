#!/bin/bash
#MSUB -l nodes=1:ppn=16
#MSUB -l walltime=12:00:00
#MSUB -l pmem=2000mb
#MSUB -N 3sat-early-restart
#MSUB -o 3sat-early-restart.out
#MSUB -M sascha.rechenberger@uni-ulm.de
#MSUB -m bea
#MSUB -q singlenode

module load devel/python/3.5.2

python \
  $WORK/sat_entropy/main.py \
  $WORK/formulae/ \
  310041 \
  $WORK/output/experiment3SAT-early-restart \
  output \
  16 \
  30 \
  0 5 \
  100 \
  0.6 0.8
