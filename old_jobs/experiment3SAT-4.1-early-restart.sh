#!/bin/bash
#MSUB -l nodes=1:ppn=16
#MSUB -l walltime=2:00:00
#MSUB -l pmem=2000mb
#MSUB -N 3sat-v100-r4.1-early-restart
#MSUB -o 3sat-v100-r4.1-early-restart.out
#MSUB -M sascha.rechenberger@uni-ulm.de
#MSUB -m bea
#MSUB -q singlenode

module load devel/python/3.5.2

python \
  $WORK/sat_entropy/main.py \
  $WORK/formulae/ \
  310041 \
  $WORK/output/experiment3SAT-v100-r4.1-early-restart \
  output \
  16 \
  10 \
  2.3 2.3 \
  500 \
  0.6 0.8
