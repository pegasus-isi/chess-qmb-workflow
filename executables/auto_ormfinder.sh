#!/bin/sh

set -e 
#set -x

# https://stackoverflow.com/questions/68162603/how-to-prevent-conda-activate-calls-inside-a-bash-script-to-take-arguments-fro
# prevent conda from picking up the arguments to the script
# if you need, store the current positional params
args=("$@")
# clear the params
set --

source /nfs/chess/sw/anaconda3_jpcr/bin/activate

#set -x
python /nfs/chess/user/kvahi/work/chess-qmb-workflow/code/auto_ormfinder.py  ${args[@]}
