#!/bin/bash
#MSUB -l nodes=1:ppn=16
#MSUB -l walltime=3:00:00
#MSUB -l pmem=2000mb
#MSUB -N k3-v500-r4.2-er
#MSUB -o k3-v500-r4.2-er.out
#MSUB -M sascha.rechenberger@uni-ulm.de
#MSUB -m bea
#MSUB -q singlenode

module load devel/python/3.5.2

python main.py k3-v500-r4.2-er --input_root $WORK/formulae --output_root data --poolsize 16 --repeat 10
