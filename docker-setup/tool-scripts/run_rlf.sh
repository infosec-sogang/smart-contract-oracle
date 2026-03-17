#!/bin/bash

# Arg1 : Tool name
# Arg2 : Time limit
# Arg3 : Source file
# Arg4 : Bytecode file
# Arg5 : ABI file
# Arg6 : Main contract name
# Arg7 : Optional argument to pass

TOOLDIR=/home/test/tools/$1/go/src/rlf
WORKDIR=/home/test/rlf-workspace
OUTDIR=/home/test/output

source /home/test/tools/rlf/venv/bin/activate

# Set up workdir
mkdir -p $WORKDIR
mkdir -p $WORKDIR/output
touch $WORKDIR/output/log.txt
# Preprocess
python3 /home/test/tools/rlf/preprocess/rlf_preprocess.py --source $3 --name $6 --proj $WORKDIR/proj --rlf $TOOLDIR
# Run rlf
cd $TOOLDIR
timeout $2s python3 -m rlf --proj $WORKDIR/proj --output_path $WORKDIR/output \
  --contract $6 --fuzzer reinforcement --limit 2000 --limit_time $2 --detect_bugs all > \
  $WORKDIR/output/stdout.txt 2>&1

mkdir -p $OUTDIR
# Move raw tc
mkdir -p $OUTDIR/raw_tc
mkdir -p $OUTDIR/raw_misc
cp $WORKDIR/output/tc_* $OUTDIR/raw_tc/
cp $WORKDIR/proj/build/contracts/*.json $OUTDIR/raw_misc/

# Move logs
mv $WORKDIR/output/log.txt $OUTDIR/log.txt
mv $WORKDIR/output/stdout.txt $OUTDIR/stdout.txt

# Move output
mv $WORKDIR/output $OUTDIR/testcase

deactivate