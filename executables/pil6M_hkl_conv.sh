#!/bin/sh

set -e 
#set -x

# https://stackoverflow.com/questions/68162603/how-to-prevent-conda-activate-calls-inside-a-bash-script-to-take-arguments-fro
# prevent conda from picking up the arguments to the script
# if you need, store the current positional params
args=("$@")
# clear the params
set --

#source /nfs/chess/sw/anaconda3_jpcr/bin/activate
source /nfs/chess/user/kvahi/software/conda/etc/profile.d/conda.sh
conda activate qmb


#set -x
python /nfs/chess/user/kvahi/work/chess-qmb-workflow/code/Pil6M_HKLConv_3D_2023.py ${args[@]}
