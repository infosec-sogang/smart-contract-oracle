#!/bin/bash
set -e

RLF_SMARTIAN_GOPATH=/home/test/tools/rlf-Smartian/go

python3 -m venv /home/test/tools/rlf-Smartian/venv
. /home/test/tools/rlf-Smartian/venv/bin/activate

mkdir -p $RLF_SMARTIAN_GOPATH/src
cd $RLF_SMARTIAN_GOPATH/src
git clone https://github.com/Demonhero0/rlf.git
cd $RLF_SMARTIAN_GOPATH/src/rlf
git checkout 840ff37d9046511bd0806a0085abfa499aa37520
patch -p1 < ../rlf-Smartian.patch

mkdir -p $RLF_SMARTIAN_GOPATH/src/github.com/ethereum
cd $RLF_SMARTIAN_GOPATH/src/github.com/ethereum
git clone https://github.com/ethereum/go-ethereum.git
cd $RLF_SMARTIAN_GOPATH/src/github.com/ethereum/go-ethereum
git checkout 86be91b3e2dff5df28ee53c59df1ecfe9f97e007
git apply $RLF_SMARTIAN_GOPATH/src/rlf/script/patch.geth

cd $RLF_SMARTIAN_GOPATH/src/rlf
python3 -m pip install --upgrade pip setuptools
python3 -m pip install -r $RLF_SMARTIAN_GOPATH/src/rlf/requirements.txt

GOPATH=$RLF_SMARTIAN_GOPATH go build -o execution.so -buildmode=c-shared $RLF_SMARTIAN_GOPATH/src/rlf/export/execution.go

deactivate
