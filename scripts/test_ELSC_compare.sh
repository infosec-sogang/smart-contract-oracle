#!/bin/bash

SCRIPTDIR=$(dirname $0)
OUTDIR=$(realpath $SCRIPTDIR/../output)
EXP_NAME="result-ELSC-compare"

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <iterN>"
    exit
fi

if ls $OUTDIR/$EXP_NAME 1> /dev/null 2>&1; then
    echo "$OUTDIR/$EXP_NAME exists, please remove it."
    exit 1
fi

# Run IConFuzz, Smartian, SmarTest, and rlf.
python $SCRIPTDIR/run_experiment.py B-ELSC Smartian 7200 $1 $OUTDIR $EXP_NAME
python $SCRIPTDIR/run_experiment.py B-ELSC SmarTest 7200 $1 $OUTDIR $EXP_NAME
python $SCRIPTDIR/run_experiment.py B-ELSC rlf 7200 $1 $OUTDIR $EXP_NAME
python $SCRIPTDIR/run_experiment.py B-ELSC Smartian-SmarTest 7200 $1 $OUTDIR $EXP_NAME
python $SCRIPTDIR/run_experiment.py B-ELSC Smartian-rlf 7200 $1 $OUTDIR $EXP_NAME
python $SCRIPTDIR/run_experiment.py B-ELSC SmarTest-Smartian 7200 $1 $OUTDIR $EXP_NAME
python $SCRIPTDIR/run_experiment.py B-ELSC rlf-Smartian 7200 $1 $OUTDIR $EXP_NAME
