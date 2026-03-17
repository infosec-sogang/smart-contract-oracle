set -e

python3 -m venv /home/test/tools/rlf/venv
. /home/test/tools/rlf/venv/bin/activate

mkdir -p $GOPATH/src
cd $GOPATH/src
git clone https://github.com/Demonhero0/rlf.git
cd $GOPATH/src/rlf
git checkout 840ff37d9046511bd0806a0085abfa499aa37520
patch -p1 < ../rlf.patch

mkdir -p $GOPATH/src/github.com/ethereum
cd $GOPATH/src/github.com/ethereum
git clone https://github.com/ethereum/go-ethereum.git
cd $GOPATH/src/github.com/ethereum/go-ethereum
git checkout 86be91b3e2dff5df28ee53c59df1ecfe9f97e007
git apply $GOPATH/src/rlf/script/patch.geth

cd $GOPATH/src/rlf
python3 -m pip install --upgrade pip setuptools
python3 -m pip install -r $GOPATH/src/rlf/requirements.txt

go build -o execution.so -buildmode=c-shared $GOPATH/src/rlf/export/execution.go

deactivate