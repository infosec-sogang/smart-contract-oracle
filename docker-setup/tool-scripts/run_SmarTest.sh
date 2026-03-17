#!/bin/bash

# Arg1 : Tool name
# Arg2 : Time limit
# Arg3 : Source file
# Arg4 : Bytecode file
# Arg5 : ABI file
# Arg6 : Main contract name
# Arg7, Arg8, Arg9, Arg10 : Optional argument to pass

OUTDIR=/home/test/output
TOOLDIR=/home/test/tools/$1
WORKDIR=/home/test/SmarTest-workspace

# Set up workdir
mkdir -p $WORKDIR
# Set up environment
mkdir -p $WORKDIR/output
mkdir -p $WORKDIR/output/bugs
touch $WORKDIR/output/log.txt

cd $TOOLDIR
eval $(opam env)
./build
# Run SmarTest
$TOOLDIR/main.native -input $3 -main $6 -mode exploit -exploit_timeout $2 $7 $8 $9 ${10} \
  > $WORKDIR/output/stdout.txt 2>&1

python3 /home/test/scripts/SmarTest_postprocess.py

mv $WORKDIR/output $OUTDIR