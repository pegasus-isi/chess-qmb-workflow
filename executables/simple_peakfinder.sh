#!/bin/bash

set -e 
#set -x

# https://stackoverflow.com/questions/68162603/how-to-prevent-conda-activate-calls-inside-a-bash-script-to-take-arguments-fro
# prevent conda from picking up the arguments to the script
# if you need, store the current positional params
args=("$@")
# clear the params
set --

#source /nfs/chess/sw/anaconda3_jpcr/bin/activate

QMB_CODE=/nfs/chess/user/kvahi/work/chess-qmb-workflow/code
# ensure we source the right conda install
if [ "X${CONTAINER_EXEC}" = "X" ]; then
    # source from the shared fs
    source /nfs/chess/user/kvahi/software/conda/etc/profile.d/conda.sh
else
    # source from inside the container
    source /opt/conda/etc/profile.d/conda.sh
    QMB_CODE=/opt/qmb-code
fi

conda activate qmb

#set -x
python ${QMB_CODE}/simple_peakfinder.py ${args[@]}
