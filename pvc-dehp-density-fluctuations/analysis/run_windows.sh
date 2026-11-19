#!/bin/bash
XTC=${1:-new_annealing.xtc}
TPR=${2:-anneal_40.tpr}
for Tc in 590 570 550 530 510 490 470 450 430 410 390 370 350 330 310; do
  b=$(( (600 - (Tc + 10)) * 1000 / 6 ))
  e=$(( (600 - (Tc - 10)) * 1000 / 6 ))
  gmx msd -f "$XTC" -s "$TPR" -mol -sel "group DEHP" -b $b -e $e -o msd_T${Tc}.xvg > /dev/null 2>&1
  echo "T = ${Tc} K   window ${b}-${e} ps   done"
done
