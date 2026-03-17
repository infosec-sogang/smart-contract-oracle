#!/bin/bash

# Arg1 : Tool name
# Arg2 : Time limit
# Arg3 : Source file
# Arg4 : Bytecode file
# Arg5 : ABI file
# Arg6 : Main contract name
# Arg7 : Optional argument to pass

OUTDIR=/home/test/output
TOOLDIR=/home/test/tools/$1

mkdir -p $OUTDIR
dotnet /home/test/tools/Smartian/build/Smartian.dll fuzz \
  --useothersoracle -t $2 -p $4 -a $5 -v 1 $7 -o $OUTDIR --initether 1000000000000000000 \
  > $OUTDIR/log.txt 2>&1
